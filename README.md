# RAG System with Hybrid Retrieval and MCP Integration

A production-ready Retrieval-Augmented Generation (RAG) system featuring:
- **Hybrid Retrieval**: Combines vector search (ChromaDB) with BM25 for optimal results
- **Multi-Format Ingestion**: Supports PDF, DOCX, PPTX, TXT, MD, CSV, XLSX, and HTML
- **MCP-based Tool Selection**: Uses RAG to dynamically select relevant collections, preventing prompt bloat
- **URL-based Ingestion**: Fetch documents from web sources or local directories
- **Image Processing**: Converts images to searchable text descriptions

## Architecture

```
├── backend/                 # FastAPI backend (port 8000)
│   ├── main.py             # FastAPI app with endpoints
│   ├── ingestion/          # Document processing pipeline
│   ├── retrieval/          # Hybrid retrieval (vector + BM25)
│   ├── mcp/                # MCP server for tool selection
│   ├── config/             # Collections configuration
│   └── models/             # Embedding model wrapper
│
├── frontend/               # Streamlit UI (port 8501)
│   ├── app.py             # Main Streamlit application
│   ├── components/        # Reusable UI components
│   └── api_client.py      # Backend API client
│
├── files/                 # Local document storage
│   ├── technical_docs/
│   ├── customer_support/
│   └── financial_reports/
│
├── data/                  # Document storage
│   ├── raw/              # Uploaded documents
│   ├── processed/        # Processed chunks
│   └── downloaded/       # URL-fetched files
│
└── vector_db/            # ChromaDB storage
```

## Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone and navigate to the repository:**
   ```bash
   cd claude_rag
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

   This will install all dependencies specified in `pyproject.toml`.

3. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate  # On Linux/Mac
   # or
   .venv\Scripts\activate  # On Windows
   ```

## Running the System

### Start the Backend (FastAPI)

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Start the Frontend (Streamlit)

In a new terminal:

```bash
cd frontend
streamlit run app.py --server.port 8501
```

The frontend will be available at:
- **UI**: http://localhost:8501

## Configuration

### Collections Configuration

Edit `backend/config/collections.yaml` to configure collections:

```yaml
collections:
  technical_docs:
    description: "Technical documentation and API references"
    chunk_size: 1000
    chunk_overlap: 200
    embedding_model: "nomic-embed-text-v1.5"
    source_url: ""  # Blank = use local files
    files_directory: "./files/technical_docs"

routing_rules:
  - pattern: "*.pdf"
    collection: "technical_docs"
```

### Source Modes

1. **Local Files**: Leave `source_url` blank to use local `files/` directory
2. **URL-based**: Set `source_url` to fetch documents from web sources

## API Endpoints

### Document Ingestion
```bash
# Upload documents
POST /api/ingest
Content-Type: multipart/form-data

# Fetch from source_url in config
POST /api/ingest/from-config
{
  "collection": "technical_docs",
  "force_refresh": false
}
```

### Search
```bash
POST /api/search
{
  "query": "How do I authenticate?",
  "collection": "technical_docs",  # Optional
  "top_k": 10
}
```

### Collection Management
```bash
# List collections
GET /api/collections

# Get collection statistics
GET /api/collections/{name}/stats

# Refresh collection from source_url
POST /api/collections/{name}/refresh
```

## Features

### Hybrid Retrieval

Combines two retrieval methods:
- **Vector Search**: Semantic similarity using embeddings
- **BM25**: Keyword-based sparse retrieval
- **Fusion**: Reciprocal Rank Fusion (RRF) algorithm

### MCP Tool Selection

Uses RAG over collection descriptions to select the top 3 most relevant collections for each query, preventing prompt bloat when dealing with many collections.

### Multi-Format Support

**Document Types:**
- PDF (with table extraction)
- DOCX, PPTX
- TXT, MD
- CSV, XLSX
- HTML webpages

**Image Handling:**
- Extracts images from documents
- Converts to text descriptions using vision models
- Makes images searchable via BM25 and vector search

### URL-based Ingestion

Two modes:
1. **Manual Upload**: Upload files through UI
2. **URL Fetch**: System fetches from configured `source_url`

## Development

### Project Structure

```
backend/
├── ingestion/
│   ├── parsers.py        # Multi-format document parsers
│   ├── chunking.py       # Text chunking strategies
│   ├── image_handler.py  # Image-to-text conversion
│   ├── html_parser.py    # HTML webpage processing
│   └── fetcher.py        # URL-based document fetching
├── retrieval/
│   ├── vector_store.py   # ChromaDB integration
│   ├── bm25_store.py     # BM25 sparse retrieval
│   └── hybrid.py         # RRF fusion algorithm
├── mcp/
│   ├── mcp_server.py     # MCP protocol implementation
│   └── tool_index.py     # RAG index for tools
└── models/
    └── embeddings.py     # Embedding model wrapper
```

### Implementation Phases

1. **Phase 1**: Basic PDF ingestion + vector retrieval
2. **Phase 2**: Multi-format support + hybrid retrieval
3. **Phase 3**: MCP integration + collection routing
4. **Phase 4**: Image processing + URL ingestion
5. **Phase 5**: Production polish + deployment

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Add docstrings for all public functions
- Keep functions under 50 lines when possible
- Use `pathlib` for file operations
- Write tests for new functionality

## Technology Stack

### Backend
- **FastAPI**: Modern async web framework
- **ChromaDB**: Vector database
- **rank-bm25**: BM25 implementation
- **sentence-transformers**: Embedding generation
- **LangChain**: Text splitting utilities

### Document Processing
- **pypdf, pdfplumber**: PDF parsing
- **python-docx, python-pptx**: Office documents
- **pandas**: Spreadsheet processing
- **beautifulsoup4, trafilatura**: HTML extraction

### Frontend
- **Streamlit**: Web UI framework
- **requests**: HTTP client

### Embeddings
- **Default Model**: nomic-embed-text-v1.5
  - 768 dimensions
  - SOTA for retrieval
  - Long context (8192 tokens)

## Testing

```bash
# Run tests (when implemented)
pytest tests/

# Check code style
ruff check .

# Format code
ruff format .
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify dependencies are installed: `uv sync`
- Check Python version: `python --version` (should be 3.10+)

### Frontend won't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`

### Slow ingestion
- Large PDFs with images take time to process
- Consider using background job processing (Celery)

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]

## Support

For issues and questions:
- Check documentation in `RAG_PROJECT_INSTRUCTIONS.md`
- Review API docs at http://localhost:8000/docs
- Open an issue on GitHub
