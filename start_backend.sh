#!/bin/bash
# Script to launch the FastAPI backend locally
#
# Usage: ./start_backend.sh [PORT]
# Default port: 8000

set -e  # Exit on error

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
DEFAULT_PORT=8000
PORT="${1:-$DEFAULT_PORT}"
HOST="0.0.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  RAG System - Backend Server${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Error: Virtual environment not found at ${VENV_DIR}${NC}"
    echo -e "${YELLOW}Please create a virtual environment first:${NC}"
    echo -e "  uv venv"
    echo -e "  uv pip install -e ."
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source "${VENV_DIR}/bin/activate"

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo -e "${RED}Error: uvicorn not found${NC}"
    echo -e "${YELLOW}Installing uvicorn...${NC}"
    uv pip install uvicorn[standard]
fi

# Change to project directory
cd "$PROJECT_DIR"

# Check if port is already in use
if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Port ${PORT} is already in use${NC}"
    echo -e "${YELLOW}Attempting to kill existing process...${NC}"
    lsof -ti:${PORT} | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Display configuration
echo -e "${GREEN}Starting FastAPI backend...${NC}"
echo -e "  Host: ${HOST}"
echo -e "  Port: ${PORT}"
echo -e "  Project: ${PROJECT_DIR}"
echo ""
echo -e "${YELLOW}API will be available at:${NC}"
echo -e "  ${GREEN}http://localhost:${PORT}${NC}"
echo -e "  ${GREEN}http://localhost:${PORT}/docs${NC} (Swagger UI)"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
echo ""

# Create vector_db directory if it doesn't exist
mkdir -p "${PROJECT_DIR}/vector_db"

# Run uvicorn
exec python3 -m uvicorn backend.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --reload \
    --log-level info
