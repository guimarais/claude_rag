"""FastAPI backend for RAG system with hybrid retrieval.

This module provides the main FastAPI application with endpoints for:
- Document ingestion (upload and URL-based)
- Hybrid retrieval (vector + BM25)
- Collection management
- Status monitoring
"""

from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import uuid
import logging

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.ingestion.parsers import parse_pdf, parse_document
from backend.ingestion.chunking import create_chunks_with_metadata
from backend.models.embeddings import EmbeddingModel
from backend.retrieval.vector_store import VectorStore
from backend.config.loader import (
    load_collections_config,
    get_collection_config,
    determine_collection
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="RAG System API",
    description="Production-ready RAG with hybrid retrieval and MCP integration",
    version="0.1.0"
)

# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
logger.info("Initializing embedding model and vector store...")
embedding_model = EmbeddingModel(model_name="nomic-ai/nomic-embed-text-v1.5")
vector_store = VectorStore(persist_directory="./vector_db")

# In-memory job tracking
jobs_db: Dict[str, Dict] = {}

logger.info("Backend initialization complete")


# Request/Response Models
class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    job_id: str
    status: str
    processed_count: int


class SearchRequest(BaseModel):
    """Request model for search queries."""
    query: str
    collection: Optional[str] = None
    top_k: int = 10


class SearchResponse(BaseModel):
    """Response model for search results."""
    answer: str
    sources: List[dict]
    selected_collections: List[str]


class CollectionStats(BaseModel):
    """Statistics for a collection."""
    name: str
    document_count: int
    chunk_count: int
    last_updated: str


# Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "RAG System API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_documents(
    files: List[UploadFile] = File(...),
    collection: Optional[str] = None,
    fetch_from_config: bool = False
):
    """Ingest documents from upload or configured source_url.

    Args:
        files: List of uploaded files (if not using fetch_from_config)
        collection: Target collection name (optional, uses routing rules)
        fetch_from_config: If True, fetch from source_url in collection config

    Returns:
        IngestResponse with job_id, status, and processed count
    """
    # Generate job ID
    job_id = str(uuid.uuid4())

    # Initialize job tracking
    jobs_db[job_id] = {
        "status": "processing",
        "processed_count": 0,
        "total_count": len(files),
        "errors": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    logger.info(f"Starting ingestion job {job_id} with {len(files)} files")

    try:
        processed_count = 0

        # Process each uploaded file
        for upload_file in files:
            try:
                logger.info(f"Processing file: {upload_file.filename}")

                # Determine target collection
                target_collection = determine_collection(upload_file.filename, collection)
                collection_config = get_collection_config(target_collection)

                if not collection_config:
                    raise ValueError(f"Collection '{target_collection}' not found in configuration")

                logger.info(f"Routing {upload_file.filename} to collection: {target_collection}")

                # Save uploaded file to temp location
                temp_dir = Path(tempfile.mkdtemp())
                temp_file = temp_dir / upload_file.filename

                with open(temp_file, "wb") as f:
                    shutil.copyfileobj(upload_file.file, f)

                logger.info(f"Saved to temp file: {temp_file}")

                # Parse document based on file extension
                if upload_file.filename.lower().endswith('.pdf'):
                    parsed_doc = parse_pdf(temp_file)
                else:
                    parsed_doc = parse_document(temp_file)

                # Check parse status
                if parsed_doc['status'] == 'error':
                    error_msg = f"Parse errors: {'; '.join(parsed_doc.get('errors', ['Unknown error']))}"
                    jobs_db[job_id]['errors'].append({
                        'file': upload_file.filename,
                        'error': error_msg
                    })
                    logger.error(f"Failed to parse {upload_file.filename}: {error_msg}")
                    # Clean up and continue
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    continue

                logger.info(f"Successfully parsed {upload_file.filename} with status: {parsed_doc['status']}")

                # Chunk the document
                chunks = create_chunks_with_metadata(
                    parsed_doc,
                    chunk_size=collection_config.get('chunk_size', 1000),
                    chunk_overlap=collection_config.get('chunk_overlap', 200)
                )

                if not chunks:
                    error_msg = "No text content to chunk"
                    jobs_db[job_id]['errors'].append({
                        'file': upload_file.filename,
                        'error': error_msg
                    })
                    logger.warning(f"No chunks created from {upload_file.filename}")
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    continue

                logger.info(f"Created {len(chunks)} chunks from {upload_file.filename}")

                # Extract texts and metadata
                texts = [chunk['text'] for chunk in chunks]
                metadatas = [chunk['metadata'] for chunk in chunks]

                # Generate embeddings
                logger.info(f"Generating embeddings for {len(texts)} chunks...")
                embeddings = embedding_model.encode_documents(texts)

                # Add to vector store
                logger.info(f"Storing chunks in collection: {target_collection}")
                vector_store.add_documents(
                    texts=texts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    collection_name=target_collection
                )

                processed_count += 1
                logger.info(f"Successfully ingested {upload_file.filename}")

                # Clean up temp file
                shutil.rmtree(temp_dir, ignore_errors=True)

            except Exception as e:
                error_msg = str(e)
                jobs_db[job_id]['errors'].append({
                    'file': upload_file.filename,
                    'error': error_msg
                })
                logger.error(f"Error processing {upload_file.filename}: {error_msg}", exc_info=True)

        # Update job status
        jobs_db[job_id]['processed_count'] = processed_count
        jobs_db[job_id]['updated_at'] = datetime.now().isoformat()

        if processed_count == 0:
            jobs_db[job_id]['status'] = 'failed'
        elif jobs_db[job_id]['errors']:
            jobs_db[job_id]['status'] = 'partial'
        else:
            jobs_db[job_id]['status'] = 'completed'

        logger.info(f"Job {job_id} finished with status: {jobs_db[job_id]['status']}, "
                   f"processed {processed_count}/{len(files)} files")

        return IngestResponse(
            job_id=job_id,
            status=jobs_db[job_id]['status'],
            processed_count=processed_count
        )

    except Exception as e:
        logger.error(f"Critical error in ingestion job {job_id}: {str(e)}", exc_info=True)
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['errors'].append({'error': str(e)})
        jobs_db[job_id]['updated_at'] = datetime.now().isoformat()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/api/ingest/from-config", response_model=IngestResponse)
async def ingest_from_config(collection: str, force_refresh: bool = False):
    """Fetch and ingest documents from source_url in collection config.

    Args:
        collection: Collection name to ingest
        force_refresh: If True, re-fetch even if already ingested

    Returns:
        IngestResponse with job_id and status
    """
    # TODO: Implement URL-based ingestion
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.get("/api/collections")
async def list_collections():
    """List all available collections with their configurations.

    Returns:
        List of collection names and descriptions
    """
    # TODO: Load and return collections from config
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Perform hybrid retrieval across collections.

    Uses MCP-based tool selection to choose relevant collections,
    then performs hybrid search (vector + BM25) with RRF fusion.

    Args:
        request: SearchRequest with query and parameters

    Returns:
        SearchResponse with answer, sources, and selected collections
    """
    # TODO: Implement hybrid search with MCP tool selection
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """Check ingestion job status.

    Args:
        job_id: Job identifier from ingest endpoint

    Returns:
        Job status and progress information
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return jobs_db[job_id]


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Remove a document and its chunks from the system.

    Args:
        doc_id: Document identifier

    Returns:
        Success confirmation
    """
    # TODO: Implement document deletion
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.get("/api/collections/{name}/stats", response_model=CollectionStats)
async def get_collection_stats(name: str):
    """Get statistics for a specific collection.

    Args:
        name: Collection name

    Returns:
        CollectionStats with document and chunk counts
    """
    try:
        stats = vector_store.get_collection_stats(name)
        return CollectionStats(
            name=stats['name'],
            document_count=stats['count'],
            chunk_count=stats['count'],  # In our case, chunks are documents
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting stats for collection {name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get collection stats: {str(e)}")


@app.post("/api/collections/{name}/refresh")
async def refresh_collection(name: str):
    """Re-fetch documents from source_url for a collection.

    Args:
        name: Collection name

    Returns:
        Refresh job status
    """
    # TODO: Implement collection refresh
    raise HTTPException(status_code=501, detail="Not implemented yet")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
