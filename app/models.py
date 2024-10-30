from pydantic import BaseModel, HttpUrl

class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: HttpUrl
    candidate_level: str

class ReviewResponse(BaseModel):
    found_files: list[str]
    downsides_comments: list[str]
    rating: float
    conclusion: str
