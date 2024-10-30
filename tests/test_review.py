import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_review_endpoint():
    request_payload = {
        "assignment_description": "Test assignment",
        "github_repo_url": "https://api.github.com/repos/testuser/testrepo",
        "candidate_level": "Junior"
    }
    async with AsyncClient(app=app, base_url="localhost") as client:
        response = await client.post("/review", json=request_payload)

    assert response.status_code == 200
    data = response.json()
    assert "found_files" in data
    assert "downsides" in data
    assert "rating" in data
    assert "conclusion" in data


@pytest.mark.asyncio
async def test_invalid_candidate_level():
    request_payload = {
        "assignment_description": "Test assignment",
        "github_repo_url": "https://api.github.com/repos/testuser/testrepo",
        "candidate_level": "InvalidLevel"
    }
    async with AsyncClient(app=app, base_url="localhost") as client:
        response = await client.post("/review", json=request_payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_github_rate_limit_handling(monkeypatch):
    async def mock_fetch_repository_contents():
        raise HTTPException(status_code=429, detail="GitHub API rate limit exceeded.")

    monkeypatch.setattr("app.services.github.fetch_repository_contents", mock_fetch_repository_contents)

    request_payload = {
        "assignment_description": "Test assignment",
        "github_repo_url": "https://api.github.com/repos/testuser/testrepo",
        "candidate_level": "Junior"
    }
    async with AsyncClient(app=app, base_url="localhost") as client:
        response = await client.post("/review", json=request_payload)

    assert response.status_code == 429
    assert response.json()["detail"] == "GitHub API rate limit exceeded."
