import asyncpg
import os
import json

DATABASE_URL = os.getenv("DATABASE_URL") #'postgresql://<username>:<password>@<host>:<port>/<database_name>'
# DATABASE_URL = 'postgresql://chat_bot_db:abcd12345@localhost:5432/chat_bot_db'
print('DB',DATABASE_URL)
class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Initialize the async connection pool."""
        self.pool = await asyncpg.create_pool(DATABASE_URL)
        
        # Optional: Initialize tables if they don't exist yet
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_table (
                    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email_id VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                );
                CREATE TABLE IF NOT EXISTS session_table (
                    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES user_table(user_id),
                    chat_history JSONB NOT NULL DEFAULT '{}'::jsonb
                );
            ''')

    async def disconnect(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()

    async def get_user_by_email(self, email_id: str):
        """Fetch user credentials by email."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT user_id, password FROM user_table WHERE email_id = $1", 
                email_id
            )

    async def get_user_sessions(self, user_id):
        """Fetch all chat sessions for a specific user."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                "SELECT session_id, chat_history FROM session_table WHERE user_id = $1", 
                user_id
            )
    
    async def get_session(self, session_id: str, user_id: str):
        """Fetch a specific session to check if it exists."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT chat_history FROM session_table WHERE session_id = $1 AND user_id = $2",
                session_id, user_id
            )

    async def insert_session(self, session_id: str, user_id: str, chat_history: list):
        """Insert a brand new chat session row."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO session_table (session_id, user_id, chat_history) VALUES ($1, $2, $3)",
                session_id, user_id, json.dumps(chat_history)
            )

    async def update_session_history(self, session_id: str, chat_history: list):
        """Update an existing chat session row."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE session_table SET chat_history = $1 WHERE session_id = $2",
                json.dumps(chat_history), session_id
            )

# Instantiate a global db object to be imported by the main app
db = Database()