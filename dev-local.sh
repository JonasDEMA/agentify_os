#!/bin/bash
#
# Local Development Startup Script
# Runs FastAPI services independently for testing and Swagger inspection
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  CPA Agent Platform - Local Development                  ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version | cut -d' ' -f2) found${NC}"

# Check Poetry
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}⚠ Poetry not found. Install with: pip install poetry${NC}"
    echo -e "${YELLOW}  Falling back to pip install...${NC}"
    USE_POETRY=false
else
    echo -e "${GREEN}✓ Poetry found${NC}"
    USE_POETRY=true
fi

# Check Redis
echo ""
echo -e "${BLUE}Checking Redis...${NC}"
if ! redis-cli ping &> /dev/null; then
    echo -e "${YELLOW}⚠ Redis not running. Starting Redis...${NC}"
    if command -v redis-server &> /dev/null; then
        redis-server --daemonize yes
        sleep 2
        if redis-cli ping &> /dev/null; then
            echo -e "${GREEN}✓ Redis started${NC}"
        else
            echo -e "${RED}✗ Failed to start Redis${NC}"
            echo -e "${YELLOW}  You can install Redis with: brew install redis (macOS) or apt-get install redis (Linux)${NC}"
        fi
    else
        echo -e "${RED}✗ Redis not installed${NC}"
        echo -e "${YELLOW}  Install with: brew install redis (macOS) or apt-get install redis (Linux)${NC}"
        echo -e "${YELLOW}  Or use docker: docker run -d -p 6379:6379 redis:7-alpine${NC}"
    fi
else
    echo -e "${GREEN}✓ Redis is running${NC}"
fi

# Install dependencies
echo ""
echo -e "${BLUE}Installing dependencies...${NC}"
if [ "$USE_POETRY" = true ]; then
    poetry install --no-root
    PYTHON_CMD="poetry run python"
else
    pip install -e .
    PYTHON_CMD="python"
fi

# Create data directories
mkdir -p data logs uploads/screenshots
echo -e "${GREEN}✓ Created data directories${NC}"

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo -e "${GREEN}✓ Loaded .env${NC}"
else
    echo -e "${YELLOW}⚠ No .env file found. Using defaults${NC}"
fi

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Available Services                                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${GREEN}1)${NC} Scheduler (Job Orchestration)"
echo -e "     Port: 8000"
echo -e "     Swagger: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "  ${GREEN}2)${NC} Server (Monitoring & Screenshots)"
echo -e "     Port: 8001"
echo -e "     Swagger: ${BLUE}http://localhost:8001/docs${NC}"
echo ""
echo -e "  ${GREEN}3)${NC} Calculation Agent (Test Agent)"
echo -e "     Port: 8002"
echo -e "     Swagger: ${BLUE}http://localhost:8002/docs${NC}"
echo ""
echo -e "  ${GREEN}4)${NC} All Services (parallel)"
echo ""
echo -e "  ${GREEN}0)${NC} Exit"
echo ""

read -p "Select service to run (1-4, 0 to exit): " choice

case $choice in
    1)
        echo -e "\n${GREEN}Starting Scheduler...${NC}"
        echo -e "Swagger UI: ${BLUE}http://localhost:8000/docs${NC}"
        echo -e "Health Check: ${BLUE}http://localhost:8000/health${NC}"
        echo ""
        $PYTHON_CMD -m uvicorn scheduler.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    2)
        echo -e "\n${GREEN}Starting Server...${NC}"
        echo -e "Swagger UI: ${BLUE}http://localhost:8001/docs${NC}"
        echo -e "Health Check: ${BLUE}http://localhost:8001/health${NC}"
        echo ""
        PORT=8001 $PYTHON_CMD -m uvicorn server.main:app --host 0.0.0.0 --port 8001 --reload
        ;;
    3)
        echo -e "\n${GREEN}Starting Calculation Agent...${NC}"
        echo -e "Swagger UI: ${BLUE}http://localhost:8002/docs${NC}"
        echo -e "Health Check: ${BLUE}http://localhost:8002/health${NC}"
        echo ""
        cd platform/agentify/agents/calculation_agent
        pip install -r requirements.txt
        PORT=8002 python main.py
        ;;
    4)
        echo -e "\n${GREEN}Starting all services...${NC}"
        echo ""
        echo -e "${BLUE}Service URLs:${NC}"
        echo -e "  Scheduler:   ${BLUE}http://localhost:8000/docs${NC}"
        echo -e "  Server:      ${BLUE}http://localhost:8001/docs${NC}"
        echo -e "  Calc Agent:  ${BLUE}http://localhost:8002/docs${NC}"
        echo ""
        echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
        echo ""
        
        # Start services in background
        $PYTHON_CMD -m uvicorn scheduler.main:app --host 0.0.0.0 --port 8000 --reload > logs/scheduler.log 2>&1 &
        SCHEDULER_PID=$!
        
        PORT=8001 $PYTHON_CMD -m uvicorn server.main:app --host 0.0.0.0 --port 8001 --reload > logs/server.log 2>&1 &
        SERVER_PID=$!
        
        cd platform/agentify/agents/calculation_agent
        pip install -q -r requirements.txt
        PORT=8002 python main.py > ../../../../logs/calc-agent.log 2>&1 &
        CALC_PID=$!
        cd ../../../..
        
        echo -e "${GREEN}✓ All services started${NC}"
        echo -e "\n${YELLOW}Waiting for services to be ready...${NC}"
        sleep 3
        
        # Show logs
        echo -e "\n${BLUE}Tailing logs (Ctrl+C to stop):${NC}\n"
        tail -f logs/scheduler.log logs/server.log logs/calc-agent.log
        
        # Cleanup on exit
        trap "kill $SCHEDULER_PID $SERVER_PID $CALC_PID 2>/dev/null; echo -e '\n${GREEN}✓ All services stopped${NC}'" EXIT
        ;;
    0)
        echo -e "${GREEN}Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
