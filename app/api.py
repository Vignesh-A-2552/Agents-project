import traceback
from datetime import datetime
from fastapi import HTTPException, APIRouter, Request
from loguru import logger
from models.schemas import CodeReviewRequest, CodeReviewResponse, HealthResponse
from models.types import CodeReviewState
from services.code_review_service import CodeReviewService
from config.settings import settings

router = APIRouter()


# Initialize code review graph (singleton)
code_review_graph = None


@router.on_event("startup")
async def startup_event():
    """Initialize the code review system on startup."""
    global code_review_graph
    try:
        logger.info("Initializing Code Review System...")
        settings.validate_settings()
        service = CodeReviewService()
        code_review_graph = await service.build_agent()
        logger.success("Code Review System initialized successfully!")
    except Exception as e:
        logger.critical(f"Failed to initialize Code Review System: {e}", exc_info=True)
        raise


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /health from {client_ip}")
    
    response = HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )
    
    logger.info(f"RESPONSE /health: {response.status}")
    return response


@router.post("/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest, http_request: Request):
    """
    Analyze code for syntax, security, performance, and best practice issues.
    
    - **code**: The source code to analyze
    - **language**: Programming language (python, javascript)
    - **file_type**: File extension (py, js)
    - **context**: Optional context about the code
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    logger.info(f"REQUEST /review from {client_ip} - Language: {request.language}, Code length: {len(request.code)}")
    
    if code_review_graph is None:
        logger.error("Code review system not initialized")
        raise HTTPException(status_code=503, detail="Code review system not initialized")
    
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
        result = await code_review_graph.ainvoke(state)
        
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
                "language": request.language
            }
        )
        
        logger.info(f"RESPONSE /review: Severity={response.severity_level}, Issues={total_issues}, Processing={processing_time:.3f}s")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error in /review: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error during code review: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/supported-languages")
async def get_supported_languages(request: Request):
    """Get list of supported programming languages."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /supported-languages from {client_ip}")
    
    response = {
        "languages": [
            {"name": "Python", "code": "python", "file_extensions": ["py"]},
            {"name": "JavaScript", "code": "javascript", "file_extensions": ["js"]}
        ]
    }
    
    logger.info(f"RESPONSE /supported-languages: {len(response['languages'])} languages")
    return response


@router.get("/debug/status")
async def get_debug_status(request: Request):
    """Debug endpoint to check system status and configuration."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /debug/status from {client_ip}")
    
    try:
        debug_info = {
            "system_status": "operational",
            "code_review_system_initialized": code_review_graph is not None,
            "configuration": settings.get_debug_info(),
            "dependencies": {
                "fastapi": check_package("fastapi"),
                "uvicorn": check_package("uvicorn"),
                "pydantic": check_package("pydantic"),
                "langchain": check_package("langchain"),
                "langchain_openai": check_package("langchain_openai"),
                "langgraph": check_package("langgraph"),
                "loguru": check_package("loguru"),
                "python_dotenv": check_package("python_dotenv")
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("RESPONSE /debug/status: System status retrieved")
        return debug_info
        
    except Exception as e:
        logger.error(f"Error getting debug status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Debug status error: {str(e)}")


@router.get("/debug/logs")
async def get_recent_logs(request: Request, lines: int = 50):
    """Debug endpoint to get recent log entries."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /debug/logs from {client_ip}, lines: {lines}")
    
    try:
        from pathlib import Path
        
        log_files = {
            "app_log": Path("logs/app.log"),
            "error_log": Path("logs/error.log"),
            "request_log": Path("logs/requests.log")
        }
        
        logs = {}
        
        for log_name, log_path in log_files.items():
            if log_path.exists():
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        all_lines = f.readlines()
                        logs[log_name] = all_lines[-lines:] if len(all_lines) > lines else all_lines
                except Exception as e:
                    logs[log_name] = [f"Error reading log: {str(e)}"]
            else:
                logs[log_name] = ["Log file not found"]
        
        response = {
            "logs": logs,
            "lines_requested": lines,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"RESPONSE /debug/logs: Retrieved {lines} lines from logs")
        return response
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Log retrieval error: {str(e)}")


def check_package(package_name: str) -> dict:
    """Check if a package is installed and get version info."""
    try:
        import importlib.metadata
        version = importlib.metadata.version(package_name)
        return {"installed": True, "version": version}
    except importlib.metadata.PackageNotFoundError:
        return {"installed": False, "version": None}
    except Exception as e:
        return {"installed": False, "error": str(e)}