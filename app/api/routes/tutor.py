"""Adaptive AI Tutor – API routes."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.tutor_service import AdaptiveTutorService, get_tutor_service

router = APIRouter(prefix="/tutor", tags=["Adaptive AI Tutor"])

class LessonRequest(BaseModel):
    learner_id: str
    subject: str
    topic: str
    learner_name: Optional[str] = "Learner"

class QuestionRequest(BaseModel):
    learner_id: str
    topic: str
    question_type: Optional[str] = "short_answer"

class AnswerRequest(BaseModel):
    learner_id: str
    question: dict
    answer: str

class HintRequest(BaseModel):
    learner_id: str
    question: dict
    attempt: str
    hint_level: Optional[int] = 1

class ReExplainRequest(BaseModel):
    learner_id: str
    concept: str
    original_explanation: str
    confusion: str

@router.post("/lesson")
async def generate_lesson(req: LessonRequest, svc: AdaptiveTutorService = Depends(get_tutor_service)):
    svc.get_or_create_learner(req.learner_id, req.learner_name)
    return svc.generate_lesson(req.learner_id, req.subject, req.topic)

@router.post("/question")
async def generate_question(req: QuestionRequest, svc: AdaptiveTutorService = Depends(get_tutor_service)):
    valid_types = ("multiple_choice", "short_answer", "problem_solving", "explain_concept")
    if req.question_type not in valid_types:
        raise HTTPException(400, f"question_type must be one of {valid_types}")
    return svc.generate_question(req.learner_id, req.topic, req.question_type)

@router.post("/answer")
async def submit_answer(req: AnswerRequest, svc: AdaptiveTutorService = Depends(get_tutor_service)):
    if not req.answer.strip():
        raise HTTPException(400, "Answer cannot be empty")
    return svc.submit_answer(req.learner_id, req.question, req.answer)

@router.post("/hint")
async def get_hint(req: HintRequest, svc: AdaptiveTutorService = Depends(get_tutor_service)):
    from app.core.config import settings
    if req.hint_level > settings.MAX_HINT_DEPTH:
        raise HTTPException(400, f"Max hint level is {settings.MAX_HINT_DEPTH}")
    return svc.get_hint(req.learner_id, req.question, req.attempt, req.hint_level)

@router.post("/re-explain")
async def re_explain(req: ReExplainRequest, svc: AdaptiveTutorService = Depends(get_tutor_service)):
    return svc.re_explain(req.learner_id, req.concept, req.original_explanation, req.confusion)

@router.get("/learner/{learner_id}")
async def get_learner_report(learner_id: str, svc: AdaptiveTutorService = Depends(get_tutor_service)):
    return svc.get_learner_report(learner_id)

@router.get("/learners")
async def list_learners(svc: AdaptiveTutorService = Depends(get_tutor_service)):
    return {"learners": svc.list_learners()}

@router.get("/health")
async def health():
    return {"status": "ok", "service": "Adaptive AI Tutor – Personalized Education with Knowledge Tracking"}
