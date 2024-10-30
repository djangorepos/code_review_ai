from app.services.github import fetch_repository_contents
from app.services.openai import analyze_code
from app.models import ReviewRequest, ReviewResponse


async def generate_review(request: ReviewRequest) -> ReviewResponse:
    repo_contents = await fetch_repository_contents(request.github_repo_url)
    analysis = await analyze_code(str(repo_contents))

    return ReviewResponse(
        found_files=[file['name'] for file in repo_contents],
        downsides_comments=["Placeholder comment based on analysis"],
        rating=4.5,
        conclusion="Suitable for the candidate level."
    )
