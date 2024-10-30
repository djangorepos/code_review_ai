import httpx
from app.config import settings


async def fetch_repository_contents(repo_url: str):
    headers = {"Authorization": f"token {settings.GITHUB_TOKEN}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{repo_url}/contents", headers=headers)
        response.raise_for_status()
        return response.json()
