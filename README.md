> **📅 Project Period:** Dec 2025 – Jan 2026 &nbsp;|&nbsp; **Status:** Completed &nbsp;|&nbsp; **Author:** [Bharghava Ram Vemuri](https://github.com/bharghavaram)

# Adaptive AI Tutor

> Personalized AI education system with real-time knowledge tracking and adaptive difficulty

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/GPT--4o-Tutor-purple)](https://openai.com)

## Overview

An intelligent tutoring system that **adapts in real-time** to each learner's knowledge level, learning pace, and weak areas. Uses exponential moving average mastery scoring, spaced repetition hints, and multi-style explanations to maximise learning outcomes.

## Core Features

- **Real-time mastery tracking** – per-topic mastery scores (0-1) updated via EMA after each answer
- **Adaptive difficulty** – automatically adjusts from beginner → intermediate → advanced → expert
- **4 question types** – multiple choice, short answer, problem solving, explain-concept
- **3-level hint system** – subtle → directional → near-answer, preserving learning
- **Re-explanation** – if the learner is confused, generates an alternative explanation (analogy, story, step-by-step)
- **Learner progress reports** – full mastery map, accuracy, question history

## Mastery Algorithm

```
After each answer:
  new_mastery = 0.7 × current_mastery + 0.3 × assessment_score (EMA)

Level adaptation:
  avg_mastery ≥ 0.85 → expert
  avg_mastery ≥ 0.65 → advanced
  avg_mastery ≥ 0.40 → intermediate
  else               → beginner
```

## Quick Start

```bash
git clone https://github.com/bharghavaram/adaptive-ai-tutor
cd adaptive-ai-tutor
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tutor/lesson` | Generate adaptive lesson |
| POST | `/api/v1/tutor/question` | Generate practice question |
| POST | `/api/v1/tutor/answer` | Submit answer + get feedback |
| POST | `/api/v1/tutor/hint` | Get progressive hint |
| POST | `/api/v1/tutor/re-explain` | Alternative explanation |
| GET | `/api/v1/tutor/learner/{id}` | Progress report |

### Learning Flow Example

```bash
# 1. Generate a lesson
curl -X POST ".../tutor/lesson" -d '{"learner_id": "u1", "subject": "ML", "topic": "neural networks"}'

# 2. Get a practice question
curl -X POST ".../tutor/question" -d '{"learner_id": "u1", "topic": "neural networks"}'

# 3. Submit an answer
curl -X POST ".../tutor/answer" -d '{"learner_id": "u1", "question": {...}, "answer": "backpropagation"}'

# 4. Check progress
curl ".../tutor/learner/u1"
```
