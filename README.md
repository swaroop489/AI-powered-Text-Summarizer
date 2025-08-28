# AI-powered-Text-Summarizer

## Project Overview  [FastAPI for backend and React JS For Frontend ] 


### Follows Problem Statement provided 

Input: Large text (e.g., article, research paper)  provided in input folder 1 research paper + sample.txt in /input folder 

#### Make Sure you copy all input files in local storage and delete contents of input and output folder for demonstration the code will produce input as well as output structure
#### demo output of executed code is found in /output folder in backend

Output: Concise summary (3-5 sentences)  

Pretrained model used : facebook/bart-large-cnn  (1.6GB)

Users can interact with the backend via a **frontend interface** or directly through **API endpoints** using Swagger UI, Postman, or other API clients.

Evaluation metrics Rouge scores

---
## 🚀 Features  
- Upload **PDF/TXT** files or paste raw text  
- Generate **abstractive summaries** (BART, T5)  
- Generate **extractive summaries** (TextRank, spaCy)  
- Compare summaries with **ROUGE scores**  
- Simple and interactive **React frontend**  
- **FastAPI backend** with Hugging Face transformers
- The system supports single and multiple files, as well as merged summaries.

## 1. System Requirements
- **Python 3.10+**  
- **Node.js 18+ / npm 9+**  
- **Memory:** Minimum 8GB RAM recommended  
- **Optional GPU:** For faster abstractive summarization using transformer models  

---

## 2. Backend Setup (FastAPI)

### 2.1 Clone Repository
```bash
git clone https://github.com/swaroop489/AI-powered-Text-Summarizer.git
cd AI-powered-Text-Summarizer
```

### 2.2 Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### 2.3 Activate Virtual Environment
- **Windows:**
```bash
venv\Scripts\activate
```
- **Linux/macOS:**
```bash
source venv/bin/activate
```

### 2.4 Install Dependencies
```bash
pip install -r requirements.txt
```
**Key Dependencies:**
- `fastapi` – backend framework  
- `uvicorn` – ASGI server  
- `transformers` & `torch` – for abstractive summarization  (619 mb)
- `sumy` – for extractive summarization  
- `pdfplumber` – PDF text extraction  
- `rouge` – summary evaluation  

### 2.5 Run Backend Server
```bash
uvicorn app:app --reload
```
- Backend runs at `http://127.0.0.1:8000/`  
- Access **Swagger UI** at `http://127.0.0.1:8000/docs` for API testing.


### 2.6 IF Using Backend Only 

- Go to `http://127.0.0.1:8000/docs`
- For single file demonstration summary
   - Path: **/api/files/extract** -> try out -> upload sample.txt and then click execute
   - for output go to Path: **/api/summaries** and enter file name sample.txt and execute and you will get json output
- For multi files
   - Path: **/api/files/summarize** add multiple files and check merge option true or false depending upon if you want merged summary or not then click execute

---

## 3. Frontend Setup (React + TailwindCSS)

### 3.1 Navigate to Frontend Folder
```bash
cd frontend
```

### 3.2 Install Dependencies
```bash
npm install
```

### 3.3 Run Frontend
```bash
npm run dev
```
- Frontend runs at `http://localhost:5173/`  
- Supports single-file and multi-file summarization.

---

## 4. Project Structure

### Backend
```
app.py             # FastAPI routes and main server
summarizer.py      # Abstractive summarization class
input/             # Folder to store uploaded files
output/            # Folder to save generated summaries
```

### Frontend
```
frontend/
  ├─ src/
      ├─components
          ├─ SingleFileSummarizer.jsx
          ├─ MultiFileSummarizer.jsx
      └─ App.jsx
```

---

## 5. API Routes

1. **Root Route**: `/` – Health check  
2. **Single File/Text Extraction**: `/api/files/extract` – Upload a single file or submit text  
   - Specifically for **single file/text input**  
   - Can be used directly via Swagger UI or Postman  
3. **Multiple File Summarization**: `/api/files/summarize` – Upload multiple files, optionally merge summaries  
   - Returns summaries and ROUGE scores for each file or the merged document  
4. **Summarize by Text or Existing File**: `/api/summaries` – Summarize text or previously uploaded files  
   - Returns both abstractive and extractive summaries with ROUGE scores  

> All routes can be used independently of the frontend.

---

## 6. Usage

### Single File/Text
1. Upload a single PDF/TXT file or paste text.  
2. Generate both abstractive and extractive summaries.  
3. View ROUGE scores for evaluation.  

### Multiple Files
1. Upload multiple PDF/TXT files.  
2. Optionally select “Merge Summary” to combine into a single summary.  
3. Retrieve summaries for each file or the merged document.

---

## 7. Optional: GPU Acceleration
For faster abstractive summarization:
- Install PyTorch with CUDA support: [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)  
- Update backend to move model and inputs to GPU.

---

## 8. Troubleshooting

- **File text not extracting from PDF** – Ensure `pdfplumber` is installed and PDF is not encrypted.  
- **Transformer model runs slowly** – Use GPU or reduce summary length.  
- **Port conflicts** – Change ports in `uvicorn` or React dev server.

---

## 9. Future Enhancements
- Support additional file types (DOCX, HTML)  
- Cloud storage integration for automatic file input/output  
- User-defined summary length and style


## 10. Screenshots

<img width="1920" height="1080" alt="Screenshot (1444)" src="https://github.com/user-attachments/assets/cdc4984c-ab0a-4987-87e5-75bbbb08bac0" />
<img width="1920" height="1080" alt="Screenshot (1445)" src="https://github.com/user-attachments/assets/338a1e2a-d2fc-448d-bef8-e3346258deee" />
<img width="1920" height="1080" alt="Screenshot (1438)" src="https://github.com/user-attachments/assets/ab99c3e9-472d-4aab-8a49-982f6ba67054" />
<img width="1920" height="1080" alt="Screenshot (1439)" src="https://github.com/user-attachments/assets/b7e9e047-845b-413e-851e-60a9ff2dc29a" />
<img width="1920" height="1080" alt="Screenshot (1443)" src="https://github.com/user-attachments/assets/19d7cbb8-c113-4139-99ba-b659c1316f4a" />
<img width="1920" height="1080" alt="Screenshot (1441)" src="https://github.com/user-attachments/assets/3c477c86-c903-424b-9119-9f2fd678c5a7" />




