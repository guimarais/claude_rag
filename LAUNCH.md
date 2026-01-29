# Launch Scripts Guide

This directory contains convenient bash scripts to launch the RAG system locally.

## Quick Start

### Launch Everything (Recommended)
```bash
./start_all.sh
```
This will open two terminal windows:
- One for the backend (FastAPI)
- One for the frontend (Streamlit)

### Launch Individually

#### Backend Only
```bash
./start_backend.sh [PORT]
```
- Default port: 8000
- API will be available at: http://localhost:8000
- Swagger docs at: http://localhost:8000/docs

Example with custom port:
```bash
./start_backend.sh 8080
```

#### Frontend Only
```bash
./start_frontend.sh [PORT]
```
- Default port: 8501
- UI will be available at: http://localhost:8501
- Note: Backend must be running first

Example with custom port:
```bash
./start_frontend.sh 8502
```

## What the Scripts Do

### start_backend.sh
1. Checks if virtual environment exists
2. Activates the virtual environment
3. Verifies uvicorn is installed
4. Kills any existing process on the port
5. Creates vector_db directory if needed
6. Launches FastAPI with hot-reload enabled

### start_frontend.sh
1. Checks if virtual environment exists
2. Activates the virtual environment
3. Verifies streamlit is installed
4. Checks if backend is running (optional)
5. Kills any existing process on the port
6. Launches Streamlit UI

### start_all.sh
1. Launches backend in a new terminal window
2. Waits 3 seconds for backend to initialize
3. Launches frontend in a new terminal window
4. Displays access URLs

## Troubleshooting

### "Virtual environment not found"
```bash
# Create virtual environment
uv venv

# Install dependencies
uv pip install -e .
```

### "Port already in use"
The scripts automatically attempt to kill existing processes. If this fails:
```bash
# Find and kill process manually
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:8501 | xargs kill -9  # Frontend
```

### "Backend API is not running"
When starting the frontend, if the backend isn't running:
1. Start the backend first: `./start_backend.sh`
2. Wait for "Uvicorn running on http://0.0.0.0:8000" message
3. Then start the frontend: `./start_frontend.sh`

### "No supported terminal emulator found"
For `start_all.sh`, you need one of:
- gnome-terminal
- xterm
- konsole
- x-terminal-emulator

If none are available, launch manually in separate terminals:
```bash
# Terminal 1
./start_backend.sh

# Terminal 2
./start_frontend.sh
```

## Manual Launch (Alternative)

If the scripts don't work, you can launch manually:

### Backend
```bash
source .venv/bin/activate
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
source .venv/bin/activate
streamlit run frontend/app.py --server.port 8501
```

## Testing the Backend

After starting the backend, test it with:
```bash
# Test root endpoint
curl http://localhost:8000/

# Upload a PDF
curl -X POST "http://localhost:8000/api/ingest" \
  -F "files=@backend/ingestion/sample_test.pdf"

# Check job status (use job_id from upload response)
curl http://localhost:8000/api/status/YOUR_JOB_ID

# View collection stats
curl http://localhost:8000/api/collections/technical_docs/stats
```

## Environment Variables

You can customize behavior with environment variables:

```bash
# Change log level
export LOG_LEVEL=DEBUG
./start_backend.sh

# Custom host for backend
export BACKEND_HOST=127.0.0.1
./start_backend.sh
```

## Production Deployment

These scripts are for local development only. For production:

### Backend (with Gunicorn)
```bash
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Frontend (with Docker)
```bash
docker run -p 8501:8501 -v $(pwd):/app streamlit-app
```

See `DEPLOYMENT.md` for full production setup instructions.
