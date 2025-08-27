from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
from summarizers import AbstractiveSummarizer, ExtractiveSummarizer, rouge_evaluator, extract_text_from_pdf, extract_text_from_txt

router = APIRouter()

class FilesRequest(BaseModel):
    texts: list[str]

@router.post("/upload_files")
async def upload_files(files: list[UploadFile] = File(...)):
    result = []
    for file in files:
        ext_text = ""
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

@router.post("/summarize_batch")
def summarize_batch(req: FilesRequest):
    results = []
    for text in req.texts:
        abs_summary = AbstractiveSummarizer().summarize_text(text)
        ext_summary = ExtractiveSummarizer().summarize(text)
        try:
            scores = rouge_evaluator.get_scores(abs_summary, ext_summary)[0]
            scores_clean = {
                "rouge1": round(scores["rouge-1"]["f"], 3),
                "rouge2": round(scores["rouge-2"]["f"], 3),
                "rougeL": round(scores["rouge-l"]["f"], 3),
            }
        except:
            scores_clean = None
        results.append({
            "abstractive": abs_summary,
            "extractive": ext_summary,
            "scores": scores_clean
        })
    return {"results": results}
