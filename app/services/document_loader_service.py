import os
from utils.temp_filename import get_temp_filename
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.vectordb_service import VectorDBService
from loguru import logger


class DocumentLoaderService:
    def __init__(self, vectordb_service: VectorDBService = None):
        self.vectordb_service = vectordb_service or VectorDBService()

    def load_document(self, file: UploadFile) -> bool:
        """Load and process a PDF document into the vector store."""
        temp_file_path = None
        try:
            # Save uploaded file to temporary location
            temp_file_path = get_temp_filename(file)
            
            # Write file content to temp file
            with open(temp_file_path, "wb") as temp_file:
                content = file.file.read()
                temp_file.write(content)
            
            logger.info(f"Processing document: {file.filename}")
            
            # Load data from PDF
            loader = PyPDFLoader(temp_file_path)
            data = loader.load()
            
            if not data:
                logger.warning(f"No content extracted from {file.filename}")
                return False
            
            logger.info(f"Loaded {len(data)} pages from {file.filename}")
            
            # Process and save to vector store
            success = self.process_and_save_vector_store(data, file.filename)
            
            return success
            
        except Exception as e:
            logger.error(f"Error loading document {file.filename}: {e}")
            return False
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.debug(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")

    def process_and_save_vector_store(self, data, filename: str) -> bool:
        """Process documents and save to vector store."""
        try:
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", ".", " "],
                chunk_size=1000,
                chunk_overlap=100
            )
            chunks = text_splitter.split_documents(data)
            
            if not chunks:
                logger.warning(f"No chunks created from {filename}")
                return False
            
            logger.info(f"Created {len(chunks)} chunks from {filename}")
            
            # Add filename metadata to chunks
            for chunk in chunks:
                chunk.metadata["source_file"] = filename
                chunk.metadata["chunk_id"] = f"{filename}_{chunks.index(chunk)}"
            
            # Save to vector store
            success = self.vectordb_service.save_documents(chunks)
            
            if success:
                logger.success(f"Successfully processed and saved {filename} with {len(chunks)} chunks")
            else:
                logger.error(f"Failed to save chunks from {filename} to vector store")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            return False