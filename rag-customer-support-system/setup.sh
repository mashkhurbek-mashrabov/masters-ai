#!/bin/bash

echo "=========================================="
echo "Tesla Cybertruck Support System Setup"
echo "=========================================="
echo ""
echo "Checking Python version..."
python3 --version

echo ""
echo "Creating virtual environment..."
python3 -m venv venv

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Upgrading pip..."
pip install --upgrade pip

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
echo "2. Index documents: python scripts/index_documents.py"
echo "3. Run app: streamlit run app.py"
echo ""
echo "=========================================="
