import httpx
import logging
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger("CodeReviewAI")
HEADERS = {"Authorization": f"token {settings.GITHUB_TOKEN}"}
ERROR_MESSAGES = {
    403: ("GitHub API rate limit exceeded.", 429),
    404: ("GitHub repository not found. Check the URL.", 404),
    401: ("Unauthorized access. Check your credentials.", 401),
    500: ("Internal Server Error. Please try again later.", 500),
    503: ("Service Unavailable. Please try again later.", 503),
}


def format_repo_url(repo_url):
    # Ensure the URL starts with the correct prefix
    if repo_url.startswith("https://github.com"):
        repo_url = repo_url.replace("github.com", "api.github.com/repos")
        # Remove the '.git' suffix if present
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]  # Remove the last 4 characters (".git")

    return repo_url


async def get_repository_contents(github_repo_url: str):
    repo_data = []
    repo_url = format_repo_url(str(github_repo_url))
    repo_contents = await fetch_repository(f"{repo_url}/contents")

    for item in repo_contents:
        await process_item(item, repo_data)

    return repo_data


async def get_latest_commit_hash(github_repo_url: str) -> str:
    async with httpx.AsyncClient() as client:
        repo_url = format_repo_url(str(github_repo_url))
        response = await client.get(f"{repo_url}/commits", headers=HEADERS)
        response.raise_for_status()
        commits = response.json()
        return commits[0]['sha']  # Return the latest commit hash with Secure Hash Algorithm


async def fetch_repository(repo_url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(repo_url, headers=HEADERS)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            # Handle specific HTTP errors using the mapping
            status_code = e.response.status_code
            if status_code in ERROR_MESSAGES:
                message, http_status = ERROR_MESSAGES[status_code]
                logger.error(message)
                raise HTTPException(status_code=http_status, detail=message)
            else:
                logger.error(f"GitHub API error (status code {status_code}): {e.response.text}")
                raise HTTPException(status_code=status_code, detail="GitHub API error occurred.")

        except httpx.RequestError as e:
            # Handle request errors (e.g., network issues)
            logger.error(f"Network error occurred while requesting {repo_url}: {e}")
            raise HTTPException(status_code=500, detail="Network error occurred while trying to reach the GitHub API.")

        except Exception as e:
            # Catch any other unexpected exceptions
            logger.error(f"An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


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
        response = await client.get(file_url, headers=HEADERS)
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
