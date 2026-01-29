#!/bin/bash
# Script to launch both backend and frontend in separate terminals
#
# Usage: ./start_all.sh

set -e  # Exit on error

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_SCRIPT="${PROJECT_DIR}/start_backend.sh"
FRONTEND_SCRIPT="${PROJECT_DIR}/start_frontend.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  RAG System - Full Stack Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if scripts exist
if [ ! -f "$BACKEND_SCRIPT" ] || [ ! -f "$FRONTEND_SCRIPT" ]; then
    echo -e "${RED}Error: Startup scripts not found${NC}"
    exit 1
fi

# Make scripts executable
chmod +x "$BACKEND_SCRIPT" "$FRONTEND_SCRIPT"

# Function to launch in new terminal
launch_terminal() {
    local script="$1"
    local title="$2"

    # Try different terminal emulators
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$title" -- bash -c "$script; exec bash"
    elif command -v xterm &> /dev/null; then
        xterm -T "$title" -e "bash -c '$script; exec bash'" &
    elif command -v konsole &> /dev/null; then
        konsole --title "$title" -e bash -c "$script; exec bash" &
    elif command -v x-terminal-emulator &> /dev/null; then
        x-terminal-emulator -e bash -c "$script; exec bash" &
    else
        echo -e "${RED}Error: No supported terminal emulator found${NC}"
        echo -e "${YELLOW}Please run the scripts manually:${NC}"
        echo -e "  Terminal 1: $BACKEND_SCRIPT"
        echo -e "  Terminal 2: $FRONTEND_SCRIPT"
        exit 1
    fi
}

echo -e "${GREEN}Launching backend in new terminal...${NC}"
launch_terminal "$BACKEND_SCRIPT" "RAG System - Backend"
sleep 3

echo -e "${GREEN}Launching frontend in new terminal...${NC}"
launch_terminal "$FRONTEND_SCRIPT" "RAG System - Frontend"
sleep 2

echo ""
echo -e "${GREEN}✓ Both services launched successfully!${NC}"
echo ""
echo -e "${YELLOW}Access the application:${NC}"
echo -e "  Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:    ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  Frontend UI: ${GREEN}http://localhost:8501${NC}"
echo ""
echo -e "${YELLOW}To stop the services:${NC}"
echo -e "  Close the terminal windows or press CTRL+C in each terminal"
echo ""
