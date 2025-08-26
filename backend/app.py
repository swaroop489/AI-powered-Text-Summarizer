from flask import Flask, request, jsonify
from summarizer import abstractive_summary, extractive_summary

app = Flask(__name__)

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    text = data.get("text", "")
    method = data.get("method", "abstractive")  # default abstractive

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    if method == "extractive":
        summary = extractive_summary(text)
    else:
        summary = abstractive_summary(text)

    return jsonify({"summary": summary})

@app.route("/summarize_batch", methods=["POST"])
def summarize_batch():
    data = request.json
    texts = data.get("texts", [])
    method = data.get("method", "abstractive")

    if not texts:
        return jsonify({"error": "No texts provided"}), 400

    summaries = []
    for text in texts:
        if method == "extractive":
            summaries.append(extractive_summary(text))
        else:
            summaries.append(abstractive_summary(text))

    return jsonify({"summaries": summaries})

if __name__ == "__main__":
    app.run(debug=True)
