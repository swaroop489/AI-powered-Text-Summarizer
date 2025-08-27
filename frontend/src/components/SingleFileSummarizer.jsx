import { useState } from "react";

function SingleFileSummarizer() {
  const [text, setText] = useState("");
  const [abstractive, setAbstractive] = useState("");
  const [extractive, setExtractive] = useState("");
  const [scores, setScores] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reference, setReference] = useState("");


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
    formData.append("files", file); // <-- new backend accepts 'files' array

    try {
      const response = await fetch("http://127.0.0.1:8000/upload_files", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.files && data.files.length > 0) {
        setText(data.files[0].text); // single file, take first
      }
    } catch (err) {
      setError("Failed to extract file text");
    }
  };

  // Summarize text
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
      const response = await fetch("http://127.0.0.1:8000/summarize_with_type", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
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
      <h1 className="text-3xl font-bold text-center mt-2 mb-8">AI Single File Text Summarizer</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column: Input */}
        <div className="bg-white p-4 rounded shadow-lg self-start">
          <h2 className="font-semibold mb-2">Input Text / Upload File</h2>
          <textarea
            rows={9}
            className="w-full border border-gray-300 p-3 rounded mb-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Paste your text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <input
            type="file"
            accept=".txt,.pdf"
            onChange={handleFileUpload}
            className="mt-2"
          />
          <textarea rows={5} className="w-full border border-gray-300 p-3 rounded mb-2 resize-none focus:outline-none focus:ring-2 focus:ring-green-400 shadow-lg mt-3" placeholder="Paste reference summary here (optional for ROUGE)" value={reference} onChange={(e) => setReference(e.target.value)} />
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
                    <p className="leading-relaxed" key={i}>- {s}</p>
                  ))
                : "Summary will appear here..."}
            </div>
          </div>

          <div className="bg-white p-4 rounded shadow-lg">
            <h2 className="font-semibold mb-2">Extractive Summary</h2>
            <div className="space-y-2">
              {extractive
                ? extractive.split(/(?<=[.!?])\s+/).map((s, i) => (
                    <p key={i} className="leading-relaxed">{s}</p>
                  ))
                : "Summary will appear here..."}
            </div>
          </div>

          {scores && (
            <div className="bg-white p-4 rounded shadow">
              <h2 className="font-semibold mb-2">ROUGE Scores</h2>
              <ul className="list-disc list-inside">
                <li>ROUGE-1 F1: {scores.rouge1}</li>
                <li>ROUGE-2 F1: {scores.rouge2}</li>
                <li>ROUGE-L F1: {scores.rougeL}</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SingleFileSummarizer;
