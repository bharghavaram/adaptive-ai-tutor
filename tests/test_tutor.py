"""Tests for Adaptive AI Tutor."""
import pytest
from app.core.config import settings
from app.services.tutor_service import LearnerProfile

def test_settings():
    assert settings.MASTERY_THRESHOLD == 0.8
    assert settings.MAX_HINT_DEPTH == 3

def test_learner_profile_creation():
    learner = LearnerProfile("user123", "Alice")
    assert learner.learner_id == "user123"
    assert learner.name == "Alice"
    assert learner.current_level == "beginner"
    assert learner.accuracy == 0.0

def test_mastery_update_ema():
    learner = LearnerProfile("u1")
    learner.update_mastery("python", 1.0)
    assert learner.subject_mastery["python"] > 0.5
    learner.update_mastery("python", 0.0)
    assert learner.subject_mastery["python"] < 0.9

def test_mastered_topics():
    learner = LearnerProfile("u1")
    learner.subject_mastery["python"] = 0.9
    learner.subject_mastery["sql"] = 0.4
    assert "python" in learner.mastered_topics
    assert "sql" not in learner.mastered_topics

def test_weak_topics():
    learner = LearnerProfile("u1")
    learner.subject_mastery["ml"] = 0.3
    learner.subject_mastery["dl"] = 0.85
    assert "ml" in learner.weak_topics
    assert "dl" not in learner.weak_topics

def test_level_adaptation():
    learner = LearnerProfile("u1")
    learner.subject_mastery["a"] = 0.9
    learner.subject_mastery["b"] = 0.9
    learner.update_level()
    assert learner.current_level == "expert"

def test_accuracy_tracking():
    learner = LearnerProfile("u1")
    learner.total_questions = 10
    learner.correct_answers = 8
    assert learner.accuracy == 0.8

def test_to_dict():
    learner = LearnerProfile("u1", "Bob")
    d = learner.to_dict()
    assert d["learner_id"] == "u1"
    assert d["name"] == "Bob"
    assert "subject_mastery" in d

@pytest.mark.asyncio
async def test_api_health():
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    resp = client.get("/api/v1/tutor/health")
    assert resp.status_code == 200
