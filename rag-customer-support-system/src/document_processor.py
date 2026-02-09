"""
Document Processor Module
Handles PDF loading, text extraction, and chunking with metadata preservation
"""
import fitz  # PyMuPDF
import os
from typing import List, Dict
import tiktoken

class DocumentProcessor:
    """Process PDF documents for RAG system"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document processor

        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def load_pdf(self, pdf_path: str) -> List[Dict[str, any]]:
        """
        Load PDF and extract text with page numbers

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of dictionaries with page text and metadata
        """
        pages = []
        filename = os.path.basename(pdf_path)

        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()

                if text.strip():  # Only add non-empty pages
                    pages.append({
                        'text': text,
                        'page_number': page_num + 1,
                        'filename': filename
                    })
            doc.close()
            print(f"✓ Loaded {filename}: {len(pages)} pages")
        except Exception as e:
            print(f"✗ Error loading {pdf_path}: {e}")

        return pages

    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Split text into chunks with overlap

        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk

        Returns:
            List of chunks with metadata
        """
        tokens = self.encoding.encode(text)
        chunks = []

        start = 0
        chunk_id = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)

            chunks.append({
                'text': chunk_text,
                'metadata': {
                    **metadata,
                    'chunk_id': chunk_id,
                    'start_token': start,
                    'end_token': end
                }
            })

            chunk_id += 1
            start += self.chunk_size - self.chunk_overlap

        return chunks

    def process_document(self, pdf_path: str) -> List[Dict]:
        """
        Process entire PDF document into chunks

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of text chunks with metadata
        """
        pages = self.load_pdf(pdf_path)
        all_chunks = []

        for page in pages:
            metadata = {
                'filename': page['filename'],
                'page_number': page['page_number']
            }
            chunks = self.chunk_text(page['text'], metadata)
            all_chunks.extend(chunks)

        return all_chunks

    def process_directory(self, directory: str) -> List[Dict]:
        """
        Process all PDF files in a directory

        Args:
            directory: Path to directory containing PDFs

        Returns:
            List of all chunks from all documents
        """
        all_chunks = []

        if not os.path.exists(directory):
            print(f"✗ Directory not found: {directory}")
            return all_chunks

        pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf')]

        print(f"\nProcessing {len(pdf_files)} PDF files from {directory}...")

        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory, pdf_file)
            chunks = self.process_document(pdf_path)
            all_chunks.extend(chunks)

        print(f"\n✓ Total chunks created: {len(all_chunks)}")
        return all_chunks
