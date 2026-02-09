# Tesla Cybertruck Customer Support System

A production-ready RAG (Retrieval-Augmented Generation) based customer support chatbot for Tesla Cybertruck documentation. Built with OpenAI GPT-4, ChromaDB, and Streamlit.

## 🚀 Features

- **Intelligent Q&A**: Ask questions about Tesla Cybertruck and get accurate answers from official documentation
- **Source Citations**: Every answer includes document name and page number references
- **Support Tickets**: Create support tickets via GitHub Issues when answers aren't found
- **Conversation History**: Maintains context across multiple questions
- **Function Calling**: Uses OpenAI's function calling for ticket creation
- **Vector Search**: Fast semantic search using ChromaDB and sentence transformers

## 📋 Requirements

- Python 3.9+
- OpenAI API Key
- GitHub Personal Access Token (for ticket creation)
- GitHub Repository (for issue tracking)

## 🛠️ Installation

### Option 1: Docker (Recommended)

The easiest way to run the application:

```bash
# 1. Clone the repository
git clone git@github.com:mashkhurbek-mashrabov/rag-customer-support-system.git
cd rag

# 2. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 3. Build and run with Docker Compose
docker-compose up -d

# 4. Index documents (one-time setup)
docker-compose exec app python scripts/index_documents.py

# 5. Access the app at http://localhost:8501
```

### Option 2: Local Installation

### 1. Clone the Repository

```bash
git clone git@github.com:mashkhurbek-mashrabov/rag-customer-support-system.git
cd rag
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key
GITHUB_TOKEN=ghp_your-actual-github-token
GITHUB_REPO=username/repository-name
```

**Getting API Keys:**

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **GitHub Token**: Create at [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
  - Required scope: `repo` (for creating issues)

### 4. Index Documents

Process and index the PDF documents:

```bash
python scripts/index_documents.py
```

This will:
- Extract text from all PDFs in the `datasource/` folder
- Create chunks with metadata (filename, page number)
- Generate embeddings and store in ChromaDB
- Create a persistent vector database in `chroma_db/`

## 🚀 Running the Application

### With Docker

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Locally

Start the Streamlit application:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🐳 Docker Commands

```bash
# Build the image
docker-compose build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f app

# Execute commands in container
docker-compose exec app python scripts/index_documents.py
docker-compose exec app python scripts/test_system.py

# Restart the application
docker-compose restart

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

## 📁 Project Structure

```
rag/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration and constants
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── datasource/                     # PDF documents
│   ├── tesla_cybertruck_owners_manual.pdf
│   ├── cybertruck_offroad_guide.pdf
│   └── Tesla-Cybertruck-Electrek-2021.pdf
├── src/                            # Source code
│   ├── document_processor.py      # PDF processing and chunking
│   ├── vector_store.py            # ChromaDB integration
│   ├── ticket_manager.py          # GitHub Issues API
│   └── rag_engine.py              # Main RAG logic
├── scripts/                        # Utility scripts
│   └── index_documents.py         # Document indexing script
└── chroma_db/                      # Vector database (created after indexing)
```

## 🎯 Usage

### Asking Questions

Simply type your question in the chat interface:

- "How do I charge the Cybertruck?"
- "What is the towing capacity?"
- "How do I enable autopilot?"

The system will:
1. Search relevant documentation
2. Generate an answer with GPT-4
3. Provide source citations (filename and page number)

### Creating Support Tickets

If the answer isn't in the documentation, you can create a ticket:

1. Ask: "I need help with battery issues"
2. The system will ask for your details
3. Provide: name, email, and description
4. A GitHub Issue will be created automatically

Or explicitly request: "Create a support ticket about [your issue]"

## 🌐 Deploying to HuggingFace Spaces

### 1. Create a New Space

1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Choose:
   - **SDK**: Streamlit
   - **Hardware**: CPU Basic (free tier)

### 2. Push Code to Space

```bash
# Add HuggingFace remote
git remote add hf https://huggingface.co/spaces/mashkhurbek/tesla-cybertruck-support

# Push code
git add .
git commit -m "Initial commit"
git push hf main
```

### 3. Configure Secrets

In your Space settings, add these secrets:

- `OPENAI_API_KEY`: Your OpenAI API key
- `GITHUB_TOKEN`: Your GitHub personal access token
- `GITHUB_REPO`: Your repository name (e.g., `username/repo`)

### 4. Index Documents

After deployment, you'll need to run the indexing script once:

1. Use the HuggingFace Space terminal or
2. Run locally and commit the `chroma_db/` folder (not recommended for large databases)

**Note**: For production, consider using a persistent storage solution or re-indexing on startup.

## 🧪 Testing

Test the system with these example queries:

1. **Basic Question**: "What is the range of the Cybertruck?"
2. **Technical Question**: "How do I perform a software update?"
3. **Ticket Creation**: "Create a support ticket about charging issues"
4. **Follow-up**: Ask related questions to test conversation history

## 📊 Technical Details

### RAG Pipeline

1. **Document Processing**:
   - PDFs loaded with PyMuPDF
   - Text extracted page-by-page
   - Chunked into ~500 tokens with 50 token overlap

2. **Vector Storage**:
   - Embeddings: `all-MiniLM-L6-v2` (384 dimensions)
   - Database: ChromaDB (persistent)
   - Metadata: filename, page number, chunk ID

3. **Retrieval**:
   - Semantic search with top-k=3
   - Results ranked by cosine similarity

4. **Generation**:
   - Model: GPT-4 Turbo
   - Function calling for ticket creation
   - Context window: last 10 messages

### Function Calling

The system uses OpenAI's function calling feature:

```python
{
  "name": "create_support_ticket",
  "parameters": {
    "user_name": "string",
    "user_email": "string",
    "title": "string",
    "description": "string"
  }
}
```

## 🔧 Configuration

Edit `config.py` or `.env` to customize:

- **Model**: Change `OPENAI_MODEL` (default: gpt-4-turbo-preview)
- **Temperature**: Adjust `TEMPERATURE` (default: 0.7)
- **Chunk Size**: Modify `CHUNK_SIZE` (default: 500)
- **Top-K Results**: Change `TOP_K_RESULTS` (default: 3)

## 📝 Data Sources

The system uses 3 PDF documents:

1. **tesla_cybertruck_owners_manual.pdf** (323 pages)
2. **cybertruck_offroad_guide.pdf** (22 pages)
3. **Tesla-Cybertruck-Electrek-2021.pdf** (54 pages)

**Total**: 399 pages of documentation

## 🤝 Contributing

This is a capstone project for Advanced Generative AI course. Feel free to fork and extend!

## 📄 License

MIT License - feel free to use for educational purposes.

## 🙏 Acknowledgments

- OpenAI for GPT-4 and embeddings
- ChromaDB for vector storage
- Streamlit for the UI framework
- Tesla for the Cybertruck documentation

## 📧 Support

For issues or questions:
- Email: support@cybertruck-support.com
- Phone: +1-800-TESLA-CT
- GitHub Issues: Create a ticket in this repository

---

**Built with ❤️ for the Advanced Generative AI Capstone Project**
