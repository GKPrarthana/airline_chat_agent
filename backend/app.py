from fastapi import FastAPI, Request
from pydantic import BaseModel
from backend.services.openai_service import ask_agent

app = FastAPI()

class Message(BaseModel):
    user_input: str

@app.post("/chat")
def chat(msg: Message):
    response_message, _ = ask_agent(msg.user_input) # ask_agent returns (message, history)
    return {"response": response_message}
