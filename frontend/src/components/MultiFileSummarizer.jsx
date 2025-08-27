import { useState } from "react";

function MultiFileSummarizer() {
  const [files, setFiles] = useState([]);
  const [fileTexts, setFileTexts] = useState([]);
  const [mergeFiles, setMergeFiles] = useState(false);
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Handle multiple file upload
  const handleMultiUpload = async (e) => {
    const uploadedFiles = Array.from(e.target.files).slice(0, 5); // max 5 files
    setFiles(uploadedFiles);
    setError("");
    setFileTexts([]);
    setSummaries([]);

    const texts = [];
    for (const file of uploadedFiles) {
      if (!["text/plain", "application/pdf"].includes(file.type)) {
        setError("Only .txt and .pdf files are supported");
        return;
      }

      const formData = new FormData();
      formData.append("files", file);

      try {
        const res = await fetch("http://127.0.0.1:8000/upload_files", {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        if (data.files && data.files.length > 0) {
          texts.push({ name: file.name, text: data.files[0].text });
        }
      } catch (err) {
        setError("Failed to extract some files");
      }
    }
    setFileTexts(texts);
  };

  // Summarize files
  const handleSummarize = async () => {
    if (!fileTexts.length) {
      setError("Please upload files first.");
      return;
    }

    setLoading(true);
    setError("");
    setSummaries([]);

    try {
      let response;
      if (mergeFiles) {
        // Combine all files into one summary
        const mergedText = fileTexts.map(f => f.text).join("\n");
        response = await fetch("http://127.0.0.1:8000/summarize_with_type", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: mergedText }),
        });
        const data = await response.json();
        setSummaries([{ name: "Merged Files", ...data }]);
      } else {
        // Individual summaries
        response = await fetch("http://127.0.0.1:8000/summarize_batch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ texts: fileTexts.map(f => f.text) }),
        });
        const data = await response.json();
        // Correctly map backend results
        const mapped = data.results.map((s, i) => ({
          name: fileTexts[i].name,
          ...s
        }));
        setSummaries(mapped);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to summarize files.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-4">
      <h1 className="text-3xl font-bold text-center mb-6">AI Multi-File Summarizer</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="bg-white p-4 rounded shadow-lg flex-shrink-0  space-y-4">
          <h2 className="font-bold">Upload Files</h2>
          <input
            type="file"
            accept=".txt,.pdf"
            multiple
            onChange={handleMultiUpload}
            className="w-full"
            disabled={files.length > 0} // disable after upload
          />

          {/* Show Combine toggle only if more than 1 file */}
          {files.length > 1 && (
            <label className="flex items-center gap-2 mt-2">
              <input
                type="checkbox"
                checked={mergeFiles}
                onChange={() => setMergeFiles(!mergeFiles)}
                className="rounded-full"
                disabled={files.length < 2} // disable after upload
              />
              <span className="text-sm">Combine Summary</span>
            </label>
          )}

          <button
            onClick={handleSummarize}
            disabled={loading || !files.length}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded mt-2 w-full"
          >
            {loading ? "Summarizing..." : "Summarize"}
          </button>
          {error && <p className="text-red-500">{error}</p>}
        </div>

        {/* Right Column: File Names */}
        <div className="space-y-4">
          {fileTexts.map((f, idx) => (
            <div key={idx} className="bg-white p-4 rounded shadow-lg">
              <h3 className="font-bold">{f.name}</h3>
            </div>
          ))}
        </div>
      </div>

      {/* Summaries: full width below both columns */}
      {summaries.length > 0 && (
        <div className="mt-6 space-y-4">
          {summaries.map((s, idx) => (
            <div key={idx} className="bg-white p-4 rounded shadow-lg">
              <h3 className="font-bold text-lg mb-2">{s.name}</h3>

              <h4 className="font-semibold mb-1">Abstractive Summary:</h4>
              <div className="space-y-2">
                {s.abstractive
                  ? s.abstractive.split(/(?<=[.!?])\s+/).map((line, i) => (
                      <p key={i} className="leading-relaxed">- {line}</p>
                    ))
                  : "Summary will appear here..."}
              </div>

              <h4 className="font-semibold mb-1 mt-3">Extractive Summary:</h4>
              <div className="space-y-2">
                {s.extractive
                  ? s.extractive.split(/(?<=[.!?])\s+/).map((line, i) => (
                      <p key={i} className="leading-relaxed">{line}</p>
                    ))
                  : "Summary will appear here..."}
              </div>

              {s.scores && (
                <div className="mt-3">
                  <h4 className="font-semibold">ROUGE Scores</h4>
                  <ul className="list-disc list-inside">
                    <li>ROUGE-1: {s.scores.rouge1}</li>
                    <li>ROUGE-2: {s.scores.rouge2}</li>
                    <li>ROUGE-L: {s.scores.rougeL}</li>
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MultiFileSummarizer;
