# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

# Initialize the FastAPI app instance
app = FastAPI()

# Define the database file name. It will be created in the project's root directory.
DB_NAME = "test.db"

def init_db():
    """
    Initializes the database. It connects to the SQLite file and creates the
    'users' table if it does not already exist. This ensures our app can always
    rely on the table being there.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Using 'IF NOT EXISTS' is a safe way to run this multiple times.
    # UNIQUE constraints prevent duplicate usernames or emails.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Run the database initialization once when the application starts up.
init_db()

# Pydantic model to define the expected structure of the request body.
# FastAPI uses this for automatic data validation.
class User(BaseModel):
    username: str
    email: str

@app.post("/register")
def register_user(user: User):
    """
    This is our API endpoint. It listens for POST requests on the /register URL.
    It takes a User object, saves it to the database, and returns a success message.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (user.username, user.email)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # This error occurs if the username or email already exists (due to the UNIQUE constraint).
        # We catch it and return a user-friendly 400 error.
        raise HTTPException(status_code=400, detail="Username or email already exists.")
    finally:
        # The 'finally' block ensures the database connection is always closed,
        # even if an error occurs.
        conn.close()
    
    return {"message": "User registered successfully"}