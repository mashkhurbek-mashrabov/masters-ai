"""
Vector Store Module
Handles ChromaDB operations for document storage and retrieval
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import os

class VectorStore:
    """Manage vector database for document retrieval"""

    def __init__(self, persist_directory: str = "chroma_db"):
        """
        Initialize vector store

        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = "cybertruck_docs"

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"✓ Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Tesla Cybertruck documentation"}
            )
            print(f"✓ Created new collection: {self.collection_name}")

    def add_documents(self, chunks: List[Dict]) -> None:
        """
        Add document chunks to vector store

        Args:
            chunks: List of text chunks with metadata
        """
        if not chunks:
            print("✗ No chunks to add")
            return

        print(f"\nIndexing {len(chunks)} chunks...")

        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        ids = [f"chunk_{i}" for i in range(len(chunks))]

        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            end_idx = min(i + batch_size, len(chunks))

            self.collection.add(
                embeddings=embeddings[i:end_idx].tolist(),
                documents=texts[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )
            print(f"  Indexed {end_idx}/{len(chunks)} chunks")

        print(f"✓ Successfully indexed all chunks")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search for relevant documents

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant documents with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )

        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })

        return formatted_results

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            'collection_name': self.collection_name,
            'total_chunks': count,
            'persist_directory': self.persist_directory
        }

    def clear_collection(self) -> None:
        """Clear all documents from collection"""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Tesla Cybertruck documentation"}
        )
        print(f"✓ Cleared collection: {self.collection_name}")
