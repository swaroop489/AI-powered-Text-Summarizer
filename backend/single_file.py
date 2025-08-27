from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import pdfplumber
import os
from summarizers import AbstractiveSummarizer, ExtractiveSummarizer, rouge_evaluator  # assume you move classes to summarizers.py

router = APIRouter()

class TextRequest(BaseModel):
    text: str

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

@router.post("/upload_txt")
async def upload_txt(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Only TXT files are supported")
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    text = extract_text_from_txt(file_location)
    os.remove(file_location)
    return {"text": text}

@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    text = extract_text_from_pdf(file_location)
    os.remove(file_location)
    return {"text": text}

@router.post("/summarize_single")
def summarize_single(req: TextRequest):
    abs_summary = AbstractiveSummarizer().summarize_text(req.text)
    ext_summary = ExtractiveSummarizer().summarize(req.text)
    try:
        scores = rouge_evaluator.get_scores(abs_summary, ext_summary)[0]
        scores_clean = {
            "rouge1": round(scores["rouge-1"]["f"], 3),
            "rouge2": round(scores["rouge-2"]["f"], 3),
            "rougeL": round(scores["rouge-l"]["f"], 3),
        }
    except:
        scores_clean = None
    return {
        "abstractive": abs_summary,
        "extractive": ext_summary,
        "scores": scores_clean
    }
