from fastapi.testclient import TestClient
from app.main import app
from app.db.init_db import init_db
import json

# Ensure db is initialized before testing
init_db()

client = TestClient(app)

def test_read_main():
    # In main.py, the root is at `/` not `/api/v1/`
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Aethera (SkillForge) API"}

def test_db_save_and_get():
    # Test saving course progress
    test_data = {
        "user_id": "test_user_123",
        "target_skill": "Python",
        "course_data": {"title": "Python Basics"}
    }
    response = client.post("/api/v1/progress/save_course", json=test_data)
    assert response.status_code == 200

    # Test getting course progress
    response = client.get("/api/v1/progress/get_course/test_user_123")
    assert response.status_code == 200
    data = response.json()
    assert data["target_skill"] == "Python"
    assert data["course_data"]["title"] == "Python Basics"

if __name__ == "__main__":
    test_read_main()
    test_db_save_and_get()
    print("Basic endpoint and database tests passed!")
