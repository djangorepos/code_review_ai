from fastapi import FastAPI, HTTPException, Depends
from app.models import ReviewRequest, ReviewResponse
from app.services.review_service import generate_review
from app.dependencies import get_redis_client
from redis.asyncio import Redis

app = FastAPI(title="CodeReviewAI")


@app.post("/review", response_model=ReviewResponse)
async def review_code(request: ReviewRequest, redis: Redis = Depends(get_redis_client)):
    # Cache key
    cache_key = f"review:{request.github_repo_url}:{request.candidate_level}"
    cached_response = await redis.get(cache_key)

    if cached_response:
        return ReviewResponse.parse_raw(cached_response)

    # Generate review
    try:
        review = await generate_review(request)
        await redis.set(cache_key, review.json(), ex=3600)  # Cache for 1 hour
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate review")
