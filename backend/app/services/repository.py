from dataclasses import dataclass, field
from uuid import UUID, uuid4
from app.models import InterviewCreate, Question, Evaluation, Report


@dataclass
class StoredInterview:
    config: InterviewCreate
    questions: list[Question] = field(default_factory=list)
    evaluations: list[Evaluation] = field(default_factory=list)
    answers: list[str] = field(default_factory=list)


class InterviewRepository:
    """Replace with Supabase persistence in production; keeps local development runnable."""
    def __init__(self):
        self.items: dict[UUID, StoredInterview] = {}

    def create(self, config: InterviewCreate) -> UUID:
        identifier = uuid4()
        self.items[identifier] = StoredInterview(config=config)
        return identifier

    def get(self, identifier: UUID) -> StoredInterview:
        if identifier not in self.items:
            raise KeyError("Interview not found")
        return self.items[identifier]

    def report(self, identifier: UUID) -> Report:
        item = self.get(identifier)
        evaluations = item.evaluations
        if not evaluations:
            raise ValueError("No answers have been evaluated yet")
        average = sum(e.score for e in evaluations) / len(evaluations)
        strengths = [x for e in evaluations for x in e.strengths]
        gaps = [x for e in evaluations for x in e.gaps]
        unique = lambda values: list(dict.fromkeys(values))[:4]
        return Report(
            interview_id=identifier, overall_score=round(average * 10),
            technical_knowledge=round(sum(e.correctness for e in evaluations) / len(evaluations) * 10),
            communication=round(sum(e.clarity for e in evaluations) / len(evaluations) * 10),
            problem_solving=round(sum(e.technical_depth for e in evaluations) / len(evaluations) * 10),
            strengths=unique(strengths) or ["You engaged thoughtfully with each question."],
            improvement_areas=unique(gaps) or ["Continue practising more concrete examples."],
            recommended_topics=unique(gaps) or ["Advanced role-specific concepts"],
            assessment=("Strong performance with clear interview readiness." if average >= 7 else "A promising foundation; focused practice will improve confidence."),
            answered_questions=len(evaluations),
        )


repository = InterviewRepository()
