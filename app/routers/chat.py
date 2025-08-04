from fastapi import APIRouter, status, HTTPException, Depends
from loguru import logger
from models.schemas import ChatRequest, ChatResponse
from ..dependencies import get_chat_service

router = APIRouter(prefix="/api/v1", tags=["Chat"])

@router.post("/chat", status_code=status.HTTP_200_OK, response_model=ChatResponse)
def create_chat(
    request: ChatRequest,
    chat_service = Depends(get_chat_service)
):
    """Create a new chat session."""
    try:
        logger.info(f"Processing chat message: {request.message}")
        message = chat_service.ask_question(request.message)
        return ChatResponse(message=message)
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")
