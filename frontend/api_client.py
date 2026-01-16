"""Backend API client for Streamlit frontend.

This module provides a clean interface for communicating with the
FastAPI backend from the Streamlit frontend.
"""

from typing import List, Dict, Any, Optional
import requests


class RAGAPIClient:
    """Client for RAG system backend API.

    Handles all HTTP communication with the FastAPI backend,
    including error handling and response parsing.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client.

        Args:
            base_url: Base URL of backend API
        """
        self.base_url = base_url
        self.session = requests.Session()

    def ingest_documents(
        self,
        files: List,
        collection: Optional[str] = None,
        fetch_from_config: bool = False
    ) -> Dict[str, Any]:
        """Upload and ingest documents.

        Args:
            files: List of file objects to upload
            collection: Target collection name
            fetch_from_config: Whether to fetch from source_url

        Returns:
            Ingestion response with job_id and status
        """
        # TODO: Implement POST request to /api/ingest
        pass

    def ingest_from_config(
        self,
        collection: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger URL-based ingestion from collection config.

        Args:
            collection: Collection name
            force_refresh: Whether to re-fetch already ingested content

        Returns:
            Ingestion response with job_id and status
        """
        # TODO: Implement POST request to /api/ingest/from-config
        pass

    def list_collections(self) -> List[Dict[str, Any]]:
        """Get list of available collections.

        Returns:
            List of collection definitions
        """
        # TODO: Implement GET request to /api/collections
        pass

    def search(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Perform search query.

        Args:
            query: Search query text
            collection: Optional collection to search
            top_k: Number of results to return

        Returns:
            Search response with answer and sources
        """
        # TODO: Implement POST request to /api/search
        pass

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Check status of ingestion job.

        Args:
            job_id: Job identifier

        Returns:
            Job status and progress information
        """
        # TODO: Implement GET request to /api/status/{job_id}
        pass

    def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get statistics for a collection.

        Args:
            collection: Collection name

        Returns:
            Statistics dictionary
        """
        # TODO: Implement GET request to /api/collections/{name}/stats
        pass

    def refresh_collection(self, collection: str) -> Dict[str, Any]:
        """Trigger refresh of collection from source_url.

        Args:
            collection: Collection name

        Returns:
            Refresh job status
        """
        # TODO: Implement POST request to /api/collections/{name}/refresh
        pass

    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document from the system.

        Args:
            doc_id: Document identifier

        Returns:
            Deletion confirmation
        """
        # TODO: Implement DELETE request to /api/documents/{doc_id}
        pass
