from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
from typing import List, Dict
import json
from schemas import *
from dotenv import load_dotenv
import os
from google import genai
from google.genai.types import UserContent, ModelContent

load_dotenv(r'D:\IT\AI\teaching\GenAI_course\Day_2\Chat_bot\backend\.env') # Always use the environment variables first.

client = genai.Client()
from db import db
# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to the PostgreSQL database
    await db.connect()
    yield
    # Shutdown: Disconnect cleanly
    await db.disconnect()

app = FastAPI(lifespan=lifespan)


# --- API Endpoints ---
@app.post("/login", response_model=LoginResponse)
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

    # 2. Extract Chat Data from session_table
    session_records = await db.get_user_sessions(user_record['user_id'])
    chats = []
    count = 1
    for record in session_records:
        session_id_str = str(record['session_id'])
        chat_name = f'Chat {count}'
        count += 1
        chats.append({
            "chatName": chat_name,
            "sessionId": session_id_str
        })

    # 3. Return formatted response (matches the Streamlit frontend expectations)
    return LoginResponse(
        userID=user_id,
        chats=chats
    )

# --- GET Route (Fetch History) ---
@app.get("/chat/{session_id}", response_model=List[Dict[str, str]])
async def get_chat_history(session_id: str, user_id: str):
    # Reuse get_session here
    session_record = await db.get_session(session_id, user_id)
    
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")
        
    history = session_record['chat_history']
    if isinstance(history, str):
        history = json.loads(history)
        
    return history

# --- POST Route (Send Message) ---
@app.post("/chat")
async def send_chat_message(request: MessageRequest):
    # 1. Fetch from Database
    session_record = await db.get_session(request.session_id, request.user_id)
    
    if session_record:
        is_new_chat = False
        chat_history_list = session_record['chat_history']
        if isinstance(chat_history_list, str):
            chat_history_list = json.loads(chat_history_list)
    else:
        is_new_chat = True
        chat_history_list = []

    # 2. Add the NEW prompt to your raw dictionary list immediately
    chat_history_list.append({"role": "user", "text": request.prompt})

    # 3. Convert the ENTIRE list (including the new prompt) to Gemini format
    gemini_contents = []
    for msg in chat_history_list:
        if msg.get("role") == "user":
            gemini_contents.append(UserContent(msg["text"]))
        elif msg.get("role") == "model":
            gemini_contents.append(ModelContent(msg["text"]))
            
    # 4. Make a single Stateless call (No 'chats.create' object needed)
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=gemini_contents
        )
        ai_response_text = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")

    # 5. Append the AI's response to your local list
    chat_history_list.append({"role": "model", "text": ai_response_text})
    
    # 6. Save back to Database
    if is_new_chat:
        await db.insert_session(request.session_id, request.user_id, chat_history_list)
    else:
        await db.update_session_history(request.session_id, chat_history_list)

    return {
        "sessionId": request.session_id,
        "response": ai_response_text
    }