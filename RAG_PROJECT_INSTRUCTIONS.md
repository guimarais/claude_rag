# RAG System with MCP Integration - Project Instructions

## Project Overview
Build a production-ready RAG system with hybrid retrieval, multi-format document ingestion, and MCP-based tool selection to solve prompt bloat.

## Architecture

```
rag-project/
├── backend/                 # FastAPI backend (port 8000)
│   ├── main.py             # FastAPI app with ingestion endpoint
│   ├── ingestion/          # Document processing pipeline
│   │   ├── parsers.py      # Multi-format document parsers
│   │   ├── chunking.py     # Text chunking strategies
│   │   ├── image_handler.py # Image-to-text/embedding conversion
│   │   ├── html_parser.py  # HTML webpage processing
│   │   └── fetcher.py      # URL-based document fetching
│   ├── retrieval/          # Hybrid retrieval system
│   │   ├── vector_store.py # Vector database (ChromaDB/Qdrant)
│   │   ├── bm25_store.py   # BM25 sparse retrieval
│   │   └── hybrid.py       # Fusion algorithm (RRF/weighted)
│   ├── mcp/                # MCP server for tool selection
│   │   ├── mcp_server.py   # MCP protocol implementation
│   │   └── tool_index.py   # RAG index for MCP tools
│   ├── config/
│   │   └── collections.yaml # Vector store routing config
│   └── models/
│       └── embeddings.py   # Embedding model wrapper
│
├── frontend/               # Streamlit frontend (port 8501)
│   ├── app.py             # Main Streamlit application
│   ├── components/        # UI components
│   └── api_client.py      # Backend API client
│
├── files/                 # Default local files directory
│   ├── technical_docs/    # Files for specific collections
│   ├── customer_support/
│   └── financial_reports/
│
├── mcp_servers/           # Custom MCP servers (optional)
├── data/                  # Document storage
│   ├── raw/              # Uploaded documents
│   ├── processed/        # Processed chunks
│   └── downloaded/       # Files fetched from URLs
├── vector_db/            # Vector database storage
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Core Requirements

### 1. Backend (FastAPI - Port 8000)

#### Ingestion Endpoint
```python
POST /api/ingest
- Accepts: multipart/form-data with files
- Parameters:
  - files: List[UploadFile]
  - collection: str (optional, defaults from config)
  - metadata: dict (optional)
- Returns: {job_id, status, processed_count}
```

**Supported Formats:**
- Documents: PDF, DOCX, PPTX, TXT, MD, CSV, XLSX, HTML
- Use well-documented libraries:
  - PDF: `pypdf`, `pdfplumber` (for tables)
  - DOCX: `python-docx`
  - PPTX: `python-pptx`
  - CSV/XLSX: `pandas`
  - Markdown: `markdown` or built-in parsing
  - HTML: `beautifulsoup4` (with `html5lib` parser) or `trafilatura` (for article extraction)

#### HTML Webpage Processing
**Two ingestion modes:**

1. **Direct Upload**: User uploads `.html` files
2. **URL-based Download**: System fetches from `source_url` in config

```python
# HTML Parser Implementation
import trafilatura
from bs4 import BeautifulSoup

def parse_html(html_content: str, url: str = None) -> dict:
    """Extract clean text from HTML webpage.
    
    Returns:
        dict with 'text', 'title', 'metadata'
    """
    # Option 1: trafilatura (best for articles/blogs)
    text = trafilatura.extract(
        html_content,
        include_comments=False,
        include_tables=True,
        include_images=False,  # We handle images separately
    )
    
    # Option 2: BeautifulSoup (for structured pages)
    if not text:
        soup = BeautifulSoup(html_content, 'html5lib')
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside']):
            element.decompose()
        text = soup.get_text(separator='\n', strip=True)
    
    # Extract metadata
    soup = BeautifulSoup(html_content, 'html5lib')
    title = soup.find('title').text if soup.find('title') else 'Untitled'
    
    # Extract images for processing
    images = []
    for img in soup.find_all('img'):
        if img.get('src'):
            images.append({
                'src': img['src'],
                'alt': img.get('alt', ''),
                'context': img.parent.get_text()[:200]  # Surrounding text
            })
    
    return {
        'text': text,
        'title': title,
        'url': url,
        'images': images,
        'metadata': {
            'source_type': 'html',
            'url': url,
            'title': title,
        }
    }
```

#### URL-based Document Fetching
```python
# backend/ingestion/fetcher.py
import httpx
from pathlib import Path

async def fetch_from_url(source_url: str, collection_config: dict) -> List[Path]:
    """Fetch documents from source_url or local files directory.
    
    Args:
        source_url: URL from collection config (blank = use files dir)
        collection_config: Collection configuration
    
    Returns:
        List of file paths to process
    """
    if not source_url or source_url.strip() == "":
        # Use local files directory
        files_dir = Path(collection_config.get('files_directory', './files'))
        return list(files_dir.glob('**/*'))
    
    # Fetch from URL
    async with httpx.AsyncClient() as client:
        if source_url.endswith('.html'):
            # Single HTML page
            response = await client.get(source_url)
            response.raise_for_status()
            return [save_temp_file(response.content, 'page.html')]
        else:
            # Directory listing or sitemap (implement based on site structure)
            # Could use: sitemap.xml parsing, web crawling, etc.
            return await crawl_website(source_url, client)

# Ingestion endpoint update
@app.post("/api/ingest")
async def ingest_documents(
    files: List[UploadFile] = File(None),
    collection: str = None,
    fetch_from_config: bool = False  # New parameter
):
    """Ingest documents from upload or configured source_url."""
    
    if fetch_from_config:
        # Fetch from source_url in collection config
        config = load_collection_config(collection)
        file_paths = await fetch_from_url(
            config.get('source_url', ''),
            config
        )
    else:
        # Process uploaded files
        file_paths = [save_upload(f) for f in files]
    
    # Process all files
    job_id = process_documents(file_paths, collection)
    return {"job_id": job_id, "status": "processing"}
```

#### Collection Control File (`config/collections.yaml`)
```yaml
collections:
  technical_docs:
    description: "Technical documentation and API references"
    chunk_size: 1000
    chunk_overlap: 200
    embedding_model: "nomic-embed-text-v1.5"
    source_url: "https://docs.example.com/api/"  # URL to download from (blank = local files dir)
    
  customer_support:
    description: "Customer FAQs and support articles"
    chunk_size: 500
    chunk_overlap: 100
    embedding_model: "nomic-embed-text-v1.5"
    source_url: ""  # Blank = files stored in 'files' directory
    
  financial_reports:
    description: "Financial statements and analysis"
    chunk_size: 1500
    chunk_overlap: 300
    embedding_model: "nomic-embed-text-v1.5"
    source_url: "https://investor.example.com/reports/"
    
  web_articles:
    description: "Web articles and blog posts"
    chunk_size: 800
    chunk_overlap: 150
    embedding_model: "nomic-embed-text-v1.5"
    source_url: "https://blog.example.com/"

routing_rules:
  - pattern: "*.pdf"
    collection: "technical_docs"
  - pattern: "FAQ_*.docx"
    collection: "customer_support"
  - pattern: "*_financial_*.xlsx"
    collection: "financial_reports"
  - pattern: "*.html"
    collection: "web_articles"

# Default source location when source_url is blank
default_files_directory: "./files"
```

#### Hybrid Retrieval System
**Components:**
1. **Vector Search**: Dense embeddings using ChromaDB or Qdrant
2. **BM25 Search**: Sparse keyword-based retrieval using `rank-bm25`
3. **Fusion**: Reciprocal Rank Fusion (RRF) algorithm

```python
# Pseudo-code structure
def hybrid_search(query: str, collection: str, top_k: int = 10):
    # 1. Vector search
    vector_results = vector_store.search(query, top_k=20)
    
    # 2. BM25 search
    bm25_results = bm25_store.search(query, top_k=20)
    
    # 3. Fusion (RRF)
    fused_results = reciprocal_rank_fusion(
        vector_results, 
        bm25_results, 
        k=60
    )
    
    return fused_results[:top_k]
```

#### Image Handling in Documents
**Decision: Use text descriptions (not raw embeddings)**

**Rationale:**
- Hybrid retrieval combines dense vectors + BM25 (keyword search)
- BM25 requires text → image descriptions enable keyword matching
- Text descriptions integrate naturally into chunking pipeline
- More interpretable results for users

**Implementation:**
```python
# Use vision-language model for image-to-text
# Options (in order of recommendation):
# 1. GPT-4 Vision API (best quality)
# 2. LLaVA (open-source, good quality)
# 3. BLIP-2 (lightweight, decent quality)

def process_image(image_bytes: bytes, context: str) -> str:
    """Convert image to detailed text description."""
    prompt = f"""Describe this image in detail for a RAG system.
    Context: {context}
    Focus on: key information, text content, data/charts, relevant details."""
    
    description = vision_model.generate(image_bytes, prompt)
    return f"[IMAGE: {description}]"

# Embed descriptions into document chunks:
chunk_text = f"{paragraph_text}\n\n{image_description}\n\n{next_paragraph}"
```

### 2. MCP Integration for Tool Selection

**Problem**: With many vector collections, listing all in the LLM prompt causes bloat.

**Solution**: RAG-MCP architecture
```python
# mcp/tool_index.py
class MCPToolIndex:
    """Index MCP tool/collection descriptions for semantic search."""
    
    def __init__(self):
        self.tools = self.load_collections()
        self.embeddings = self.embed_descriptions()
        
    def select_tools(self, query: str, top_k: int = 3) -> List[str]:
        """Use RAG to select most relevant collections."""
        query_embedding = embed(query)
        similar_tools = vector_search(query_embedding, self.embeddings)
        return [tool.name for tool in similar_tools[:top_k]]

# Usage in retrieval
def smart_retrieval(query: str):
    # 1. Use RAG to select relevant collections
    relevant_collections = mcp_tool_index.select_tools(query, top_k=3)
    
    # 2. Search only selected collections
    results = []
    for collection in relevant_collections:
        results.extend(hybrid_search(query, collection))
    
    return fuse_and_rank(results)
```

### 3. Frontend (Streamlit - Port 8501)

**Features:**
- Document upload interface with drag-and-drop
- Collection selection/auto-routing display
- Query interface with streaming responses
- Source citation display with metadata
- Collection management UI

```python
# frontend/app.py structure
import streamlit as st

st.title("RAG System")

# Sidebar: Document upload
with st.sidebar:
    uploaded_files = st.file_uploader("Upload documents", accept_multiple_files=True)
    collection = st.selectbox("Collection", get_collections())
    if st.button("Ingest"):
        ingest_documents(uploaded_files, collection)

# Main: Query interface
query = st.text_input("Ask a question")
if query:
    with st.spinner("Searching..."):
        # Show which collections were selected
        selected_collections = get_selected_collections(query)
        st.info(f"Searching in: {', '.join(selected_collections)}")
        
        # Retrieve and display results
        response = search(query)
        st.write(response.answer)
        
        # Show sources
        with st.expander("Sources"):
            for source in response.sources:
                st.markdown(f"**{source.title}** (Score: {source.score})")
                st.text(source.content)
```

## Technical Stack Recommendations

### Core Dependencies
```txt
# Backend
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
httpx==0.25.2  # For URL-based document fetching

# Document Processing
pypdf==3.17.0
pdfplumber==0.10.3
python-docx==1.1.0
python-pptx==0.6.23
pandas==2.1.3
openpyxl==3.1.2
markdown==3.5.1
beautifulsoup4==4.12.2
html5lib==1.1
trafilatura==1.6.2  # Advanced HTML extraction
lxml==4.9.3  # XML/HTML parser

# Retrieval
chromadb==0.4.18  # or qdrant-client==1.7.0
rank-bm25==0.2.2
sentence-transformers==2.2.2

# Image Processing
Pillow==10.1.0
transformers==4.35.2  # For BLIP-2 or LLaVA

# MCP
mcp==0.1.0  # Anthropic's MCP SDK

# Frontend
streamlit==1.28.1
requests==2.31.0
```

### Embedding Model
**Recommendation: `nomic-embed-text-v1.5`**
- Reason: SOTA for retrieval, 768-dim, permissive license, long context (8192 tokens)
- Alternative: `BAAI/bge-large-en-v1.5` (also excellent)

### Vector Database
**Recommendation: ChromaDB**
- Reason: Easy setup, built-in hybrid search support, persistent storage
- Alternative: Qdrant (better for production scale, requires separate service)

## Implementation Priority

1. **Phase 1: Basic Pipeline**
   - FastAPI ingestion endpoint
   - Single document format (PDF)
   - Simple vector-only retrieval
   - Basic Streamlit UI

2. **Phase 2: Multi-Format + Hybrid**
   - Add all document parsers (including HTML)
   - Implement BM25 indexing
   - Build RRF fusion
   - Add collection routing

3. **Phase 3: Images + MCP**
   - Image-to-text conversion
   - MCP tool indexing
   - Smart collection selection
   - Enhanced UI with source display

4. **Phase 4: URL-based Ingestion**
   - Implement URL fetching from `source_url`
   - Add files directory fallback
   - URL deduplication
   - Refresh endpoint for re-fetching

5. **Phase 5: Production Polish**
   - Error handling and validation
   - Background job processing (Celery)
   - Monitoring and logging
   - Docker deployment

## URL-based Ingestion Modes

### Mode 1: Manual Trigger
User triggers ingestion via API or UI for a specific collection.

```python
# API call
POST /api/ingest/from-config
{
    "collection": "web_articles",
    "force_refresh": false  # Skip if already ingested
}
```

### Mode 2: Scheduled Refresh (Optional)
For collections with `source_url`, schedule periodic re-fetching.

```python
# Using APScheduler or Celery Beat
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=2)  # Daily at 2 AM
async def refresh_web_collections():
    """Refresh all collections with source_url configured."""
    config = load_collections_config()
    
    for collection_name, collection_config in config['collections'].items():
        if collection_config.get('source_url'):
            await ingest_from_url(collection_name)
```

### Mode 3: Webhook-triggered (Advanced)
Accept webhooks when content changes on source websites.

```python
@app.post("/api/webhooks/content-updated")
async def handle_content_update(webhook_data: dict):
    """Handle webhook when source content is updated."""
    collection = webhook_data.get('collection')
    url = webhook_data.get('url')
    
    # Fetch and re-index specific URL
    await fetch_and_ingest_url(url, collection)
```

## Critical Implementation Details

### Chunking Strategy
```python
# Use semantic chunking, not fixed-size
# Recommended: LangChain's RecursiveCharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len,
)
```

### HTML-Specific Considerations
```python
# Handle HTML preprocessing
def preprocess_html_text(text: str) -> str:
    """Clean extracted HTML text."""
    import re
    
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    # Remove navigation artifacts
    text = re.sub(r'(Home|Menu|Navigation|Breadcrumb)[\s\n]+', '', text)
    
    # Preserve structure markers
    text = re.sub(r'(#{1,6})\s+', r'\1 ', text)  # Headers
    
    return text.strip()

# URL normalization for deduplication
def normalize_url(url: str) -> str:
    """Normalize URL to prevent duplicate ingestion."""
    from urllib.parse import urlparse, urlunparse
    
    parsed = urlparse(url)
    # Remove fragments, normalize path
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        parsed.path.rstrip('/'),
        parsed.params,
        parsed.query,
        ''  # Remove fragment
    ))
    return normalized
```

### Metadata Preservation
Store with each chunk:
```python
{
    "text": "chunk content",
    "metadata": {
        "source_file": "document.pdf",  # or URL for HTML
        "source_url": "https://example.com/page.html",  # For web pages
        "page_number": 5,  # For PDFs/DOCX
        "collection": "technical_docs",
        "timestamp": "2026-01-15T10:30:00",
        "file_type": "pdf",  # or "html", "docx", etc.
        "chunk_index": 12,
        "total_chunks": 45,
        "title": "Document Title",  # Extracted from doc/HTML
        "last_fetched": "2026-01-15T10:30:00",  # For URL-based sources
    }
}
```

### API Endpoints
```python
# Backend endpoints
POST   /api/ingest                    # Upload documents (multipart/form-data)
POST   /api/ingest/from-config        # Fetch & ingest from source_url in config
GET    /api/collections                # List collections
POST   /api/search                     # Query with hybrid retrieval
GET    /api/status/{job_id}            # Check ingestion status
DELETE /api/documents/{doc_id}        # Remove document
GET    /api/collections/{name}/stats  # Collection statistics
POST   /api/collections/{name}/refresh # Re-fetch from source_url
```

## Questions to Clarify

### Answered Assumptions:
1. **Image Handling**: Using text descriptions (not raw embeddings) for BM25 compatibility
2. **Fusion Algorithm**: Reciprocal Rank Fusion (industry standard)
3. **Embedding Model**: nomic-embed-text-v1.5 (best for retrieval)
4. **Vector DB**: ChromaDB (easiest production setup)

### Still Need Clarification:
1. **Authentication**: Should the API be protected? If yes, JWT/API keys?
2. **File Size Limits**: Maximum document size? (suggest 50MB per file)
3. **Concurrency**: Should ingestion be async/background jobs? (recommend Celery for production)
4. **LLM Integration**: Which LLM for final answer generation? (Claude, GPT-4, or local?)
5. **Deployment**: Docker only, or also K8s manifests?
6. **Monitoring**: Need observability (Prometheus/Grafana)?
7. **URL Fetching**:
   - Should web crawling be recursive (follow links)?
   - Max depth for crawling?
   - Respect robots.txt?
   - Rate limiting for fetches?
8. **Scheduled Refresh**: Should URL-based collections auto-refresh on a schedule?

## Quick Start Command

Once created:
```bash
# Backend
cd backend && uvicorn main:app --port 8000 --reload

# Frontend  
cd frontend && streamlit run app.py --server.port 8501
```

## Success Criteria

- [ ] Ingests all specified document formats (PDF, DOCX, PPTX, TXT, MD, CSV, XLSX, HTML)
- [ ] Routes documents to correct collections via YAML config
- [ ] Fetches documents from `source_url` when configured
- [ ] Falls back to local `files` directory when `source_url` is blank
- [ ] Properly processes HTML webpages with trafilatura/BeautifulSoup
- [ ] Hybrid retrieval combines vector + BM25 search
- [ ] MCP reduces tool selection from N to top-3 collections
- [ ] Images converted to searchable text descriptions
- [ ] Streamlit UI provides smooth user experience
- [ ] Backend runs on port 8000, frontend on 8501
- [ ] Properly cites sources with metadata (including URLs for web pages)
- [ ] Prevents duplicate ingestion of same URLs
