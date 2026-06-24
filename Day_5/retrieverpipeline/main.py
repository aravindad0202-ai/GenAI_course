from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
load_dotenv(r'D:\IT\AI\teaching\GenAI_course\Day_5\.env')
from src.VDb import vdb
from src.db import db
from src.rag_service import ragsvc
from src.schemas import ChatRequest, LoginRequest




@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    await vdb.connect()
    yield
    await vdb.disconnect()
    await db.disconnect()


app = FastAPI(lifespan=lifespan)


@app.post('/login')
async def login(request: LoginRequest):
    user_record = await db.get_user_by_email(request.email_id)

    if not user_record or user_record['password'] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid user',
        )

    user_id = str(user_record['user_id'])
    return {
        'userID': user_id,
        'role': user_record['role'],
        'department': user_record['department'],
    }


@app.post('/rag-chat/')
async def rag_chat(request: ChatRequest):
    user_profile = {
        'userId': request.userId,
        'role': request.role,
        'department': request.department,
    }

    if request.userId:
        user_record = await db.get_user_by_id(request.userId)
        if user_record:
            user_profile = {
                'userId': str(user_record['user_id']),
                'role': user_record['role'],
                'department': user_record['department'],
            }

    department = user_profile.get('department')
    documents = await vdb.retrieve_documents(request.userPrompt, department=department, top_k=10)
    result = await ragsvc.generate_answer(request.userPrompt, user_profile, documents)

    return {
        'message': 'Response generated successfully',
        'answer': result['answer'],
        'sources': result['sources'],
        'context': result['context'],
        'userId': user_profile.get('userId'),
    }