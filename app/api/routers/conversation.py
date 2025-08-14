from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from loguru import logger

from app.api.dependencies import(get_conversation_service,
    get_document_loader_service,
)
from app.models.schemas import ChatRequest, ChatResponse
from app.services.conversation_service import ConversationService
from app.services.document_loader_service import DocumentLoaderService


router = APIRouter()

@router.post("/query", status_code = status.HTTP_200_OK, response_model=ChatResponse)
async def create_chat(request: ChatRequest,
    conversation_service: ConversationService=Depends(get_conversation_service)
):
    """Create a new chat session with enhanced error handling and logging."""
    start_time = datetime.now()

    try:
        logger.info(f"REQUEST /query - Message length: {len(request.message)} characters")

        # Process question using the new structured method
        result = await conversation_service.process_question(request.message, use_rag=True)

        # Calculate total processing time
        total_processing_time = (datetime.now() - start_time).total_seconds()

        if result["success"]:
            logger.info(f"RESPONSE /query - Success: RAG = {result['use_rag']}, Context = {result['context_used']}, Docs = {result['documents_found']}, Time={total_processing_time:.3f}s")
            return ChatResponse(message=result["message"])
        else:
            logger.warning(f"RESPONSE /query - Failed: {result['error']}, Time={total_processing_time:.3f}s")
            # Still return the message even if there was an error, as it contains a user-friendly error message
            return ChatResponse(message=result["message"])
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Error processing chat message: {e}, Time = {processing_time:.3f}s", exc_info=True)
        raise HTTPException(status_code = 500, detail="Internal server error during chat processing")

@router.post("/upload", status_code=status.HTTP_200_OK)
def upload_document(file: UploadFile=File(...),
    document_loader_service: DocumentLoaderService = Depends(get_document_loader_service)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code = 400, detail="Only PDF files are allowed")

    try:
        logger.info(f"Uploading document: {file.filename}")
        success = document_loader_service.load_document(file)

        if success:
            return {
                "message": f"Document '{file.filename}' successfully uploaded and processed",
                "filename": file.filename,
                "status": "success"
            }
        else:
            raise HTTPException(status_code = 500,
                detail=f"Failed to process document '{file.filename}'"
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code = 500, detail="Internal server error during document upload")
