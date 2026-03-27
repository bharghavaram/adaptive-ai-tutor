"""
Adaptive AI Tutor – Personalized education with knowledge tracking and spaced repetition.
Adapts difficulty, style, and content based on real-time learner performance.
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Optional, List
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

CONCEPT_ASSESSMENT_PROMPT = """Assess the learner's understanding of this concept based on their answer.

Concept: {concept}
Difficulty: {difficulty}
Question: {question}
Learner's Answer: {answer}
Expected Answer: {expected}

JSON response:
{{
  "is_correct": true/false,
  "mastery_score": 0.0-1.0,
  "understanding_level": "none|partial|good|expert",
  "misconceptions": [...],
  "strengths": [...],
  "feedback": "encouraging, specific feedback",
  "needs_reinforcement": true/false
}}"""

LESSON_GENERATION_PROMPT = """Create a personalized lesson for this learner.

Subject: {subject}
Topic: {topic}
Learner Level: {level}
Known Concepts: {known}
Weak Areas: {weak_areas}
Learning Style: {style}

Generate an engaging lesson with:
1. Brief introduction connecting to what they know
2. Core concept explanation (adapted to their level)
3. 2-3 concrete examples
4. Key takeaways

JSON: {{"title": "...", "introduction": "...", "content": "...", "examples": [...], "key_takeaways": [...], "estimated_minutes": 5-15}}"""

QUESTION_GENERATION_PROMPT = """Generate a practice question for this learner.

Topic: {topic}
Difficulty: {difficulty} (beginner/intermediate/advanced/expert)
Question Type: {q_type} (multiple_choice/short_answer/problem_solving/explain_concept)
Previously Asked: {previous_questions}
Weak Areas: {weak_areas}

JSON: {{
  "question": "...",
  "question_type": "...",
  "expected_answer": "...",
  "hints": ["hint1", "hint2", "hint3"],
  "difficulty": "...",
  "concept_tested": "..."
}}"""

HINT_PROMPT = """Give hint #{hint_level} for this problem (hint 1 = subtle, hint 3 = almost the answer).
Question: {question}
Previous hints given: {previous_hints}
Learner's attempt: {attempt}
Answer: {answer}
Return just the hint text, no JSON."""

ADAPTIVE_EXPLANATION_PROMPT = """Re-explain this concept differently. The learner didn't understand the first explanation.

Concept: {concept}
Original Explanation: {original}
Learner's confusion: {confusion}
Learner Level: {level}

Try a completely different approach: use an analogy, a story, a visual description, or step-by-step breakdown.
Make it engaging and relatable for a {level} learner."""


class LearnerProfile:
    def __init__(self, learner_id: str, name: str = "Learner"):
        self.learner_id = learner_id
        self.name = name
        self.subject_mastery: dict = {}  # topic -> mastery score 0-1
        self.question_history: list = []
        self.session_history: list = []
        self.current_level: str = "beginner"
        self.learning_style: str = "visual"  # visual/verbal/example-based
        self.total_questions = 0
        self.correct_answers = 0
        self.created_at = datetime.utcnow().isoformat()
        self.last_active = datetime.utcnow().isoformat()

    @property
    def accuracy(self) -> float:
        if self.total_questions == 0:
            return 0.0
        return round(self.correct_answers / self.total_questions, 3)

    @property
    def mastered_topics(self) -> list:
        return [t for t, s in self.subject_mastery.items() if s >= settings.MASTERY_THRESHOLD]

    @property
    def weak_topics(self) -> list:
        return [t for t, s in self.subject_mastery.items() if s < 0.5]

    def update_mastery(self, topic: str, score: float):
        current = self.subject_mastery.get(topic, 0.5)
        # Exponential moving average
        self.subject_mastery[topic] = round(0.7 * current + 0.3 * score, 3)

    def update_level(self):
        avg_mastery = sum(self.subject_mastery.values()) / max(len(self.subject_mastery), 1)
        if avg_mastery >= 0.85: self.current_level = "expert"
        elif avg_mastery >= 0.65: self.current_level = "advanced"
        elif avg_mastery >= 0.4: self.current_level = "intermediate"
        else: self.current_level = "beginner"

    def to_dict(self):
        return {
            "learner_id": self.learner_id,
            "name": self.name,
            "current_level": self.current_level,
            "learning_style": self.learning_style,
            "accuracy": self.accuracy,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "mastered_topics": self.mastered_topics,
            "weak_topics": self.weak_topics,
            "subject_mastery": self.subject_mastery,
            "last_active": self.last_active,
        }


class AdaptiveTutorService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._learners: dict[str, LearnerProfile] = {}

    def _call_llm(self, prompt: str, json_mode: bool = False) -> str:
        kwargs = {
            "model": settings.LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": settings.TEMPERATURE,
            "max_tokens": settings.MAX_TOKENS,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        return self.client.chat.completions.create(**kwargs).choices[0].message.content

    def get_or_create_learner(self, learner_id: str, name: str = "Learner") -> LearnerProfile:
        if learner_id not in self._learners:
            self._learners[learner_id] = LearnerProfile(learner_id, name)
        return self._learners[learner_id]

    def generate_lesson(self, learner_id: str, subject: str, topic: str) -> dict:
        learner = self.get_or_create_learner(learner_id)
        prompt = LESSON_GENERATION_PROMPT.format(
            subject=subject, topic=topic, level=learner.current_level,
            known=", ".join(learner.mastered_topics[:5]) or "None yet",
            weak_areas=", ".join(learner.weak_topics[:3]) or "None identified",
            style=learner.learning_style,
        )
        result = self._call_llm(prompt, json_mode=True)
        try:
            lesson = json.loads(result)
        except Exception:
            lesson = {"title": topic, "content": result}
        lesson["learner_id"] = learner_id
        lesson["topic"] = topic
        lesson["level"] = learner.current_level
        return lesson

    def generate_question(self, learner_id: str, topic: str, question_type: str = "short_answer") -> dict:
        learner = self.get_or_create_learner(learner_id)
        mastery = learner.subject_mastery.get(topic, 0.5)
        # Adaptive difficulty
        if mastery < 0.3: difficulty = "beginner"
        elif mastery < 0.6: difficulty = "intermediate"
        elif mastery < 0.8: difficulty = "advanced"
        else: difficulty = "expert"

        recent_questions = [q["question"][:50] for q in learner.question_history[-5:]]
        prompt = QUESTION_GENERATION_PROMPT.format(
            topic=topic, difficulty=difficulty, q_type=question_type,
            previous_questions="\n".join(recent_questions) or "None",
            weak_areas=", ".join(learner.weak_topics[:3]) or "None",
        )
        result = self._call_llm(prompt, json_mode=True)
        try:
            question = json.loads(result)
        except Exception:
            question = {"question": result, "expected_answer": "", "hints": [], "difficulty": difficulty, "concept_tested": topic}

        question["question_id"] = str(uuid.uuid4())
        question["topic"] = topic
        question["learner_id"] = learner_id
        return question

    def submit_answer(self, learner_id: str, question: dict, answer: str) -> dict:
        learner = self.get_or_create_learner(learner_id)
        prompt = CONCEPT_ASSESSMENT_PROMPT.format(
            concept=question.get("concept_tested", question.get("topic", "")),
            difficulty=question.get("difficulty", "intermediate"),
            question=question["question"],
            answer=answer,
            expected=question.get("expected_answer", ""),
        )
        result = self._call_llm(prompt, json_mode=True)
        try:
            assessment = json.loads(result)
        except Exception:
            assessment = {"is_correct": False, "mastery_score": 0.3, "feedback": result}

        # Update learner profile
        topic = question.get("topic", "general")
        mastery_score = float(assessment.get("mastery_score", 0.5))
        learner.update_mastery(topic, mastery_score)
        learner.update_level()
        learner.total_questions += 1
        if assessment.get("is_correct"):
            learner.correct_answers += 1
        learner.last_active = datetime.utcnow().isoformat()
        learner.question_history.append({
            "question": question["question"],
            "answer": answer,
            "is_correct": assessment.get("is_correct"),
            "mastery_score": mastery_score,
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Determine next action
        if not assessment.get("is_correct") and assessment.get("needs_reinforcement"):
            next_action = "retry_with_hint"
        elif mastery_score >= settings.MASTERY_THRESHOLD:
            next_action = "advance_topic"
        else:
            next_action = "practice_more"

        return {
            "assessment": assessment,
            "learner_progress": learner.to_dict(),
            "next_action": next_action,
            "topic_mastery": learner.subject_mastery.get(topic, 0),
        }

    def get_hint(self, learner_id: str, question: dict, attempt: str, hint_level: int = 1) -> dict:
        previous_hints = [f"Hint {i+1}" for i in range(hint_level - 1)]
        prompt = HINT_PROMPT.format(
            hint_level=hint_level, question=question["question"],
            previous_hints=", ".join(previous_hints) or "None",
            attempt=attempt,
            answer=question.get("expected_answer", ""),
        )
        hint = self._call_llm(prompt)
        return {"hint_level": hint_level, "hint": hint, "max_hints": settings.MAX_HINT_DEPTH}

    def re_explain(self, learner_id: str, concept: str, original_explanation: str, confusion: str) -> dict:
        learner = self.get_or_create_learner(learner_id)
        prompt = ADAPTIVE_EXPLANATION_PROMPT.format(
            concept=concept, original=original_explanation,
            confusion=confusion, level=learner.current_level,
        )
        new_explanation = self._call_llm(prompt)
        return {"concept": concept, "new_explanation": new_explanation, "approach": "alternative"}

    def get_learner_report(self, learner_id: str) -> dict:
        learner = self.get_or_create_learner(learner_id)
        return {
            **learner.to_dict(),
            "recent_questions": learner.question_history[-10:],
        }

    def list_learners(self) -> list:
        return [l.to_dict() for l in self._learners.values()]


_service: Optional[AdaptiveTutorService] = None
def get_tutor_service() -> AdaptiveTutorService:
    global _service
    if _service is None:
        _service = AdaptiveTutorService()
    return _service
