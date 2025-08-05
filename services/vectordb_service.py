from pathlib import Path
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from loguru import logger


class VectorDBService:
    def __init__(self):
        self.vector_store_path = Path("vector_store")
        self.vector_store_path.mkdir(exist_ok=True)
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store: Optional[FAISS] = None
        self._load_existing_vector_store()
        
    def _load_existing_vector_store(self):
        """Load existing vector store if it exists."""
        try:
            if (self.vector_store_path / "index.faiss").exists():
                self.vector_store = FAISS.load_local(
                    str(self.vector_store_path), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Loaded existing vector store")
            else:
                logger.info("No existing vector store found")
        except Exception as e:
            logger.error(f"Error loading existing vector store: {e}")
            self.vector_store = None
    
    def save_documents(self, documents: List[Document]) -> bool:
        """Save documents to vector store."""
        try:
            if not documents:
                logger.warning("No documents to save")
                return False
                
            if self.vector_store is None:
                # Create new vector store
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                logger.info(f"Created new vector store with {len(documents)} documents")
            else:
                # Add documents to existing vector store
                new_vector_store = FAISS.from_documents(documents, self.embeddings)
                self.vector_store.merge_from(new_vector_store)
                logger.info(f"Added {len(documents)} documents to existing vector store")
            
            # Save to disk
            self.vector_store.save_local(str(self.vector_store_path))
            logger.success("Vector store saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving documents to vector store: {e}")
            return False
    
    def search_similar_documents(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents based on query."""
        try:
            if self.vector_store is None:
                logger.warning("No vector store available for search")
                return []
            
            # Perform similarity search
            similar_docs = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Found {len(similar_docs)} similar documents for query")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {e}")
            return []
    
    def search_with_scores(self, query: str, k: int = 4) -> List[tuple]:
        """Search for similar documents with similarity scores."""
        try:
            if self.vector_store is None:
                logger.warning("No vector store available for search")
                return []
            
            # Perform similarity search with scores
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"Found {len(results)} similar documents with scores")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents with scores: {e}")
            return []
    
    def get_all_documents(self) -> List[dict]:
        """Get all documents from the vector store with metadata."""
        try:
            if self.vector_store is None:
                logger.warning("No vector store available")
                return []
            
            # Get all documents from the vector store
            all_docs = []
            documents_by_source = {}
            
            # FAISS doesn't have a direct way to get all documents, 
            # so we'll use the docstore if available
            if hasattr(self.vector_store, 'docstore') and hasattr(self.vector_store.docstore, '_dict'):
                for doc_id, doc in self.vector_store.docstore._dict.items():
                    source_file = doc.metadata.get('source_file', 'Unknown')
                    
                    if source_file not in documents_by_source:
                        documents_by_source[source_file] = {
                            'filename': source_file,
                            'chunk_count': 0,
                            'total_characters': 0
                        }
                    
                    documents_by_source[source_file]['chunk_count'] += 1
                    documents_by_source[source_file]['total_characters'] += len(doc.page_content)
            
            all_docs = list(documents_by_source.values())
            logger.info(f"Retrieved {len(all_docs)} unique documents from vector store")
            return all_docs
            
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return []
    
    def delete_documents_by_source(self, source_filename: str) -> bool:
        """Delete all documents with the specified source filename."""
        try:
            if self.vector_store is None:
                logger.warning("No vector store available for deletion")
                return False
            
            # Get all documents except those from the specified source
            remaining_docs = []
            deleted_count = 0
            
            if hasattr(self.vector_store, 'docstore') and hasattr(self.vector_store.docstore, '_dict'):
                for doc_id, doc in self.vector_store.docstore._dict.items():
                    if doc.metadata.get('source_file') != source_filename:
                        remaining_docs.append(doc)
                    else:
                        deleted_count += 1
            
            if deleted_count == 0:
                logger.warning(f"No documents found with source filename: {source_filename}")
                return False
            
            # If no documents remain, clear the vector store
            if not remaining_docs:
                logger.info("No documents remaining, clearing vector store")
                return self.clear_vector_store()
            
            # Rebuild vector store with remaining documents
            logger.info(f"Rebuilding vector store with {len(remaining_docs)} remaining documents")
            self.vector_store = FAISS.from_documents(remaining_docs, self.embeddings)
            
            # Save the updated vector store
            self.vector_store.save_local(str(self.vector_store_path))
            logger.success(f"Successfully deleted {deleted_count} chunks from {source_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents by source {source_filename}: {e}")
            return False

    def get_vector_store_info(self) -> dict:
        """Get information about the current vector store."""
        try:
            if self.vector_store is None:
                return {"status": "empty", "document_count": 0, "total_chunks": 0}
            
            # Count total chunks and unique documents
            total_chunks = 0
            unique_documents = set()
            
            if hasattr(self.vector_store, 'docstore') and hasattr(self.vector_store.docstore, '_dict'):
                for doc_id, doc in self.vector_store.docstore._dict.items():
                    total_chunks += 1
                    source_file = doc.metadata.get('source_file', 'Unknown')
                    unique_documents.add(source_file)
            
            index_info = {
                "status": "active",
                "document_count": len(unique_documents),
                "total_chunks": total_chunks,
                "index_exists": (self.vector_store_path / "index.faiss").exists(),
                "embeddings_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
            
            return index_info
            
        except Exception as e:
            logger.error(f"Error getting vector store info: {e}")
            return {"status": "error", "error": str(e)}
    
    def clear_vector_store(self) -> bool:
        """Clear the vector store and delete files."""
        try:
            # Remove files
            for file_path in self.vector_store_path.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
            
            self.vector_store = None
            logger.info("Vector store cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            return False