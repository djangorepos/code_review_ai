import pytest
from fastapi.testclient import TestClient
from app.main import app

BASE_URL = "http://localhost:8000"
client = TestClient(app)


@pytest.mark.asyncio
async def test_review_endpoint():
    request_payload = {
        "assignment_description": "Test assignment",
        "github_repo_url": "https://api.github.com/repos/djangorepos/code_review_ai",
        "candidate_level": "Junior"
    }

    response = client.post(f"{BASE_URL}/review", json=request_payload)

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
        "github_repo_url": "https://api.github.com/repos/djangorepos/code_review_ai",
        "candidate_level": "InvalidLevel"
    }
    response = client.post(f"{BASE_URL}/review", json=request_payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_github_invalid_link():
    # Test payload for the API request
    request_payload = {
        "assignment_description": "Test assignment",
        "github_repo_url": "https://api.github.com/repos/test/test",
        "candidate_level": "Junior",
    }

    response = client.post(f"{BASE_URL}/review", json=request_payload)

    assert response.status_code == 404
    assert response.json() == {'detail': 'GitHub repository not found.'}