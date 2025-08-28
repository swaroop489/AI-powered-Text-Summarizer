import { useState } from "react";

function MultiFileSummarizer() {
  const [files, setFiles] = useState([]);
  const [mergeFiles, setMergeFiles] = useState(false);
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleMultiUpload = (e) => {
    const uploadedFiles = Array.from(e.target.files).slice(0, 5); 
    setFiles(uploadedFiles);
    setError("");
    setSummaries([]);
  };

  const handleSummarize = async () => {
    if (!files.length) {
      setError("Please upload files first.");
      return;
    }

    setLoading(true);
    setError("");
    setSummaries([]);

    try {
      const formData = new FormData();
      files.forEach(f => formData.append("files", f));
      formData.append("merge", mergeFiles); 

      const res = await fetch("http://127.0.0.1:8000/api/files/summarize", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Failed to summarize files");

      const data = await res.json();
      setSummaries(data.results); 

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
        <div className="bg-white p-4 rounded shadow-lg flex-shrink-0 space-y-4">
          <h2 className="font-bold">Upload Files</h2>
          <input
            type="file"
            accept=".txt,.pdf"
            multiple
            onChange={handleMultiUpload}
            className="w-full"
            disabled={loading}
          />

          {files.length > 1 && (
            <label className="flex items-center gap-2 mt-2">
              <input
                type="checkbox"
                checked={mergeFiles}
                onChange={() => setMergeFiles(!mergeFiles)}
                className="rounded-full"
                disabled={loading || files.length < 1  }
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
          {files.map((f, idx) => (
            <div key={idx} className="bg-white p-4 rounded shadow-lg">
              <h3 className="font-bold">{f.name}</h3>
            </div>
          ))}
        </div>
      </div>

      {summaries.length > 0 && (
        <div className="mt-6 space-y-4">
          {summaries.map((s, idx) => (
            <div key={idx} className="bg-white p-4 rounded shadow-lg">
              <h3 className="font-bold text-lg mb-2">{s.name}</h3>

              <h4 className="font-semibold mb-1">Abstractive Summary:</h4>
              <div className="space-y-2">
                {s.abstractive
                  ? s.abstractive.split(/(?<=[.!?])\s+/).map((line, i) => (
                      <p key={i} className="leading-relaxed">{line}</p>
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

              { s.scores && (
  <div className="mt-3">
    <h4 className="font-semibold">ROUGE Scores</h4>
    <ul className="list-disc list-inside">
      <li>Abstractive - ROUGE-1: {s.scores.abstractive.rouge1}</li>
      <li>Abstractive - ROUGE-2: {s.scores.abstractive.rouge2}</li>
      <li>Abstractive - ROUGE-L: {s.scores.abstractive.rougeL}</li>
      <li>Extractive - ROUGE-1: {s.scores.extractive.rouge1}</li>
      <li>Extractive - ROUGE-2: {s.scores.extractive.rouge2}</li>
      <li>Extractive - ROUGE-L: {s.scores.extractive.rougeL}</li>
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
