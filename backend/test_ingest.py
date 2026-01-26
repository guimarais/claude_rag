"""Test suite for document ingestion endpoint.

This module provides automated tests for the POST /api/ingest endpoint
using httpx and pytest. Tests cover:
- Single PDF upload
- Multiple file upload
- Explicit collection specification
- Job status tracking
- Error handling
"""

import pytest
from httpx import AsyncClient, ASGITransport
from pathlib import Path
import asyncio

from backend.main import app


@pytest.mark.asyncio
async def test_ingest_single_pdf():
    """Test ingesting a single PDF file."""
    pdf_path = Path(__file__).parent / "ingestion" / "sample_test.pdf"

    if not pdf_path.exists():
        pytest.skip(f"Sample PDF not found at {pdf_path}")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open(pdf_path, "rb") as f:
            files = {"files": ("sample_test.pdf", f, "application/pdf")}
            response = await client.post("/api/ingest", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "status" in data
        assert "processed_count" in data
        assert data["processed_count"] == 1
        assert data["status"] in ["completed", "partial"]


@pytest.mark.asyncio
async def test_ingest_with_explicit_collection():
    """Test ingesting with explicitly specified collection."""
    pdf_path = Path(__file__).parent / "ingestion" / "sample_test.pdf"

    if not pdf_path.exists():
        pytest.skip(f"Sample PDF not found at {pdf_path}")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open(pdf_path, "rb") as f:
            files = {"files": ("sample_test.pdf", f, "application/pdf")}
            data = {"collection": "customer_support"}
            response = await client.post("/api/ingest", files=files, data=data)

        assert response.status_code == 200
        result = response.json()
        assert result["processed_count"] == 1


@pytest.mark.asyncio
async def test_job_status_endpoint():
    """Test job status tracking endpoint."""
    pdf_path = Path(__file__).parent / "ingestion" / "sample_test.pdf"

    if not pdf_path.exists():
        pytest.skip(f"Sample PDF not found at {pdf_path}")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First, ingest a file
        with open(pdf_path, "rb") as f:
            files = {"files": ("sample_test.pdf", f, "application/pdf")}
            ingest_response = await client.post("/api/ingest", files=files)

        assert ingest_response.status_code == 200
        job_id = ingest_response.json()["job_id"]

        # Check job status
        status_response = await client.get(f"/api/status/{job_id}")
        assert status_response.status_code == 200

        status_data = status_response.json()
        assert "status" in status_data
        assert "processed_count" in status_data
        assert "total_count" in status_data
        assert "errors" in status_data
        assert "created_at" in status_data
        assert status_data["status"] in ["completed", "partial", "processing"]


@pytest.mark.asyncio
async def test_job_status_not_found():
    """Test job status endpoint with non-existent job ID."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/status/nonexistent-job-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_collection_stats():
    """Test collection statistics endpoint."""
    pdf_path = Path(__file__).parent / "ingestion" / "sample_test.pdf"

    if not pdf_path.exists():
        pytest.skip(f"Sample PDF not found at {pdf_path}")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First, ingest a file
        with open(pdf_path, "rb") as f:
            files = {"files": ("sample_test.pdf", f, "application/pdf")}
            await client.post("/api/ingest", files=files)

        # Check collection stats
        stats_response = await client.get("/api/collections/technical_docs/stats")
        assert stats_response.status_code == 200

        stats_data = stats_response.json()
        assert "name" in stats_data
        assert "document_count" in stats_data
        assert "chunk_count" in stats_data
        assert stats_data["name"] == "technical_docs"
        assert stats_data["document_count"] > 0


@pytest.mark.asyncio
async def test_empty_file_handling():
    """Test handling of empty or invalid files."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Try to upload an empty file
        files = {"files": ("empty.pdf", b"", "application/pdf")}
        response = await client.post("/api/ingest", files=files)

        # Should return 200 but with errors
        assert response.status_code == 200
        data = response.json()
        assert data["processed_count"] == 0
        assert data["status"] in ["failed", "partial"]


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns API information."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data


if __name__ == "__main__":
    # Run tests with pytest
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
