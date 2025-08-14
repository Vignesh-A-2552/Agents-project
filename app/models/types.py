from typing import Any, Dict, List, Optional, TypedDict

from typing_extensions import NotRequired, Required


class CodeReviewState(TypedDict):
    code: Required[str]
    language: Required[str]
    file_type: Required[str]
    context: NotRequired[Optional[str]]
    syntax_issues: NotRequired[Optional[List[dict]]]
    security_vulnerabilities: NotRequired[Optional[List[dict]]]
    performance_issues: NotRequired[Optional[List[dict]]]
    style_violations: NotRequired[Optional[List[dict]]]
    best_practice_violations: NotRequired[Optional[List[dict]]]
    explanations: NotRequired[Optional[List[dict]]]
    improvement_suggestions: NotRequired[Optional[List[dict]]]
    learning_resources: NotRequired[Optional[List[str]]]
    severity_level: NotRequired[Optional[str]]
    requires_human_review: NotRequired[bool]
    analysis_complete: NotRequired[bool]
    processing_time: NotRequired[float]


class ConversationState(TypedDict):
    question: Required[str]
    context: NotRequired[str]
    relevant_documents: NotRequired[Optional[List[dict]]]
    enhanced_prompt: NotRequired[str]
    response: NotRequired[str]
    use_rag: NotRequired[bool]
    processing_time: NotRequired[float]
    error: NotRequired[Optional[str]]
