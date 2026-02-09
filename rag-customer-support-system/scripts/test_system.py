"""
Test Script for RAG System
Verify all components are working correctly
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        import config
        from src.document_processor import DocumentProcessor
        from src.vector_store import VectorStore
        from src.ticket_manager import TicketManager
        from src.rag_engine import RAGEngine
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        import config

        # Check required configs
        checks = {
            "OPENAI_API_KEY": config.OPENAI_API_KEY,
            "DATASOURCE_DIR": config.DATASOURCE_DIR,
            "VECTOR_DB_PATH": config.VECTOR_DB_PATH,
            "SYSTEM_PROMPT": config.SYSTEM_PROMPT,
            "FUNCTIONS": config.FUNCTIONS
        }

        for key, value in checks.items():
            if value:
                print(f"  ✓ {key} configured")
            else:
                print(f"  ⚠ {key} not set (may need .env file)")

        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_datasource():
    """Test datasource directory"""
    print("\nTesting datasource...")
    try:
        import config

        if not os.path.exists(config.DATASOURCE_DIR):
            print(f"✗ Datasource directory not found: {config.DATASOURCE_DIR}")
            return False

        pdf_files = [f for f in os.listdir(config.DATASOURCE_DIR) if f.endswith('.pdf')]
        print(f"✓ Found {len(pdf_files)} PDF files:")
        for pdf in pdf_files:
            file_size = os.path.getsize(os.path.join(config.DATASOURCE_DIR, pdf))
            print(f"  - {pdf} ({file_size / 1024 / 1024:.2f} MB)")

        return len(pdf_files) >= 3
    except Exception as e:
        print(f"✗ Datasource error: {e}")
        return False

def test_document_processor():
    """Test document processor"""
    print("\nTesting document processor...")
    try:
        from src.document_processor import DocumentProcessor
        import config

        processor = DocumentProcessor()

        # Test with first PDF
        pdf_files = [f for f in os.listdir(config.DATASOURCE_DIR) if f.endswith('.pdf')]
        if pdf_files:
            test_pdf = os.path.join(config.DATASOURCE_DIR, pdf_files[0])
            chunks = processor.process_document(test_pdf)
            print(f"✓ Processed {pdf_files[0]}: {len(chunks)} chunks created")
            return True
        else:
            print("✗ No PDF files to test")
            return False
    except Exception as e:
        print(f"✗ Document processor error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("RAG System Component Tests")
    print("=" * 60)

    results = {
        "Imports": test_imports(),
        "Configuration": test_config(),
        "Datasource": test_datasource(),
        "Document Processor": test_document_processor()
    }

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✓ All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Create .env file with your API keys (copy from .env.example)")
        print("2. Run: python scripts/index_documents.py")
        print("3. Run: streamlit run app.py")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")

    print("=" * 60)

if __name__ == "__main__":
    main()
