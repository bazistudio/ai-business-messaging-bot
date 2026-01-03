#!/bin/bash

# AI Business Messaging Bot - Deployment Script
# One-click setup for VPS/Render/Railway

set -e

echo "🤖 AI Business Messaging Bot - Setup Script"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python3 --version || { echo -e "${RED}Python3 not found. Please install Python 3.8+${NC}"; exit 1; }

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}Virtual environment activated${NC}"
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    echo -e "${GREEN}Virtual environment activated${NC}"
else
    echo -e "${RED}Failed to activate virtual environment${NC}"
    exit 1
fi

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create database directory
echo -e "${YELLOW}Setting up database...${NC}"
mkdir -p database

# Copy environment file if not exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}Please edit .env file with your configuration${NC}"
    else
        echo -e "${RED}.env.example not found${NC}"
    fi
else
    echo -e "${GREEN}.env file already exists${NC}"
fi

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
python3 -c "
from app.models.message import Base, engine
Base.metadata.create_all(bind=engine)
print('✅ Database initialized')
"

# Start the server
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
echo "3. Start bot: python -m app.main"
echo ""
echo "🌐 Web interface: http://localhost:8000"
echo "📚 API docs: http://localhost:8000/admin/docs"
echo ""
echo "📱 Telegram setup:"
echo "1. Create bot via @BotFather"
echo "2. Get TELEGRAM_BOT_TOKEN"
echo "3. Set TELEGRAM_WEBHOOK_URL in .env"
echo "4. POST to /webhook/telegram/setup"
echo ""
echo -e "${YELLOW}Starting server in 5 seconds...${NC}"
sleep 5

# Run the server
python -m app.main