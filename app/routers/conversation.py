from datetime import datetime
from fastapi import APIRouter, status, HTTPException, Depends, File, UploadFile
from loguru import logger
from models.schemas import ChatRequest, ChatResponse, DocumentListResponse, DeleteDocumentResponse, DocumentInfo
from ..dependencies import ( 
    get_conversation_service, 
    get_document_loader_service,
    get_vectordb_service
)
from services.conversation_service import ConversationService
from services.document_loader_service import DocumentLoaderService
from services.vectordb_service import VectorDBService


router = APIRouter(prefix="/api/v1", tags=["Conversation"])

@router.post("/query", status_code=status.HTTP_200_OK, response_model=ChatResponse)
async def create_chat(
    request: ChatRequest,
    conversation_service: ConversationService = Depends(get_conversation_service)
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
            logger.info(f"RESPONSE /query - Success: RAG={result['use_rag']}, Context={result['context_used']}, Docs={result['documents_found']}, Time={total_processing_time:.3f}s")
            return ChatResponse(message=result["message"])
        else:
            logger.warning(f"RESPONSE /query - Failed: {result['error']}, Time={total_processing_time:.3f}s")
            # Still return the message even if there was an error, as it contains a user-friendly error message
            return ChatResponse(message=result["message"])
            
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Error processing chat message: {e}, Time={processing_time:.3f}s", exc_info=True)
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


@router.get("/vector-store/documents", status_code=status.HTTP_200_OK, response_model=DocumentListResponse)
def get_all_documents(
    vectordb_service: VectorDBService = Depends(get_vectordb_service)
):
    """Get a list of all documents available in the vector store."""
    try:
        documents_data = vectordb_service.get_all_documents()
        
        # Convert to DocumentInfo objects
        documents = [
            DocumentInfo(
                filename=doc['filename'],
                chunk_count=doc['chunk_count'],
                total_characters=doc['total_characters']
            )
            for doc in documents_data
        ]
        
        # Calculate totals
        total_documents = len(documents)
        total_chunks = sum(doc.chunk_count for doc in documents)
        
        response = DocumentListResponse(
            documents=documents,
            total_documents=total_documents,
            total_chunks=total_chunks
        )
        
        logger.info(f"Retrieved {total_documents} documents with {total_chunks} total chunks")
        return response
        
    except Exception as e:
        logger.error(f"Error getting documents list: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while retrieving documents")


@router.get("/debug/search/{query}", status_code=status.HTTP_200_OK)
def debug_search(
    query: str,
    k: int = 6,
    vectordb_service: VectorDBService = Depends(get_vectordb_service)
):
    """Debug endpoint to test vector search directly."""
    try:
        logger.info(f"DEBUG SEARCH - Query: '{query}', k={k}")
        
        # Get vector store info first
        vector_info = vectordb_service.get_vector_store_info()
        
        # Perform search with scores
        results_with_scores = vectordb_service.search_with_scores(query, k=k)
        
        # Format results for response
        search_results = []
        for i, (doc, score) in enumerate(results_with_scores):
            search_results.append({
                "rank": i + 1,
                "score": float(score),
                "source_file": doc.metadata.get('source_file', 'Unknown'),
                "content_preview": doc.page_content[:200],
                "content_length": len(doc.page_content),
                "metadata": doc.metadata
            })
        
        response = {
            "query": query,
            "vector_store_info": vector_info,
            "results_found": len(results_with_scores),
            "results": search_results
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in debug search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error during debug search: {str(e)}")

@router.delete("/vector-store/documents/{filename}", status_code=status.HTTP_200_OK, response_model=DeleteDocumentResponse)
def delete_document(
    filename: str,
    vectordb_service: VectorDBService = Depends(get_vectordb_service)
):
    """Delete a specific document from the vector store."""
    try:
        logger.info(f"Attempting to delete document: {filename}")
        
        # Check if document exists first
        all_documents = vectordb_service.get_all_documents()
        document_exists = any(doc['filename'] == filename for doc in all_documents)
        
        if not document_exists:
            logger.warning(f"Document not found: {filename}")
            return DeleteDocumentResponse(
                success=False,
                message=f"Document '{filename}' not found in vector store",
                filename=filename
            )
        
        # Attempt to delete the document
        success = vectordb_service.delete_documents_by_source(filename)
        
        if success:
            logger.success(f"Successfully deleted document: {filename}")
            return DeleteDocumentResponse(
                success=True,
                message=f"Document '{filename}' successfully deleted from vector store",
                filename=filename
            )
        else:
            logger.error(f"Failed to delete document: {filename}")
            return DeleteDocumentResponse(
                success=False,
                message=f"Failed to delete document '{filename}' from vector store",
                filename=filename
            )
            
    except Exception as e:
        logger.error(f"Error deleting document {filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error while deleting document '{filename}'")