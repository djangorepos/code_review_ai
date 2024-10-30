import pytest
import redis
from fastapi import HTTPException

from httpx import AsyncClient, HTTPError, RequestError, HTTPStatusError
from app.main import app

BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_review_endpoint():
    request_payload = {
        "assignment_description": "Test assignment",
        "github_repo_url": "https://api.github.com/repos/djangorepos/code_review_ai",
        "candidate_level": "Junior"
    }
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/review", json=request_payload)

    assert response.status_code == 200
    data = response.json()
    assert "found_files" in data
    assert "downsides" in data
    assert "rating" in data
    assert "comments" in data


@pytest.mark.asyncio
async def test_invalid_candidate_level():
    request_payload = {
        "assignment_description": "Test assignment",
        "github_repo_url": "https://api.github.com/repos/djangorepos/code_review_ai",
        "candidate_level": "InvalidLevel"
    }
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        response = await client.post("/review", json=request_payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_github_rate_limit_handling(monkeypatch):
    # Mock the GitHub service function to raise a rate limit error
    async def mock_get_repository_contents(*args, **kwargs):
        raise HTTPException(status_code=429, detail="GitHub API rate limit exceeded.")

    # Patch the function in the correct module
    monkeypatch.setattr("app.services.github_service.get_repository_contents", mock_get_repository_contents)

    # Test payload for the API request
    request_payload = {
        "assignment_description": "Test assignment",
        "github_repo_url": "https://api.github.com/repos/test/test",
        "candidate_level": "Junior",
    }

    # Use a fresh event loop for each test
    async with AsyncClient(app=app, base_url=BASE_URL) as ac:
        with pytest.raises(HTTPException) as error:
            await ac.post("/review", json=request_payload)

        # Assertions for the error response
        assert error.value.status_code == 429
        assert error.value.detail == "GitHub API rate limit exceeded."
