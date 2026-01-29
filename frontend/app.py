"""Streamlit frontend for RAG system.

This module provides a user-friendly web interface for:
- Document upload with drag-and-drop
- Collection selection and management
- Query interface with streaming responses
- Source citation display with metadata
- Collection statistics and monitoring
"""

import streamlit as st
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add project root to path for imports when running with streamlit
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import the API client
try:
    from frontend.api_client import RAGAPIClient
except ImportError:
    # Fallback for different execution contexts
    from api_client import RAGAPIClient

# Initialize API client
api_client = RAGAPIClient(base_url="http://localhost:8000")


# Page configuration
st.set_page_config(
    page_title="RAG System",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 RAG System")
st.markdown("Production-ready RAG with hybrid retrieval and MCP integration")


def get_collections() -> List[str]:
    """Fetch available collections from backend API.

    Returns:
        List of collection names
    """
    # TODO: Implement API call to /api/collections
    pass


def ingest_documents(
    files: List,
    collection: str,
    fetch_from_config: bool = False
) -> Dict[str, Any]:
    """Upload and ingest documents via backend API.

    Args:
        files: List of uploaded files
        collection: Target collection name
        fetch_from_config: Whether to fetch from source_url

    Returns:
        Ingestion response from API
    """
    return api_client.ingest_documents(
        files=files,
        collection=collection,
        fetch_from_config=fetch_from_config
    )


def search_query(query: str, collection: str = None) -> Dict[str, Any]:
    """Perform search query via backend API.

    Args:
        query: Search query text
        collection: Optional collection to search

    Returns:
        Search response with answer and sources
    """
    # TODO: Implement API call to /api/search
    pass


def get_collection_stats(collection: str) -> Dict[str, Any]:
    """Get statistics for a collection.

    Args:
        collection: Collection name

    Returns:
        Statistics dictionary
    """
    return api_client.get_collection_stats(collection)


# Sidebar: Document upload and collection management
with st.sidebar:
    st.header("📄 Document Upload")

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload documents",
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, PPTX, TXT, MD, CSV, XLSX, HTML"
    )

    # Collection selection
    collection = st.selectbox(
        "Target Collection",
        options=["Auto-route"] + ["technical_docs", "customer_support",
                                   "financial_reports", "web_articles"],
        help="Select collection or use auto-routing based on file type"
    )

    # Ingest button
    if st.button("📥 Ingest Documents", type="primary"):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                result = ingest_documents(
                    files=uploaded_files,
                    collection=collection if collection != "Auto-route" else None
                )

                # Display results
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                elif result.get("status") == "completed":
                    st.success(f"✅ Successfully ingested {result['processed_count']} document(s)")
                    st.info(f"📋 Job ID: `{result.get('job_id', 'N/A')}`")

                    # Show any errors if partial success
                    if result.get("errors"):
                        with st.expander("⚠️ Warnings", expanded=False):
                            for error in result["errors"]:
                                st.warning(f"File: {error.get('file', 'unknown')} - {error.get('error', 'unknown error')}")
                elif result.get("status") == "partial":
                    st.warning(f"⚠️ Partially ingested {result['processed_count']} document(s)")
                    st.info(f"📋 Job ID: `{result.get('job_id', 'N/A')}`")

                    if result.get("errors"):
                        with st.expander("❌ Errors", expanded=True):
                            for error in result["errors"]:
                                st.error(f"File: {error.get('file', 'unknown')} - {error.get('error', 'unknown error')}")
                else:
                    st.error(f"❌ Ingestion failed: {result.get('status', 'unknown status')}")
        else:
            st.warning("⚠️ Please upload files first")

    st.divider()

    # URL-based ingestion
    st.header("🌐 URL Ingestion")
    url_collection = st.selectbox(
        "Collection for URL fetch",
        options=["technical_docs", "customer_support",
                "financial_reports", "web_articles"],
        key="url_collection"
    )

    if st.button("🔄 Fetch from Source URL"):
        with st.spinner(f"Fetching documents for {url_collection}..."):
            # TODO: Call API to fetch from config
            st.success(f"✅ Fetched documents for {url_collection}")

    st.divider()

    # Collection stats
    st.header("📊 Collections")
    if st.button("🔍 View Stats"):
        collections = ["technical_docs", "customer_support", "financial_reports", "web_articles"]

        for coll in collections:
            stats = get_collection_stats(coll)

            if "error" not in stats:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.text(f"📁 {coll}")
                with col2:
                    st.metric("Documents", stats.get("document_count", 0))
            else:
                st.text(f"📁 {coll}: No data")


# Main area: Query interface
st.header("💬 Query Interface")

# Query input
query = st.text_input(
    "Ask a question",
    placeholder="What would you like to know?",
    help="Enter your question and press Enter"
)

# Search button
if query:
    with st.spinner("Searching..."):
        # TODO: Call search_query()

        # Show selected collections (placeholder)
        st.info("📚 Searching in: technical_docs, customer_support")

        # Display answer (placeholder)
        st.markdown("### Answer")
        st.markdown("*Answer will appear here after implementation*")

        # Display sources
        with st.expander("📖 Sources", expanded=True):
            st.markdown("*Source citations will appear here*")

            # Placeholder source
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("**Example Document.pdf**")
                st.text("Sample text excerpt from the document...")
            with col2:
                st.metric("Score", "0.95")


# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <small>RAG System v0.1.0 | Backend: http://localhost:8000 |
    <a href='http://localhost:8000/docs'>API Docs</a></small>
    </div>
    """,
    unsafe_allow_html=True
)
