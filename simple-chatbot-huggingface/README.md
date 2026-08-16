## Simple Chatbot with Hugging Face

**Problem:** Learn how a frontend and backend talk to each other by building a minimal AI chatbot.
**Stack:** FastAPI + Hugging Face Inference API (backend), React + TypeScript + Vite (frontend).

### Run it

Backend:
```bash
cd back-end
pip install -r requirements.txt
cp .env.example .env   # add your Hugging Face token
python main.py
```

Frontend:
```bash
cd frontend/chatbot-frontend
npm install
npm run dev
```
