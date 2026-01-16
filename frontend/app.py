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
):
    """Upload and ingest documents via backend API.

    Args:
        files: List of uploaded files
        collection: Target collection name
        fetch_from_config: Whether to fetch from source_url
    """
    # TODO: Implement API call to /api/ingest
    pass


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
    # TODO: Implement API call to /api/collections/{name}/stats
    pass


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
                # TODO: Call ingest_documents()
                st.success(f"✅ Ingested {len(uploaded_files)} document(s)")
        else:
            st.warning("Please upload files first")

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
        # TODO: Display collection statistics
        st.info("Collection statistics will appear here")


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
