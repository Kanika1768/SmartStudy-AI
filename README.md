# SmartStudy AI 

I built this because re-reading notes never worked for me. Upload any PDF 
and SmartStudy AI turns it into an active study session.

🔗 **Live app:** https://smartstudy-ai-vly8fyfdxdhuv83znhptbz.streamlit.app


## What it does

- **Quiz Me** — generates MCQ + short answer questions from your notes
- **Ask a Question** — answers from YOUR document only, not general knowledge
- **Weak Spots** — tracks which sections you keep getting wrong


## Tech stack

Python · Streamlit · Google Gemini API · ChromaDB · RAG · PyPDF2

**The interesting part:** questions are answered using RAG — your PDF chunks 
get embedded into ChromaDB, your question gets matched to the closest chunk, 
and the LLM answers using only that context. If the answer isn't there, it 
says so instead of guessing.


## Run locally

```bash
git clone https://github.com/YOUR_USERNAME/smartstudy-ai
cd smartstudy-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# add GEMINI_API_KEY=your_key to .env
streamlit run app.py
```


## Limitations
- Typed PDFs only — scanned/handwritten not supported yet
- Free-tier Gemini quota means large PDFs process slowly

Built by Kanika Gadiya