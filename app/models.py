from pydantic import BaseModel, HttpUrl, Field, field_validator


class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: HttpUrl
    candidate_level: str = Field(..., description="Junior, Middle, or Senior")

    @field_validator("candidate_level")
    def validate_candidate_level(cls, v):
        if v not in {"Junior", "Middle", "Senior"}:
            raise ValueError("candidate_level must be one of: Junior, Middle, Senior")
        return v


class ReviewResponse(BaseModel):
    found_files: list[str]
    downsides: str
    rating: str
    comments: str
