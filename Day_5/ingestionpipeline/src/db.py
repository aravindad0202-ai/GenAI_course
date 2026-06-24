import asyncpg
import os
import json

DATABASE_URL = os.getenv('DATABASE_URL')

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
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(255) NOT NULL,
                    department VARCHAR(255) NOT NULL
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
                "SELECT user_id, password, role, department FROM user_table WHERE email_id = $1", 
                email_id
            )
        
db= Database()