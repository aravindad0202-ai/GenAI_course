from pydantic import BaseModel


class LoginRequest(BaseModel):
    email_id: str
    password: str


class ChatRequest(BaseModel):
    userPrompt: str
    userId: str | None = None
    role: str | None = None
    department: str | None = None