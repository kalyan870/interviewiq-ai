from uuid import UUID
import pymupdf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models import AnswerResponse, AnswerSubmit, InterviewCreate, InterviewCreated, Report
from app.services.interview_engine import evaluate_answer, generate_question, next_difficulty
from app.services.repository import repository

app = FastAPI(title="AI Mock Interview Partner", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins.split(","), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok", "ai_mode": "openai" if settings.openai_api_key else "demo"}


@app.post("/api/interviews", response_model=InterviewCreated, status_code=201)
def create_interview(payload: InterviewCreate):
    identifier = repository.create(payload)
    question = generate_question(payload, 1, 2)
    repository.get(identifier).questions.append(question)
    return InterviewCreated(interview_id=identifier, question=question)


@app.post("/api/interviews/{interview_id}/answers", response_model=AnswerResponse)
def submit_answer(interview_id: UUID, payload: AnswerSubmit):
    try:
        interview = repository.get(interview_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    if len(interview.evaluations) >= interview.config.question_count:
        raise HTTPException(409, "This interview is already complete")
    evaluation = evaluate_answer(interview.questions[-1], payload.answer)
    interview.answers.append(payload.answer)
    interview.evaluations.append(evaluation)
    completed = len(interview.evaluations) >= interview.config.question_count
    if completed:
        return AnswerResponse(evaluation=evaluation, complete=True)
    previous = interview.questions[-1]
    follow_up = evaluation.score < 6.0
    question = generate_question(interview.config, len(interview.questions) + 1, next_difficulty(previous.difficulty, evaluation.difficulty_action), follow_up, payload.answer)
    interview.questions.append(question)
    return AnswerResponse(evaluation=evaluation, next_question=question)


@app.get("/api/interviews/{interview_id}/report", response_model=Report)
def get_report(interview_id: UUID):
    try:
        return repository.report(interview_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@app.post("/api/resumes/parse")
async def parse_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(415, "Please upload a PDF resume")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(413, "Resume must be smaller than 5 MB")
    try:
        document = pymupdf.open(stream=content, filetype="pdf")
        text = "\n".join(page.get_text() for page in document)
    except Exception as exc:
        raise HTTPException(422, "We could not read this PDF") from exc
    return {"text": text[:12000], "pages": len(document)}
