from pydantic import BaseModel, HttpUrl, Field


class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: HttpUrl
    candidate_level: str = Field(..., description="Junior, Middle, or Senior")

    @classmethod
    def validate_candidate_level(cls, v):
        if v not in {"Junior", "Middle", "Senior"}:
            raise ValueError("candidate_level must be one of: Junior, Middle, Senior")
        return v


class ReviewResponse(BaseModel):
    found_files: list[str]
    downsides_comments: list[str]
    rating: float
    conclusion: str
