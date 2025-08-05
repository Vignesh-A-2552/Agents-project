from datetime import datetime
from fastapi import HTTPException, APIRouter, Request, Depends
from loguru import logger
from models.schemas import CodeReviewRequest, CodeReviewResponse
from models.types import CodeReviewState
from config.container import Container
from dependency_injector.wiring import inject, Provide
from services.code_review_service import CodeReviewService
from app.dependencies import get_code_review_service

router = APIRouter(prefix="/api/v1/review", tags=["Code Review"])

@router.post("/analyze", response_model=CodeReviewResponse)
async def review_code(
    request: CodeReviewRequest, 
    review_service: CodeReviewService = Depends(get_code_review_service)
):
    """
    Analyze code for syntax, security, performance, and best practice issues.
    
    - **code**: The source code to analyze
    - **language**: Programming language (python, javascript)
    - **file_type**: File extension (py, js)
    - **context**: Optional context about the code
    
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
            return len([x for x in (issues_list or []) if not x.get("error")])
        
        syntax_count = count_valid_issues(result.get("syntax_issues"))
        security_count = count_valid_issues(result.get("security_vulnerabilities"))
        performance_count = count_valid_issues(result.get("performance_issues"))
        style_count = count_valid_issues(result.get("style_violations"))
        best_practice_count = count_valid_issues(result.get("best_practice_violations"))
        total_issues = syntax_count + security_count + performance_count + style_count + best_practice_count
        
        # Create response
        response = CodeReviewResponse(
            severity_level=result.get("severity_level", "unknown"),
            requires_human_review=result.get("requires_human_review", False),
            analysis_complete=result.get("analysis_complete", False),
            processing_time_seconds=processing_time,
            syntax_issues=result.get("syntax_issues", []),
            security_vulnerabilities=result.get("security_vulnerabilities", []),
            performance_issues=result.get("performance_issues", []),
            style_violations=result.get("style_violations", []),
            best_practice_violations=result.get("best_practice_violations", []),
            explanations=result.get("explanations", []),
            improvement_suggestions=result.get("improvement_suggestions", []),
            learning_resources=result.get("learning_resources", []),
            summary={
                "total_issues": total_issues,
                "syntax_issues": syntax_count,
                "security_vulnerabilities": security_count,
                "performance_issues": performance_count,
                "style_violations": style_count,
                "best_practice_violations": best_practice_count,
                "code_length": len(request.code),
                "language": request.language,
                # "analyzed_by": current_user.get("username") if current_user else "anonymous"
            }
        )
        
        # logger.info(f"RESPONSE /review/analyze: {user_info}, Severity={response.severity_level}, Issues={total_issues}, Processing={processing_time:.3f}s")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error in /review/analyze: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during code review: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/supported-languages")
async def get_supported_languages(request: Request):
    """Get list of supported programming languages."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /review/supported-languages from {client_ip}")
    
    response = {
        "languages": [
            {"name": "Python", "code": "python", "file_extensions": ["py"]},
            {"name": "JavaScript", "code": "javascript", "file_extensions": ["js"]}
        ]
    }
    
    logger.info(f"RESPONSE /review/supported-languages: {len(response['languages'])} languages")
    return response


@router.get("/status")
async def get_review_system_status(request: Request):
    """Get code review system status."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /review/status from {client_ip}")
    
    response = {
        "status": "operational",
        "initialized": True,
        "supported_languages": ["python", "javascript"],
        "max_code_length": 50000,
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"RESPONSE /review/status: System {'operational' if response['status'] == 'operational' else 'not initialized'}")
    return response