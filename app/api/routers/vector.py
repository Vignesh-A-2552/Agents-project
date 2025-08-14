from fastapi import APIRouter, Depends, status, HTTPException
from loguru import logger
from app.models.schemas import DocumentListResponse, DeleteDocumentResponse, DocumentInfo
from app.services.vectordb_service import VectorDBService
from app.api.dependencies import get_vectordb_service

router = APIRouter()


@router.get("/documents", status_code = status.HTTP_200_OK, response_model=DocumentListResponse)
def get_all_documents(vectordb_service: VectorDBService=Depends(get_vectordb_service)
):
    """Get a list of all documents available in the vector store."""
    try:
        documents_data = vectordb_service.get_all_documents()

        # Convert to DocumentInfo objects
        documents = [
            DocumentInfo(filename = doc['filename'],
                chunk_count = doc['chunk_count'],
                total_characters=doc['total_characters']
            )
            for doc in documents_data
        ]

        # Calculate totals
        total_documents = len(documents)
        total_chunks = sum(doc.chunk_count for doc in documents)

        response = DocumentListResponse(documents = documents,
            total_documents = total_documents,
            total_chunks=total_chunks
        )

        logger.info(f"Retrieved {total_documents} documents with {total_chunks} total chunks")
        return response

    except Exception as e:
        logger.error(f"Error getting documents list: {e}", exc_info=True)
        raise HTTPException(status_code = 500, detail="Internal server error while retrieving documents")

@router.delete("/documents/{filename}", status_code = status.HTTP_200_OK, response_model=DeleteDocumentResponse)
def delete_document(filename: str,
    vectordb_service: VectorDBService=Depends(get_vectordb_service)
):
    """Delete a specific document from the vector store."""
    try:
        logger.info(f"Attempting to delete document: {filename}")

        # Check if document exists first
        all_documents = vectordb_service.get_all_documents()
        document_exists = any(doc['filename'] == filename for doc in all_documents)

        if not document_exists:
            logger.warning(f"Document not found: {filename}")
            return DeleteDocumentResponse(success = False,
                message = f"Document '{filename}' not found in vector store",
                filename=filename
            )

        # Attempt to delete the document
        success = vectordb_service.delete_documents_by_source(filename)

        if success:
            logger.success(f"Successfully deleted document: {filename}")
            return DeleteDocumentResponse(success = True,
                message = f"Document '{filename}' successfully deleted from vector store",
                filename=filename
            )
        else:
            logger.error(f"Failed to delete document: {filename}")
            return DeleteDocumentResponse(success = False,
                message = f"Failed to delete document '{filename}' from vector store",
                filename=filename
            )

    except Exception as e:
        logger.error(f"Error deleting document {filename}: {e}", exc_info=True)
        raise HTTPException(status_code = 500, detail=f"Internal server error while deleting document '{filename}'")
