import logging
from time import sleep

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi_limiter.depends import RateLimiter
from starlette.responses import RedirectResponse
from uvicorn.config import LOGGING_CONFIG

from app.cache import redis_client
from app.models import ReviewRequest, ReviewResponse
from app.services.github_service import get_repo_id
from app.services.review_service import generate_review
from app.dependencies import get_redis_client
from redis.asyncio import Redis

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CodeReviewAI")
app = FastAPI(title="CodeReviewAI", docs_url="/swagger")


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/swagger")  # Redirect to Swagger UI


@app.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest, redis: Redis = Depends(get_redis_client)):
    repo_id, repo_url = await get_repo_id(request.github_repo_url)
    cache_key = f"review:{repo_id}:{repo_url}:{request.candidate_level}"
    # Check Redis cache
    try:
        cached_response = await redis.get(cache_key)
    except Exception as error:
        print(error)
        cached_response = None

    if cached_response:
        logger.info(f"Cache hit for {cache_key}")
        return ReviewResponse.parse_raw(cached_response)

    # Generate review and handle possible errors
    try:
        review = await generate_review(request, repo_id)
        await redis.set(cache_key, review.json(), ex=3600)  # Cache for 1 hour
        logger.info(f"Generated review for {cache_key} and cached the result")
        return review
    except HTTPException as e:
        logger.error(f"Failed to generate review: {e.detail}")
        raise e
    except Exception as e:
        logger.exception("Unexpected error occurred", e)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred, {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=80, log_config=LOGGING_CONFIG)
