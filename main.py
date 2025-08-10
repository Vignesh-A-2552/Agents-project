import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.config.settings import settings
from app.config.container import Container
from app.api.routers import auth, review, conversation


# Initialize dependency injection container
container = Container()

# Wire the container with all modules that use injection
container.wire(modules=[
    "app.routers.auth", 
    "app.routers.review",
    "app.routers.conversation"
])

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

app.include_router(auth.router,prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(review.router,prefix="/api/v1/review", tags=["Code Review"])
app.include_router(conversation.router,prefix="/api/v1/conversation", tags=["Conversation"])

@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info(f"Starting Code Review API server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )