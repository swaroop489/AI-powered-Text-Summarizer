# AI-powered-Text-Summarizer

## Project Overview  [FastAPI Backend & ReactJS Frontend]

### Problem Statement

- **Input:** Large text files (e.g., articles, research papers) provided in the `/input` folder. Example: 1 research paper + `sample.txt`.  
- **Output:** Concise summaries (3–5 sentences).  

> **Note:**  
> - Copy all input files into local storage before running the project.  
> - Clear the contents of `/input` and `/output` folders for demonstration purposes.  
> - After execution, output files will be saved in the `/output` folder in the backend.

- **Pretrained Model:** `facebook/bart-large-cnn` (1.6GB).  
- **User Interaction:** Through the **frontend interface** or directly via **API endpoints** using Swagger UI, Postman, or other API clients.  
- **Evaluation Metric:** ROUGE scores.

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


### 2.6 Using Backend Only

- Open Swagger UI at `http://127.0.0.1:8000/docs`.

- **Single File Demonstration:**
   1. Go to **/api/files/extract** → Click **Try it out** → Upload `sample.txt` → Click **Execute**.  
   2. To get the summary, go to **/api/summaries** → Enter the file name `sample.txt` → Click **Execute** → JSON output will be displayed.

- **Multiple Files:**
   1. Go to **/api/files/summarize** → Click **Try it out** → Upload multiple files.  
   2. Set the **Merge** option to `true` or `false` depending on whether you want a merged summary.  
   3. Click **Execute** → Summaries and ROUGE scores will be returned.

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

1. **Root Route**: `/` – Health check.

2. **Single File/Text Extraction**: `/api/files/extract` – Upload a single file or provide text.  
   - Specifically designed for **single file or text input**.  
   - Can be accessed directly via **Swagger UI** or **Postman**.

3. **Multiple File Summarization**: `/api/files/summarize` – Upload multiple files and optionally merge summaries.  
   - Returns summaries and **ROUGE scores** for each file or the merged document.

4. **Summarize by Text or Existing File**: `/api/summaries` – Summarize text or previously uploaded files.  
   - Provides both **abstractive** and **extractive summaries** along with **ROUGE scores**.

> All routes can be used independently of the frontend.


---

## Explanation of Separate Routes

In this project, I created **separate FastAPI routes** for file/text extraction and summarization to keep the API **modular, maintainable, and flexible**. Here’s the reasoning:

### `/api/files/extract` – File/Text Extraction
- Handles **raw text input** or **single file upload** (PDF/TXT).  
- Responsible for **extracting textual content** from files or using provided text.  
- Returns a **standardized JSON structure** (`files: [{name, text}]`) so other endpoints can consume it easily.  
- Separating extraction allows **pre-processing files independently** without triggering summarization.

### `/api/files/summarize` – Multiple Files Summarization
- Handles **batch uploads** of multiple files.  
- Optionally **merges all files** into a single summary.  
- Calls the **summarization logic after extraction**.  
- Keeping this separate makes it easier to **reuse the extraction logic** for multiple files and handle merging.

### `/api/summaries` – Single Text or File Summarization
- Summarizes **already extracted text** or a single uploaded file.  
- Allows users to **directly summarize text without uploading files**, supporting both file-based and text-based workflows.  
- Provides **abstractive and extractive summaries** along with **ROUGE scores**.

### Benefits of This Separation
- **Modularity:** Each route has a single responsibility (extract vs summarize).  
- **Reusability:** Extraction logic can be used independently by other endpoints or clients.  
- **Scalability:** Easier to extend (e.g., add new summarization models or handle more file types).  
- **Swagger clarity:** Each endpoint has a clear purpose and schema, making the API easier to document and consume.


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




