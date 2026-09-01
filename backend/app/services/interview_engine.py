import json
from uuid import uuid4
try:
    from openai import OpenAI
except ImportError:  # keeps demo mode available before optional AI dependency is installed
    OpenAI = None  # type: ignore[assignment,misc]
from app.config import settings
from app.models import Evaluation, InterviewCreate, Question


TOPICS = {
    "AI Engineer": ["LLM fundamentals", "RAG architecture", "evaluation and safety", "production AI systems"],
    "Software Engineer": ["data structures", "API design", "system design", "reliability"],
    "Data Scientist": ["experimentation", "model evaluation", "feature engineering", "deployment"],
}


def topics_for(role: str) -> list[str]:
    return TOPICS.get(role, ["fundamentals", "implementation", "system design", "best practices"])


def question_for(config: InterviewCreate, number: int, difficulty: int, follow_up: bool = False) -> Question:
    topic = topics_for(config.role)[(number - 1) % len(topics_for(config.role))]
    prefix = "Follow up: " if follow_up else ""
    if config.interview_type.value == "hr":
        body = f"Tell me about a time you handled a difficult situation relevant to a {config.role} role. What was your approach and result?"
    elif config.interview_type.value == "coding":
        body = "Solve this problem: Given a string, return its first non-repeating character. Explain your algorithm, its time and space complexity, and important edge cases."
    elif config.interview_type.value == "system_design":
        body = f"Design a scalable platform for a {config.role} use case. Describe the APIs, data flow, storage, reliability, security, and trade-offs."
    elif config.interview_type.value == "genai":
        body = "Design a production RAG assistant. Explain ingestion, chunking, retrieval, context construction, evaluation, safety, and how you would control cost."
    elif config.interview_type.value == "project_defense":
        body = f"{prefix}For {config.project_name or 'your selected project'}, explain its {topic}. What trade-offs did you make and how would you improve it?"
    elif config.interview_type.value == "resume":
        body = f"{prefix}Based on your experience, explain how you applied {topic} and what measurable impact it created."
    else:
        prompts = {
            "LLM fundamentals": "What is an LLM, and how would you explain its capabilities and limitations to a product team?",
            "RAG architecture": "Explain a retrieval-augmented generation pipeline. How does retrieval reduce hallucinations?",
            "evaluation and safety": "How would you evaluate an AI feature before release and protect users from unsafe output?",
            "production AI systems": "Design a reliable AI service. How would you manage latency, failures, and cost?",
        }
        body = prompts.get(topic, f"Explain the core ideas of {topic} and how you would apply them in a production {config.role} project.")
        if difficulty >= 4:
            body += " Include trade-offs, observability, and a concrete example."
        if follow_up:
            body = prefix + "You mentioned this topic. " + body
    return Question(id=uuid4(), number=number, text=body, topic=topic, difficulty=difficulty, is_follow_up=follow_up)


def generate_question(config: InterviewCreate, number: int, difficulty: int, follow_up: bool = False, context: str = "") -> Question:
    """Uses the model in production and retains a useful offline experience locally."""
    fallback = question_for(config, number, difficulty, follow_up)
    if not settings.openai_api_key or OpenAI is None:
        return fallback
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        prompt = f"""Create exactly one concise interview question as JSON. Role: {config.role}; level: {config.experience_level.value}; mode: {config.interview_type.value}; difficulty 1-5: {difficulty}; question number: {number}. Resume/project context: {config.resume_context or config.project_name or 'none'}. Prior response context: {context[:2000]}. JSON keys: text, topic. Do not include an answer."""
        data = json.loads(client.chat.completions.create(model=settings.openai_model, messages=[{"role":"system","content":"You are a rigorous, supportive interviewer."},{"role":"user","content":prompt}], response_format={"type":"json_object"}).choices[0].message.content or "{}")
        return Question(id=uuid4(), number=number, text=str(data["text"]), topic=str(data.get("topic", "role knowledge")), difficulty=difficulty, is_follow_up=follow_up)
    except Exception:
        return fallback


def evaluate_locally(answer: str) -> Evaluation:
    words = len(answer.split())
    has_example = any(token in answer.lower() for token in ["example", "because", "for instance", "implemented"])
    has_structure = any(token in answer.lower() for token in ["first", "then", "therefore", "however"])
    base = min(8.5, 3.5 + words / 32 + (0.7 if has_example else 0) + (0.5 if has_structure else 0))
    score = round(base, 1)
    gaps = [] if words > 75 else ["Add a concrete implementation example"]
    if not has_example:
        gaps.append("Explain the reasoning behind your technical choices")
    return Evaluation(
        score=score, correctness=score, relevance=round(min(9, score + .3), 1), completeness=round(max(1, score - .4), 1),
        clarity=round(min(9, score + (.4 if has_structure else 0)), 1), technical_depth=round(max(1, score - .5), 1),
        strengths=["Your response addresses the question directly", "You communicated your thinking clearly"], gaps=gaps,
        improved_answer="A stronger answer defines the core concept, explains why it matters, and anchors it with a concise real-world implementation example.",
        feedback="Good direction. Add a specific example and describe the trade-offs to make your answer more interview-ready.",
        difficulty_action="increase" if score >= 7.5 else "maintain" if score >= 5.5 else "decrease",
    )


def evaluate_answer(question: Question, answer: str) -> Evaluation:
    fallback = evaluate_locally(answer)
    if not settings.openai_api_key or OpenAI is None:
        return fallback
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        schema = "score, correctness, relevance, completeness, clarity, technical_depth (numbers 0-10), strengths (array), gaps (array), improved_answer, feedback, difficulty_action (increase|maintain|decrease)"
        prompt = f"Evaluate this candidate answer to the interview question. Weight score: correctness 30%, relevance 20%, completeness 20%, clarity 15%, technical depth 15%. Return JSON only with {schema}. Question: {question.text}\nAnswer: {answer}"
        data = json.loads(client.chat.completions.create(model=settings.openai_model, messages=[{"role":"system","content":"You give specific, fair interview feedback. Never invent achievements."},{"role":"user","content":prompt}], response_format={"type":"json_object"}).choices[0].message.content or "{}")
        return Evaluation.model_validate(data)
    except Exception:
        return fallback


def next_difficulty(current: int, action: str) -> int:
    return max(1, min(5, current + (1 if action == "increase" else -1 if action == "decrease" else 0)))
