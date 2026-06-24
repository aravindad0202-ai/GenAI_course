from pydantic import BaseModel
from typing import List

class LoginRequest(BaseModel):
    email_id: str
    password: str

class ChatSession(BaseModel):
    chatName: str
    sessionId: str

class LoginResponse(BaseModel):
    userID: str
    chats: List[ChatSession]

class MessageRequest(BaseModel):
    session_id: str  
    user_id: str     
    prompt: str