from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_interview_flow():
    created = client.post("/api/interviews", json={"role":"AI Engineer","experience_level":"entry","interview_type":"technical","question_count":3})
    assert created.status_code == 201
    interview_id = created.json()["interview_id"]
    answer = client.post(f"/api/interviews/{interview_id}/answers", json={"answer":"First, I would define the concept clearly. For example, I implemented it because it improves reliability and gives users useful context."})
    assert answer.status_code == 200
    assert 0 <= answer.json()["evaluation"]["score"] <= 10
