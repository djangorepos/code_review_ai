import re

from app.cache import redis_client
from app.services.github_service import get_repository_contents
from app.services.openai_service import analyze_code
from app.models import ReviewRequest, ReviewResponse


async def generate_review(request: ReviewRequest, repo_id: str) -> ReviewResponse:
    repo_contents = await get_repository_contents(request.github_repo_url)
    analysis = await analyze_code(redis_client, repo_id, request.assignment_description, request.candidate_level, str(repo_contents))
    downsides_text, rating_text, conclusion_text = extract_sections(analysis)

    return ReviewResponse(
        found_files=[file['path'] for file in repo_contents],
        downsides=downsides_text,
        rating=rating_text,
        conclusion=conclusion_text
    )


def extract_sections(text):
    downsides_match = re.search(r"### Downsides:\n(.*?)\n###", text, re.DOTALL)
    rating_match = re.search(r"### Rating:\n(.*?)\n###", text, re.DOTALL)
    conclusion_match = re.search(r"### Comments:\n(.*?)(?:\n###|$)", text, re.DOTALL)

    downsides = downsides_match.group(1).strip() if downsides_match else ""
    rating = rating_match.group(1).strip() if rating_match else ""
    conclusion = conclusion_match.group(1).strip() if conclusion_match else ""

    return downsides, rating, conclusion
