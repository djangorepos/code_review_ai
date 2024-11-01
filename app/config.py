import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    OPENAI_API_KEY = os.getenv("API_KEY")
    MODEL = os.getenv("MODEL")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


settings = Settings()
