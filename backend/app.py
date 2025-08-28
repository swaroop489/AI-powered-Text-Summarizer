from fastapi import FastAPI, UploadFile, File, Form, HTTPException
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
from typing import Optional,List


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
    text: Optional[str] = None 

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

def save_summary_file(name_prefix, abs_summary, ext_summary, scores=None):
    if not os.path.exists("output"):
        os.makedirs("output")
    
    filename = f"{name_prefix}_summary.txt"
    path = os.path.join("output", filename)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write("Abstractive Summary:\n")
        f.write(abs_summary + "\n\n")
        f.write("Extractive Summary:\n")
        f.write(ext_summary + "\n\n")
        
        if scores:
            f.write("ROUGE Scores:\n")
            f.write("Abstractive:\n")
            f.write(f"- ROUGE-1: {scores['abstractive']['rouge1']}\n")
            f.write(f"- ROUGE-2: {scores['abstractive']['rouge2']}\n")
            f.write(f"- ROUGE-L: {scores['abstractive']['rougeL']}\n\n")
            
            f.write("Extractive:\n")
            f.write(f"- ROUGE-1: {scores['extractive']['rouge1']}\n")
            f.write(f"- ROUGE-2: {scores['extractive']['rouge2']}\n")
            f.write(f"- ROUGE-L: {scores['extractive']['rougeL']}\n")
    
    return path


def summarize_text(text):
    # Abstractive summary (limit to 5 sentences)
    abs_summary1 = abstractive_summarizer.summarize_text(text)
    abs_sentences = re.split(r'(?<=[.!?])\s+', abs_summary1.strip())
    abs_summary = "\n".join([f"- {s}" for s in abs_sentences[:5]])

    # Extractive summary (5 sentences)
    parser = PlaintextParser.from_string(text, SumyTokenizer("english"))
    ext_summary_sentences = extractive_summarizer(parser.document, 5)
    ext_summary = "\n".join([f"- {str(s)}" for s in ext_summary_sentences])

    # ROUGE scores against original text
    try:
        abs_scores = rouge_evaluator.get_scores(abs_summary, text)[0]
        ext_scores = rouge_evaluator.get_scores(ext_summary, text)[0]
        scores_clean = {
            "abstractive": {
                "rouge1": round(abs_scores["rouge-1"]["f"], 3),
                "rouge2": round(abs_scores["rouge-2"]["f"], 3),
                "rougeL": round(abs_scores["rouge-l"]["f"], 3),
            },
            "extractive": {
                "rouge1": round(ext_scores["rouge-1"]["f"], 3),
                "rouge2": round(ext_scores["rouge-2"]["f"], 3),
                "rougeL": round(ext_scores["rouge-l"]["f"], 3),
            }
        }
    except:
        scores_clean = None

    return abs_summary, ext_summary, scores_clean




# ------------------- Routes -------------------



@app.get("/")
def root():
    return {"message": "FastAPI backend is running"}



# ------------------- Upload Files/Text And Extract Text -------------------

@app.post(
    "/api/files/extract",
    summary="Upload File Or Text",
    description="This endpoint allows uploading a single PDF/TXT file or providing raw text for extraction."
)
async def upload_file_or_text(
    file: Optional[UploadFile] = File(None, description="Upload a single file (PDF/TXT)"),
    text: Optional[str] = Form(None, description="Provide raw text instead of file")
):
    # Case 1: If text is provided
    if text:
        return {"files": [{"name": "text_input", "text": text}]}

    # Case 2: If a file is provided
    if file:
        input_dir = "input"
        os.makedirs(input_dir, exist_ok=True)

        file_path = os.path.join(input_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        if file.content_type == "application/pdf":
            extracted_text = extract_text_from_pdf(file_path)
        elif file.content_type == "text/plain":
            extracted_text = extract_text_from_txt(file_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")

        return {"files": [{"name": file.filename, "text": extracted_text}]}

    raise HTTPException(status_code=400, detail="No file or text provided")




# ------------------- Upload Multiple Files and Summarize (merge option) -------------------


@app.post("/api/files/summarize")
async def upload_and_summarize_files(
    files: list[UploadFile] = File(...),
    merge: bool = Form(False)
):  
    if not os.path.exists("input"):
        os.makedirs("input")
    file_texts = []
    for file in files:
        input_path = os.path.join("input", sanitize_filename(file.filename))
        with open(input_path, "wb") as f:
            f.write(await file.read())

        if file.content_type == "application/pdf":
            text = extract_text_from_pdf(input_path)
        elif file.content_type == "text/plain":
            text = extract_text_from_txt(input_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")

        file_texts.append({"name": file.filename, "text": text})

    summaries = []

    if merge:
        merged_text = "\n".join([f["text"] for f in file_texts])
        abs_summary, ext_summary, scores = summarize_text(merged_text)
        save_summary_file("merge_summary", abs_summary, ext_summary, scores)
        summaries.append({
            "name": "Merged Files",
            "abstractive": abs_summary,
            "extractive": ext_summary,
            "scores": scores
        })
    else:
        for f in file_texts:
            abs_summary, ext_summary, scores = summarize_text(f["text"])
            file_name_prefix = sanitize_filename(f["name"].rsplit(".", 1)[0])
            save_summary_file(file_name_prefix, abs_summary, ext_summary, scores)
            summaries.append({
                "name": f["name"],
                "abstractive": abs_summary,
                "extractive": ext_summary,
                "scores": scores
            })

    return {"results": summaries}



# -------------------   Summarization  -------------------
@app.post("/api/summaries")
def summarize_with_type(req: TextRequest, file_name: str = None):
    if file_name:
        file_path = os.path.join("input", sanitize_filename(file_name))
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File {file_name} not found in input/")
        

        if file_path.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif file_path.endswith(".txt"):
            text = extract_text_from_txt(file_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_name}")
    elif req.text:  
        text = req.text
    else:
        raise HTTPException(status_code=400, detail="Either text or file_name is required")
    

    abs_summary, ext_summary, scores = summarize_text(text)
    base_name = sanitize_filename(file_name.rsplit(".", 1)[0]) if file_name else "text_input"
    save_summary_file(base_name, abs_summary, ext_summary, scores)
    return {
        "abstractive": abs_summary,
        "extractive": ext_summary,
        "scores": scores
    }

