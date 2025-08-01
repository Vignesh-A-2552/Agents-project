from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


class CodeReviewRequest(BaseModel):
    """Request model for code review."""
    code: str = Field(..., description="The code to analyze", min_length=1, max_length=50000)
    language: str = Field(..., description="Programming language (python, javascript)")
    file_type: str = Field(..., description="File extension (py, js)")
    context: Optional[str] = Field(None, description="Additional context about the code")
    
    @validator('language')
    def validate_language(cls, v):
        allowed_languages = ['python', 'javascript']
        if v.lower() not in allowed_languages:
            raise ValueError(f'Language must be one of: {", ".join(allowed_languages)}')
        return v.lower()
    
    @validator('file_type')
    def validate_file_type(cls, v):
        allowed_types = ['py', 'js']
        if v.lower() not in allowed_types:
            raise ValueError(f'File type must be one of: {", ".join(allowed_types)}')
        return v.lower()


class CodeReviewResponse(BaseModel):
    """Response model for code review results."""
    severity_level: str
    requires_human_review: bool
    analysis_complete: bool
    processing_time_seconds: float
    syntax_issues: List[Dict[str, Any]]
    security_vulnerabilities: List[Dict[str, Any]]
    performance_issues: List[Dict[str, Any]]
    style_violations: List[Dict[str, Any]]
    best_practice_violations: List[Dict[str, Any]]
    explanations: List[Dict[str, Any]]
    improvement_suggestions: List[Dict[str, Any]]
    learning_resources: List[str]
    summary: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str = "1.0.0"