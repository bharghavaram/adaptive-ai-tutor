import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    MASTERY_THRESHOLD: float = float(os.getenv("MASTERY_THRESHOLD", "0.8"))
    MIN_PRACTICE_QUESTIONS: int = int(os.getenv("MIN_PRACTICE_QUESTIONS", "3"))
    MAX_HINT_DEPTH: int = int(os.getenv("MAX_HINT_DEPTH", "3"))
    DIFFICULTY_LEVELS: list = ["beginner", "intermediate", "advanced", "expert"]
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

settings = Settings()
