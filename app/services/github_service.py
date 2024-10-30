import httpx
from fastapi import HTTPException
from app.config import settings
import logging

logger = logging.getLogger("CodeReviewAI")
headers = {"Authorization": f"token {settings.GITHUB_TOKEN}"}


async def get_repository_contents(github_repo_url: str):
    repository_data = []
    repo_contents = await fetch_repository_contents(format_repo_url(str(github_repo_url)))

    for item in repo_contents:
        await process_item(item, repository_data)

    return repository_data


def format_repo_url(repo_url):
    # Ensure the URL starts with the correct prefix
    if repo_url.startswith("https://github.com"):
        repo_url = repo_url.replace("github.com", "api.github.com/repos")

        # Remove the '.git' suffix if present
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]  # Remove the last 4 characters (".git")

    return f"{repo_url}/contents"


async def fetch_repository_contents(repo_url: str):
    print(repo_url)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(repo_url, headers=headers)
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


async def process_item(item, repository_data):
    """Process a single item in the repository contents."""
    if item['type'] == 'file':
        file_url = item['download_url']
        try:
            content = await fetch_file_contents(file_url)
            repository_data.append({"path": item["path"], "content": content})
            return repository_data
        except Exception as e:
            print(f"Error fetching {item['name']}: {e}")
    elif item['type'] == 'dir':
        # If the item is a directory, fetch its contents recursively
        print(f"Entering directory: {item['name']}")
        directory_contents = await fetch_repository_contents(item['url'])
        for sub_item in directory_contents:
            repository_data = await process_item(sub_item, repository_data)  # Process each item in the directory


async def fetch_file_contents(file_url):
    async with httpx.AsyncClient() as client:
        response = await client.get(file_url, headers=headers)
        response.raise_for_status()

        # Inspect the content type of the response
        content_type = response.headers.get('Content-Type', '')

        # If the content is JSON, decode it as JSON
        if 'application/json' in content_type:
            return response.json()
        # If the content is text (like .gitignore), return it as text
        elif 'text/' in content_type:
            return response.text
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
