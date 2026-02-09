#!/bin/bash

# Setup script for RAG Customer Support System

echo "=========================================="
echo "Tesla Cybertruck Support System Setup"
echo "=========================================="

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Create .env file: cp .env.example .env"
echo "3. Edit .env with your API keys"
echo "4. Index documents: python scripts/index_documents.py"
echo "5. Run app: streamlit run app.py"
echo ""
echo "=========================================="
