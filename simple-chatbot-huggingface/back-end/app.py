import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from the .env file
load_dotenv()

# --- 1. Initialize FastAPI and Hugging Face Client ---
app = FastAPI()
hf_token = os.getenv("HUGGINGFACE_API_KEY")
client = InferenceClient(api_key=hf_token)

# --- 2. Configure CORS ---
origins = [
    "http://localhost:5173",
    "http://localhost:5174",  # Default Vite React dev server
    "http://localhost:3000",  # Common Create React App dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Define the Request Data Structure ---
class ChatInput(BaseModel):
    user_message: str

# --- 4. Create API Endpoints ---
@app.get("/")
async def health_check():
    """A simple endpoint to confirm the server is running."""
    return {"status": "ok"}
from transformers import pipeline

# Load once at startup
# llm = pipeline("text-generation", model="gpt2")
@app.post("/chat")
async def chat_with_ai(input_data: ChatInput):
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": input_data.user_message}],
        )
        bot_response = response.choices[0].message.content
        return {"bot_response": bot_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# @app.post("/chat")
# async def chat_with_ai(input_data: ChatInput):
#     try:
#         response = llm(input_data.user_message, max_length=100)
#         bot_response = response[0]["generated_text"]
#         return {"bot_response": bot_response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))