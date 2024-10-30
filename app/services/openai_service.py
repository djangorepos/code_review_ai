import logging
import openai
import time
from fastapi import HTTPException
from openai import RateLimitError
from app.config import settings


logger = logging.getLogger("CodeReviewAI")
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
MODEL = settings.MODEL
MAX_RETRIES = 5


async def analyze_code(assignment: str, level: str, contents: str) -> str:
    max_retries = 5  # Define the maximum number of retries for rate limit errors

    try:
        messages = [{
            "role": "user",
            "content": f"""Task was {assignment} for candidate level {level}. Analyze the following code and write paragraphs:
            Downsides, Rating in format (n/5) only numbers, and some comments on next line.
            Use the following response format, keeping the section headings as-is, and provide
            your feedback. Use bullet points for each response. The provided examples are for 
            illustration purposes only and should not be repeated.
            ### Downsides:
            - something wrong
            - something wrong
            - something wrong
            ### Rating:
            n/5
            ### Comments:
            Despite the downsides mentioned above, some comments.
            {contents}"""
        }]

        retries = 0
        while retries < max_retries:
            try:
                completion = client.chat.completions.create(
                    model=MODEL, messages=messages, max_tokens=1024, n=1,
                    stop=None, temperature=0.5
                )
                response = completion.choices[0].message.content.strip()

                return response

            except RateLimitError as e:
                logger.warning(f"Rate limit exceeded: {e}. Retrying in {2 ** retries} seconds...")
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                time.sleep(wait_time)

            except openai.OpenAIError as e:
                logger.error(f"OpenAI API error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

        # Raise an exception if max retries are exceeded
        logger.error("Max retries exceeded. Unable to get a response from the API.")
        raise HTTPException(status_code=503, detail="Max retries exceeded. Unable to get a response from the API.")

    except openai.BadRequestError as e:
        logger.error(f"Invalid request to OpenAI API: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid request to OpenAI API. Check your input parameters.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")
