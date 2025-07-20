# test_register.py

from fastapi.testclient import TestClient
from main import app, DB_NAME
import sqlite3
import os
import pytest

# Create a TestClient instance. This lets us send requests to our app in our tests.
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown_database():
    """
    This is a special pytest 'fixture' that prepares our test environment.
    `autouse=True` means it runs automatically before every single test function.
    Its job is to ensure every test starts with a fresh, empty database.
    """
    # --- SETUP PHASE (runs before each test) ---
    # To be safe, delete the database file if it exists from a previous failed run.
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    # Re-initialize a clean database and table for the upcoming test.
    from main import init_db
    init_db()
    
    # The 'yield' keyword passes control to the test function, which then runs.
    yield
    
    # --- TEARDOWN PHASE (runs after each test) ---
    # After the test is complete, clean up by deleting the database file.
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

def test_register_user_successfully():
    """
    This is our "happy path" test. It verifies the entire flow for a new user.
    """
    # 1. ARRANGE & ACT: Send a real HTTP POST request to the /register endpoint.
    response = client.post("/register", json={
        "username": "shoaib",
        "email": "shoaib@example.com"
    })
    
    # 2. ASSERT: Check that the API responded with a 200 OK status code and the correct message.
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    # 3. VERIFY: The most important step of an integration test.
    # Go behind the API's back and check the database directly to confirm the data was written.
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, email FROM users WHERE username = 'shoaib'")
    user_from_db = cursor.fetchone() # Fetch the first matching row.
    conn.close()

    # Assert that we found the user and their details are correct.
    assert user_from_db is not None
    assert user_from_db == ("shoaib", "shoaib@example.com")

def test_register_duplicate_user():
    """

    This is our "sad path" test. It verifies the API handles errors correctly.
    """
    # 1. ARRANGE: Register a user successfully first.
    client.post("/register", json={"username": "testuser", "email": "test@example.com"})

    # 2. ACT: Try to register the exact same user a second time.
    response = client.post("/register", json={"username": "testuser", "email": "test@example.com"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Username or email already exists."}