from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger

from app.api.dependencies import get_code_review_service
from app.models.schemas import CodeReviewRequest, CodeReviewResponse
from app.models.types import CodeReviewState
from app.services.code_review_service import CodeReviewService

router = APIRouter()

@router.post("/analyze", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest,
    review_service: CodeReviewService=Depends(get_code_review_service)
):
    """
    Analyze code for syntax, security, performance, and best practice issues.

    Authentication is optional but recommended for better tracking.
    """

    start_time = datetime.now()

    try:
        # Prepare state
        state: CodeReviewState = {
            "code": request.code,
            "language": request.language,
            "file_type": request.file_type,
            "context": request.context
        }

        # Run analysis
        result = await review_service.analyze_code(state)

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Count issues for summary
        def count_valid_issues(issues_list):
            return len([x for x in(issues_list or []) if not x.get("error")])

        syntax_count = count_valid_issues(result.get("syntax_issues"))
        security_count = count_valid_issues(result.get("security_vulnerabilities"))
        performance_count = count_valid_issues(result.get("performance_issues"))
        style_count = count_valid_issues(result.get("style_violations"))
        best_practice_count = count_valid_issues(result.get("best_practice_violations"))
        total_issues = syntax_count + security_count + performance_count + style_count + best_practice_count

        # Create response
        response = CodeReviewResponse(severity_level=result.get("severity_level", "unknown"),
            requires_human_review = result.get("requires_human_review", False),
            analysis_complete = result.get("analysis_complete", False),
            processing_time_seconds = processing_time,
            syntax_issues = result.get("syntax_issues", []),
            security_vulnerabilities = result.get("security_vulnerabilities", []),
            performance_issues = result.get("performance_issues", []),
            style_violations = result.get("style_violations", []),
            best_practice_violations = result.get("best_practice_violations", []),
            explanations = result.get("explanations", []),
            improvement_suggestions = result.get("improvement_suggestions", []),
            learning_resources = result.get("learning_resources", []),
            summary = {
                "total_issues": total_issues,
                "syntax_issues": syntax_count,
                "security_vulnerabilities": security_count,
                "performance_issues": performance_count,
                "style_violations": style_count,
                "best_practice_violations": best_practice_count,
                "code_length": len(request.code),
                "language": request.language,
            }
        )

        return response
    except ValueError as e:
        logger.warning(f"Validation error in /review/analyze: {e}")
        raise HTTPException(status_code = 400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during code review: {e}", exc_info=True)
        raise HTTPException(status_code = 500, detail=f"Internal server error: {str(e)}")
