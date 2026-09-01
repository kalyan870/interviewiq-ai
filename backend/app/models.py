from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field


class ExperienceLevel(str, Enum):
    entry = "entry"
    mid = "mid"
    senior = "senior"


class InterviewType(str, Enum):
    technical = "technical"
    hr = "hr"
    mixed = "mixed"
    resume = "resume"
    project_defense = "project_defense"
    coding = "coding"
    system_design = "system_design"
    genai = "genai"


class InterviewCreate(BaseModel):
    role: str = Field(min_length=2, max_length=100)
    experience_level: ExperienceLevel
    interview_type: InterviewType
    question_count: int = Field(ge=3, le=20)
    resume_context: str | None = Field(default=None, max_length=12000)
    project_name: str | None = Field(default=None, max_length=200)


class Question(BaseModel):
    id: UUID
    number: int
    text: str
    topic: str
    difficulty: int = Field(ge=1, le=5)
    is_follow_up: bool = False


class InterviewCreated(BaseModel):
    interview_id: UUID
    question: Question


class AnswerSubmit(BaseModel):
    answer: str = Field(min_length=10, max_length=10000)


class Evaluation(BaseModel):
    score: float = Field(ge=0, le=10)
    correctness: float = Field(ge=0, le=10)
    relevance: float = Field(ge=0, le=10)
    completeness: float = Field(ge=0, le=10)
    clarity: float = Field(ge=0, le=10)
    technical_depth: float = Field(ge=0, le=10)
    strengths: list[str]
    gaps: list[str]
    improved_answer: str
    feedback: str
    difficulty_action: str


class AnswerResponse(BaseModel):
    evaluation: Evaluation
    next_question: Question | None = None
    complete: bool = False


class Report(BaseModel):
    interview_id: UUID
    overall_score: float
    technical_knowledge: int
    communication: int
    problem_solving: int
    strengths: list[str]
    improvement_areas: list[str]
    recommended_topics: list[str]
    assessment: str
    answered_questions: int
