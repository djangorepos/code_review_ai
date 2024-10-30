from time import sleep

import httpx
from fastapi import HTTPException
from app.config import settings
import logging

logger = logging.getLogger("CodeReviewAI")
headers = {"Authorization": f"token {settings.GITHUB_TOKEN}"}


def format_repo_url(repo_url):
    # Ensure the URL starts with the correct prefix
    if repo_url.startswith("https://github.com"):
        repo_url = repo_url.replace("github.com", "api.github.com/repos")
        # Remove the '.git' suffix if present
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]  # Remove the last 4 characters (".git")

    return repo_url


async def get_repo_id(github_repo_url):
    # Get id of repository
    repo_url = format_repo_url(str(github_repo_url))
    repo = await fetch_repository(repo_url)
    sleep(5)
    return repo.get("id"), repo_url


async def get_repository_contents(github_repo_url: str):
    repo_data = []
    repo_id, repo_url = await get_repo_id(github_repo_url)
    repo_contents = await fetch_repository(repo_url + "/contents")

    for item in repo_contents:
        await process_item(item, repo_data)

    return repo_data, repo_id


async def fetch_repository(repo_url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(repo_url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()

        except httpx.HTTPStatusError as e:
            # Handle specific HTTP errors
            if e.response.status_code == 403:
                logger.error("GitHub API rate limit exceeded.")
                raise HTTPException(status_code=429, detail="GitHub API rate limit exceeded. Please try again later.")
            elif e.response.status_code == 404:
                logger.error("GitHub repository not found.")
                raise HTTPException(status_code=404, detail="GitHub repository not found. Check the URL.")
            elif e.response.status_code == 401:
                logger.error("Unauthorized access to the GitHub repository.")
                raise HTTPException(status_code=401, detail="Unauthorized access. Check your credentials.")
            elif e.response.status_code == 500:
                logger.error("Internal Server Error from GitHub API.")
                raise HTTPException(status_code=500, detail="Internal Server Error. Please try again later.")
            elif e.response.status_code == 503:
                logger.error("Service Unavailable from GitHub API.")
                raise HTTPException(status_code=503, detail="Service Unavailable. Please try again later.")
            else:
                logger.error(f"GitHub API error (status code {e.response.status_code}): {e.response.text}")
                raise HTTPException(status_code=e.response.status_code, detail="GitHub API error occurred.")

        except httpx.RequestError as e:
            # Handle request errors (e.g., network issues)
            logger.error(f"An error occurred while requesting {repo_url}: {e}")
            raise HTTPException(status_code=500, detail="Network error occurred while trying to reach the GitHub API.")

        except Exception as e:
            # Catch any other unexpected exceptions
            logger.error(f"An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred, {e}")


async def process_item(item, repository_data):
    """Process a single item in the repository contents."""
    try:
        # Validate that required keys are present in the item
        if 'type' not in item or 'path' not in item:
            raise ValueError("Invalid item structure: missing 'type' or 'path'")

        if item['type'] == 'file':
            if 'download_url' not in item:
                raise ValueError(f"Missing 'download_url' for file: {item['path']}")

            file_url = item['download_url']
            content = await fetch_file_contents(file_url)
            repository_data.append({"path": item["path"], "content": content})

        elif item['type'] == 'dir':
            # If the item is a directory, fetch its contents recursively
            if 'url' not in item:
                raise ValueError(f"Missing 'url' for directory: {item['path']}")

            directory_contents = await fetch_repository(item['url'])
            for sub_item in directory_contents:
                repository_data = await process_item(sub_item, repository_data)  # Process each item in the directory

    except ValueError as ve:
        # Handle known value errors (like missing keys)
        print(f"ValueError: {ve}")
    except Exception as e:
        # Handle all other exceptions
        print(f"Error processing {item.get('path', 'unknown')}: {e}")

    return repository_data


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
