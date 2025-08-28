import { useState } from "react";

function SingleFileSummarizer() {
  const [text, setText] = useState("");
  const [uploadedFileName, setUploadedFileName] = useState(null);
  const [abstractive, setAbstractive] = useState("");
  const [extractive, setExtractive] = useState("");
  const [scores, setScores] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Handle file upload (txt + pdf)
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!["text/plain", "application/pdf"].includes(file.type)) {
      setError("Only .txt and .pdf files are supported");
      return;
    }

    setError("");
    const formData = new FormData();
    formData.append("file", file); 

    try {
      const response = await fetch("http://127.0.0.1:8000/api/files/extract", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("File extraction failed");

      const data = await response.json();
      if (data.files && data.files.length > 0) {
        setText(data.files[0].text);
        setUploadedFileName(data.files[0].name);
      }
    } catch (err) {
      setError("Failed to extract file text");
    }
  };

  // Summarize text (works for both file-uploaded text or pasted text)
  const handleSummarize = async () => {
    if (!text.trim()) {
      setError("Please enter text or upload a file.");
      return;
    }

    setLoading(true);
    setError("");
    setAbstractive("");
    setExtractive("");
    setScores(null);

    try {
      const fileNameParam = uploadedFileName ? uploadedFileName : null;
      const response = await fetch(
        "http://127.0.0.1:8000/api/summaries" + 
        (fileNameParam ? `?file_name=${fileNameParam}` : ""),
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, file_name: fileNameParam }),
        }
      );

      if (!response.ok) throw new Error("Failed to summarize text");

      const data = await response.json();
      setAbstractive(data.abstractive || "");
      setExtractive(data.extractive || "");
      setScores(data.scores || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-1">
      <h1 className="text-3xl font-bold text-center mt-2 mb-8">
        AI Single File Text Summarizer
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column: Input */}
        <div className="bg-white p-4 rounded shadow-lg self-start">
          <h2 className="font-semibold mb-2">Input Text / Upload File</h2>

          <textarea
            rows={16}
            className="w-full border border-gray-300 p-3 rounded mb-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Paste your text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={loading}
          />

          <input type="file" accept=".txt,.pdf" onChange={handleFileUpload} disabled={loading} className="mt-2" />

          <button
            onClick={handleSummarize}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded mt-4 w-full"
            disabled={loading}
          >
            {loading ? "Summarizing..." : "Summarize"}
          </button>

          {error && <p className="text-red-500 mt-2">{error}</p>}
        </div>

        {/* Right Column: Output */}
        <div className="space-y-4">
          <div className="bg-white p-4 rounded shadow-lg">
            <h2 className="font-semibold mb-2">Abstractive Summary</h2>
            <div className="space-y-2">
              {abstractive
                ? abstractive.split(/(?<=[.!?])\s+/).map((s, i) => (
                    <p className="leading-relaxed" key={i}>
                      {s}
                    </p>
                  ))
                : "Summary will appear here..."}
            </div>
          </div>

          <div className="bg-white p-4 rounded shadow-lg">
            <h2 className="font-semibold mb-2">Extractive Summary</h2>
            <div className="space-y-2">
              {extractive
                ? extractive.split(/(?<=[.!?])\s+/).map((s, i) => (
                    <p key={i} className="leading-relaxed">
                      {s}
                    </p>
                  ))
                : "Summary will appear here..."}
            </div>
          </div>

          {scores && (
            <div className="mt-3">
              <span className="font-semibold bg-blue-600 text-white p-2">ROUGE Scores</span>
              <ul className="list-disc list-inside mt-4">
                <div className="bg-white p-4 rounded shadow-lg">
                  <li>Abstractive - ROUGE-1: {scores.abstractive.rouge1}</li>
                  <li>Abstractive - ROUGE-2: {scores.abstractive.rouge2}</li>
                  <li>Abstractive - ROUGE-L: {scores.abstractive.rougeL}</li>
                </div>
                <div className="bg-white p-4 rounded shadow-lg mt-2">
                  <li>Extractive - ROUGE-1: {scores.extractive.rouge1}</li>
                  <li>Extractive - ROUGE-2: {scores.extractive.rouge2}</li>
                  <li>Extractive - ROUGE-L: {scores.extractive.rougeL}</li>
                </div>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SingleFileSummarizer;
