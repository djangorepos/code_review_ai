import httpx
from fastapi import HTTPException
from app.config import settings
import logging

logger = logging.getLogger("CodeReviewAI")


async def fetch_repository_contents(repo_url: str):
    headers = {"Authorization": f"token {settings.GITHUB_TOKEN}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{repo_url}/contents", headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.error("GitHub API rate limit exceeded.")
                raise HTTPException(status_code=429, detail="GitHub API rate limit exceeded.")
            elif e.response.status_code == 404:
                logger.error("GitHub repository not found.")
                raise HTTPException(status_code=404, detail="GitHub repository not found.")
            else:
                logger.error(f"GitHub API error: {e.response.text}")
                raise HTTPException(status_code=e.response.status_code, detail="GitHub API error.")
