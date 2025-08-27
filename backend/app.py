from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer as SumyTokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from rouge import Rouge
import pdfplumber
import os
import re

from summarizer import Summarizer

# ------------------- FastAPI setup -------------------
app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Models -------------------
class TextRequest(BaseModel):
    text: str

class BatchRequest(BaseModel):
    texts: list

# ------------------- Initialize summarizers -------------------
abstractive_summarizer = Summarizer()
extractive_summarizer = LexRankSummarizer()
rouge_evaluator = Rouge()

# ------------------- Helpers -------------------
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def sanitize_filename(name):
    return re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name)

def save_summary_file(name_prefix, abs_summary, ext_summary, scores):
    if not os.path.exists("output"):
        os.makedirs("output")
    score_part = ""
    if scores:
        score_part = f"_R1-{scores['rouge1']}_R2-{scores['rouge2']}_RL-{scores['rougeL']}"
    filename = f"{name_prefix}{score_part}_summary.txt"
    path = os.path.join("output", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("Abstractive Summary:\n")
        f.write(abs_summary + "\n\n")
        f.write("Extractive Summary:\n")
        f.write(ext_summary + "\n\n")
        if scores:
            f.write(f"ROUGE Scores: {scores}\n")
    return path

# ------------------- Routes -------------------
@app.get("/")
def root():
    return {"message": "FastAPI backend is running"}

# ------------------- File Upload -------------------
@app.post("/upload_files")
async def upload_files(files: list[UploadFile] = File(...)):
    result = []
    for file in files:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        if file.content_type == "application/pdf":
            ext_text = extract_text_from_pdf(temp_path)
        elif file.content_type == "text/plain":
            ext_text = extract_text_from_txt(temp_path)
        else:
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
        
        os.remove(temp_path)
        result.append({"name": file.filename, "text": ext_text})
    return {"files": result}

# ------------------- Single Text Summarization -------------------
@app.post("/summarize_with_type")
def summarize_with_type(req: TextRequest):
    abs_summary1 = abstractive_summarizer.summarize_text(req.text)
    abs_sentences = re.split(r'(?<=[.!?])\s+', abs_summary1.strip())
    abs_summary = "\n".join([f"- {s}" for s in abs_sentences])
    parser = PlaintextParser.from_string(req.text, SumyTokenizer("english"))
    ext_summary_sentences = extractive_summarizer(parser.document, 5)
    ext_summary = "\n".join([f"- {str(s)}" for s in ext_summary_sentences])
    
    try:
        scores = rouge_evaluator.get_scores(abs_summary, ext_summary)[0]
        scores_clean = {
            "rouge1": round(scores["rouge-1"]["f"], 3),
            "rouge2": round(scores["rouge-2"]["f"], 3),
            "rougeL": round(scores["rouge-l"]["f"], 3),
        }
    except:
        scores_clean = None

    # Save combined summary to output folder
    save_summary_file("multisummary", abs_summary, ext_summary, scores_clean)

    return {
        "abstractive": abs_summary,
        "extractive": ext_summary,
        "scores": scores_clean
    }

# ------------------- Batch Summarization -------------------
@app.post("/summarize_batch")
def summarize_batch(request: BatchRequest):
    summaries = abstractive_summarizer.summarize_batch(request.texts)
    results = []

    for i, (text, abs_summary) in enumerate(zip(request.texts, summaries)):
        parser = PlaintextParser.from_string(text, SumyTokenizer("english"))
        ext_summary_sentences = extractive_summarizer(parser.document, 5)
        ext_summary = "\n".join([f"- {str(s)}" for s in ext_summary_sentences])

        try:
            scores = rouge_evaluator.get_scores(abs_summary, ext_summary)[0]
            scores_clean = {
                "rouge1": round(scores["rouge-1"]["f"], 3),
                "rouge2": round(scores["rouge-2"]["f"], 3),
                "rougeL": round(scores["rouge-l"]["f"], 3),
            }
        except:
            scores_clean = None

        # Save individual summary to output folder
        file_name_prefix = sanitize_filename(f"File{i+1}")
        save_summary_file(file_name_prefix, abs_summary, ext_summary, scores_clean)

        results.append({
            "abstractive": abs_summary,
            "extractive": ext_summary,
            "scores": scores_clean
        })

    return {"results": results}
