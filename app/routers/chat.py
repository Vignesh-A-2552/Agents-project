from fastapi import APIRouter, status, HTTPException, Depends, File, UploadFile
from loguru import logger
from models.schemas import ChatRequest, ChatResponse
from ..dependencies import ( 
    get_chat_service, 
    get_document_loader_service,
    get_vectordb_service
)
from services.chat_service import ChatService
from services.document_loader_service import DocumentLoaderService
from services.vectordb_service import VectorDBService


router = APIRouter(prefix="/api/v1", tags=["Chat"])

@router.post("/query", status_code=status.HTTP_200_OK, response_model=ChatResponse)
def create_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Create a new chat session."""
    try:
        logger.info(f"Processing chat message: {request.message}")
        message = chat_service.ask_question(request.message)
        return ChatResponse(message=message)
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during chat processing")

@router.post("/upload", status_code=status.HTTP_200_OK)
def upload_document(
    file: UploadFile = File(...),
    document_loader_service: DocumentLoaderService = Depends(get_document_loader_service)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

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
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to process document '{file.filename}'"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during document upload")

@router.get("/vector-store/status", status_code=status.HTTP_200_OK)
def get_vector_store_status(
    vectordb_service: VectorDBService = Depends(get_vectordb_service)
):
    """Get the current status of the vector store."""
    try:
        status_info = vectordb_service.get_vector_store_info()
        return status_info
    except Exception as e:
        logger.error(f"Error getting vector store status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while getting vector store status")