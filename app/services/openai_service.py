import openai
from fastapi import HTTPException
from app.config import settings
import logging

logger = logging.getLogger("CodeReviewAI")

openai.api_key = settings.OPENAI_API_KEY


async def analyze_code(contents: str) -> str:
    try:
        response = openai.Completion.create(
            model="gpt-4-turbo",
            prompt=f"Analyze the following code: {contents}",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except openai.RateLimitError:
        logger.error("OpenAI API rate limit exceeded.")
        raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded.")
    except openai.OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error communicating with OpenAI API.")
