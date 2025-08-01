from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, APIRouter, Request, Depends
from loguru import logger
from models.schemas import CodeReviewRequest, CodeReviewResponse
from models.types import CodeReviewState
from services.code_review_service import CodeReviewService
from middleware.auth_middleware import get_optional_user

router = APIRouter(prefix="/api/v1/review", tags=["Code Review"])

# Initialize code review graph (singleton)
code_review_graph = None


async def get_code_review_service():
    """Dependency to get code review service."""
    global code_review_graph
    if code_review_graph is None:
        raise HTTPException(status_code=503, detail="Code review system not initialized")
    return code_review_graph


@router.on_event("startup")
async def initialize_review_system():
    """Initialize the code review system on startup."""
    global code_review_graph
    try:
        logger.info("Initializing Code Review System...")
        service = CodeReviewService()
        code_review_graph = await service.build_agent()
        logger.success("Code Review System initialized successfully!")
    except Exception as e:
        logger.critical(f"Failed to initialize Code Review System: {e}", exc_info=True)
        raise


@router.post("/analyze", response_model=CodeReviewResponse)
async def review_code(
    request: CodeReviewRequest, 
    http_request: Request,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    review_service = Depends(get_code_review_service)
):
    """
    Analyze code for syntax, security, performance, and best practice issues.
    
    - **code**: The source code to analyze
    - **language**: Programming language (python, javascript)
    - **file_type**: File extension (py, js)
    - **context**: Optional context about the code
    
    Authentication is optional but recommended for better tracking.
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    user_info = f"User: {current_user.get('username')}" if current_user else "Anonymous"
    logger.info(f"REQUEST /review/analyze from {client_ip} - {user_info} - Language: {request.language}, Code length: {len(request.code)}")
    
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
        result = await review_service.ainvoke(state)
        
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
                "analyzed_by": current_user.get("username") if current_user else "anonymous"
            }
        )
        
        logger.info(f"RESPONSE /review/analyze: {user_info}, Severity={response.severity_level}, Issues={total_issues}, Processing={processing_time:.3f}s")
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
        "status": "operational" if code_review_graph is not None else "not_initialized",
        "initialized": code_review_graph is not None,
        "supported_languages": ["python", "javascript"],
        "max_code_length": 50000,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"RESPONSE /review/status: System {'operational' if code_review_graph else 'not initialized'}")
    return response