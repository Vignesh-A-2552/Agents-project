from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


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


class LoginRequest(BaseModel):
    """Login request model."""
    username: str = Field(..., description="Username or email", min_length=3, max_length=100)
    password: str = Field(..., description="User password", min_length=6, max_length=100)


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_info: Dict[str, Any] = Field(..., description="User information")


class UserInfo(BaseModel):
    """User information model."""
    user_id: str
    username: str
    email: Optional[str] = None
    role: str = Field(default="user", description="User role")
    created_at: datetime
    last_login: Optional[datetime] = None