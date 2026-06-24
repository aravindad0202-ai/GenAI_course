import base64
import os
from fastapi import FastAPI, HTTPException, status
from dotenv import load_dotenv
load_dotenv(r'D:\IT\AI\teaching\GenAI_course\Day_5\.env')
print('initializing server')
from src.schemas import *
from contextlib import asynccontextmanager
from src.pipeline import ingest_data
print('initiailizing data')
from src.BlobDb import blobdb
from src.VDb import vdb
from src.db import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    await vdb.connect()
    await blobdb.connect()
    yield
    await blobdb.disconnect()
    await vdb.disconnect()
    await db.disconnect()

app = FastAPI(lifespan=lifespan)

@app.post('/login')
async def login(request: LoginRequest):
    # 1. Verify User exists
    user_record = await db.get_user_by_email(request.email_id)
    
    # Note: In a production environment, never compare plaintext passwords.
    # Use a library like passlib and bcrypt to verify hashed passwords.
    if not user_record or user_record['password'] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    
    user_id = str(user_record['user_id'])

    return {'userID':user_id,'role':user_record['role'], 'department': user_record['department']}

@app.post('/upload-data')
async def upload_data(request: UploadDataRequest):
    if not request.files or not isinstance(request.files, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded files payload is invalid."
        )
    department = request.department
    filename = request.files.get('filename', 'uploaded_file')
    content = request.files.get('content')
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file content provided."
        )

    try:
        file_bytes = base64.b64decode(content)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content decoding failed."
        )

    result = await ingest_data(filename, file_bytes, department)

    return {
        'message': result['message'],
        'userId': request.userId,
        'department': request.department
    }


@app.get('/delete-files')
async def delete_files():
    try:
        files = await blobdb.list_files()
        return {
            'message': 'Files fetched successfully',
            'files': files
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )


@app.delete('/delete-files')
async def delete_file(request: DeleteFileRequest):
    try:
        vector_result = await vdb.delete_documents_by_source(request.fileName)
        blob_result = await blobdb.delete_file(request.fileName)
        return {
            'message': 'File deleted successfully',
            'vector_result': vector_result,
            'blob_result': blob_result,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )