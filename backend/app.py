from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import BartForConditionalGeneration, BartTokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer as SumyTokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from rouge import Rouge
import pdfplumber
import os
import nltk

# ------------------- NLTK Setup -------------------
nltk.download("punkt")

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

class ReferenceRequest(BaseModel):
    text: str
    reference: str = None  # optional

# ------------------- Abstractive Summarizer -------------------
import re

class AbstractiveSummarizer:
    def __init__(self):
        self.model_name = "facebook/bart-large-cnn"
        self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
        self.model = BartForConditionalGeneration.from_pretrained(self.model_name)
        self.max_input_tokens = 1024

    def chunk_text(self, text):
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            token_len = len(self.tokenizer.encode(current_chunk + sentence, truncation=False))
            if token_len <= self.max_input_tokens:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def summarize_text(self, text, max_length=120, min_length=40):
        chunks = self.chunk_text(text)
        summaries = []
        for chunk in chunks:
            inputs = self.tokenizer([chunk], max_length=self.max_input_tokens, return_tensors='pt', truncation=True)
            summary_ids = self.model.generate(
                inputs['input_ids'],
                num_beams=4,
                max_length=max_length,
                min_length=min_length,
                early_stopping=True
            )
            summaries.append(self.tokenizer.decode(summary_ids[0], skip_special_tokens=True))

        full_summary = " ".join(summaries)

        # Force 3–5 sentences
        sentences = re.split(r'(?<=[.!?]) +', full_summary)
        sentences = sentences[:5] if len(sentences) > 5 else sentences

        # Format as bullets for readability
        formatted_summary = "\n".join([f"- {s.strip()}" for s in sentences if s.strip()])

        return formatted_summary


# ------------------- Extractive Summarizer -------------------
class ExtractiveSummarizer:
    def __init__(self, sentences_count=5):
        self.sentences_count = sentences_count
        self.summarizer = LexRankSummarizer()

    def summarize(self, text):
        parser = PlaintextParser.from_string(text, SumyTokenizer("english"))
        summary_sentences = self.summarizer(parser.document, self.sentences_count)
        summary_list = [str(sentence).strip() for sentence in summary_sentences]

        # Force 3–5 sentences
        if len(summary_list) > 5:
            summary_list = summary_list[:5]
        elif len(summary_list) < 3:
            summary_list = summary_list  # return whatever is available

        # Format as bullet points for readability
        formatted_summary = "\n".join([f"- {sentence}" for sentence in summary_list])

        return formatted_summary


# ------------------- Initialize Summarizers and ROUGE -------------------
abstractive_summarizer = AbstractiveSummarizer()
extractive_summarizer = ExtractiveSummarizer()
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

# ------------------- Routes -------------------
@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running"}

# PDF Upload
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_location)
    os.remove(file_location)
    return {"text": text}

# TXT Upload
@app.post("/upload_txt")
async def upload_txt(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Only TXT files are supported")
    
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_txt(file_location)
    os.remove(file_location)
    return {"text": text}

# Summarize with type
@app.post("/summarize_with_type")
def summarize_with_type(request: TextRequest):
    abs_summary = abstractive_summarizer.summarize_text(request.text)
    ext_summary = extractive_summarizer.summarize(request.text)
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

# Batch Summarize
@app.post("/summarize_batch")
def summarize_batch(request: BatchRequest):
    results = []
    for text in request.texts:
        abs_summary = abstractive_summarizer.summarize_text(text)
        ext_summary = extractive_summarizer.summarize(text)
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

# Summarize with reference
@app.post("/summarize_with_reference")
def summarize_with_reference(request: ReferenceRequest):
    abs_summary = abstractive_summarizer.summarize_text(request.text)
    ext_summary = extractive_summarizer.summarize(request.text)

    if request.reference:
        try:
            scores = rouge_evaluator.get_scores(abs_summary, request.reference)[0]
            scores_clean = {
                "rouge1": round(scores["rouge-1"]["f"], 3),
                "rouge2": round(scores["rouge-2"]["f"], 3),
                "rougeL": round(scores["rouge-l"]["f"], 3),
            }
        except:
            scores_clean = None
    else:
        scores_clean = None

    return {
        "abstractive": abs_summary,
        "extractive": ext_summary,
        "scores": scores_clean
    }
