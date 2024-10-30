import openai
from fastapi import HTTPException
from app.config import settings
import logging

logger = logging.getLogger("CodeReviewAI")
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
model = "gpt-4o-mini"


async def analyze_code(assigment, level, contents: str) -> str:
    try:
        messages = [{"role": "user",
                     "content": f"""Task was {assigment} for candidate level {level}. Analyze the following code and write paragraphs:
                                Downsides, Rating in format (n/5) only numbers, and some comments on next line"
                                Use the following response format, keeping the section headings as-is, and provide
                                your feedback. Use bullet points for each response. The provided examples are for 
                                illustration purposes only and should not be repeated."
                                ### Downsides:"
                                - something wrong
                                - something wrong
                                - something wrong
                                ### Rating:
                                n/5
                                ### Comments:
                                Despite the downsides mentioned above, some comments.
                                {contents}"""}]
        completion = client.chat.completions.create(
            model=model, messages=messages, max_tokens=1024, n=1,
            stop=None, temperature=0.5
        )
        return completion.choices[0].message.content.strip()

    except openai.RateLimitError:
        logger.error("OpenAI API rate limit exceeded.")
        raise HTTPException(status_code=429, detail="OpenAI API rate limit exceeded.")
    except openai.BadRequestError as e:
        logger.error(f"Invalid request to OpenAI API: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid request to OpenAI API.")
    except openai.OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error communicating with OpenAI API.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
