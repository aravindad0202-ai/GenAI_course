from pydantic import BaseModel

class LoginRequest(BaseModel):
    email_id: str
    password: str

class UploadDataRequest(BaseModel):
    userId: str
    role: str
    department: str
    files: dict


class DeleteFileRequest(BaseModel):
    fileName: str

