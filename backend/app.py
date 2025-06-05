from fastapi import FastAPI, Request
from pydantic import BaseModel
from backend.services.openai_service import ask_openai

app = FastAPI()

class Message(BaseModel):
    user_input: str

@app.post("/chat")
def chat(msg: Message):
    response = ask_openai(msg.user_input)
    return {"response": response}
