"""
Indexing Script
Process and index all PDF documents into the vector database
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
import config

def main():
    """Main indexing function"""
    print("=" * 60)
    print("Tesla Cybertruck Documentation Indexing")
    print("=" * 60)

    # Initialize components
    processor = DocumentProcessor(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    vector_store = VectorStore(persist_directory=config.VECTOR_DB_PATH)

    # Check if collection already has data
    stats = vector_store.get_collection_stats()
    if stats['total_chunks'] > 0:
        print(f"\n⚠ Collection already contains {stats['total_chunks']} chunks")
        response = input("Do you want to clear and re-index? (yes/no): ")
        if response.lower() == 'yes':
            vector_store.clear_collection()
        else:
            print("Indexing cancelled.")
            return

    # Process documents
    chunks = processor.process_directory(config.DATASOURCE_DIR)

    if not chunks:
        print("\n✗ No documents found to index")
        return

    # Add to vector store
    vector_store.add_documents(chunks)

    # Print final stats
    final_stats = vector_store.get_collection_stats()
    print("\n" + "=" * 60)
    print("Indexing Complete!")
    print("=" * 60)
    print(f"Collection: {final_stats['collection_name']}")
    print(f"Total chunks: {final_stats['total_chunks']}")
    print(f"Storage location: {final_stats['persist_directory']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
