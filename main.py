"""Adaptive AI Tutor – FastAPI Entry Point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.tutor import router
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s – %(message)s")

app = FastAPI(
    title="Adaptive AI Tutor",
    description="Personalized AI tutoring system that adapts difficulty, teaching style, and content in real-time based on learner performance. Features knowledge tracking, spaced repetition hints, and mastery-based progression.",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "service": "Adaptive AI Tutor",
        "version": "1.0.0",
        "features": ["Real-time mastery tracking per topic", "Adaptive difficulty (beginner → expert)", "Multiple question types", "3-level hint system", "Alternative explanations (analogies/stories)", "Learner progress reports", "Exponential moving average mastery scoring"],
        "mastery_threshold": settings.MASTERY_THRESHOLD,
        "docs": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
