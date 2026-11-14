import asyncio
from io import BytesIO

import pymupdf
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.datastructures import Headers, UploadFile

from app.main import MAX_RESUME_BYTES, app, parse_resume

client = TestClient(app)


def test_interview_flow():
    created = client.post("/api/interviews", json={"role":"AI Engineer","experience_level":"entry","interview_type":"technical","question_count":3})
    assert created.status_code == 201
    interview_id = created.json()["interview_id"]
    answer = client.post(f"/api/interviews/{interview_id}/answers", json={"answer":"First, I would define the concept clearly. For example, I implemented it because it improves reliability and gives users useful context."})
    assert answer.status_code == 200
    assert 0 <= answer.json()["evaluation"]["score"] <= 10


def test_resume_pdf_extracts_text():
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Experience with Python and AI projects")
    content = document.tobytes()
    document.close()

    response = client.post(
        "/api/resumes/parse",
        files={"file": ("resume.pdf", content, "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["pages"] == 1
    assert "Python and AI projects" in response.json()["text"]


def test_resume_upload_rejects_oversize_before_full_read():
    class TrackingUpload(UploadFile):
        async def read(self, size: int = -1) -> bytes:
            self.requested_read_size = size
            return await super().read(size)

    upload = TrackingUpload(
        filename="large.pdf",
        file=BytesIO(b"x" * (MAX_RESUME_BYTES + 100)),
        headers=Headers({"content-type": "application/pdf"}),
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(parse_resume(upload))

    assert error.value.status_code == 413
    assert upload.requested_read_size == MAX_RESUME_BYTES + 1


def test_resume_upload_rejects_wrong_media_type():
    response = client.post(
        "/api/resumes/parse",
        files={"file": ("resume.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 415
