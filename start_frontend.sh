#!/bin/bash
# Script to launch the Streamlit frontend locally
#
# Usage: ./start_frontend.sh [PORT]
# Default port: 8501

set -e  # Exit on error

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
DEFAULT_PORT=8501
PORT="${1:-$DEFAULT_PORT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  RAG System - Frontend UI${NC}"
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

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo -e "${RED}Error: streamlit not found${NC}"
    echo -e "${YELLOW}Installing streamlit...${NC}"
    uv pip install streamlit
fi

# Change to project directory
cd "$PROJECT_DIR"

# Check if backend is running
BACKEND_PORT=8000
if ! curl -s "http://localhost:${BACKEND_PORT}/" > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Backend API is not running on port ${BACKEND_PORT}${NC}"
    echo -e "${YELLOW}Please start the backend first:${NC}"
    echo -e "  ./start_backend.sh"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if port is already in use
if lsof -Pi :${PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Port ${PORT} is already in use${NC}"
    echo -e "${YELLOW}Attempting to kill existing process...${NC}"
    lsof -ti:${PORT} | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Display configuration
echo -e "${GREEN}Starting Streamlit frontend...${NC}"
echo -e "  Port: ${PORT}"
echo -e "  Project: ${PROJECT_DIR}"
echo ""
echo -e "${YELLOW}Frontend will be available at:${NC}"
echo -e "  ${GREEN}http://localhost:${PORT}${NC}"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
echo ""

# Run streamlit
exec streamlit run frontend/app.py \
    --server.port "${PORT}" \
    --server.address localhost \
    --server.headless true \
    --browser.serverAddress localhost
