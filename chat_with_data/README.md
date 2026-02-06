# Chat with Data - E-Commerce Data Insights App

A conversational AI assistant that helps users explore and analyze e-commerce data through natural language queries. Built with Python, Streamlit, and OpenAI's function calling capabilities.

## 🎯 Features

### Core Functionality
- **Natural Language Queries**: Ask questions about your data in plain English
- **SQL Query Execution**: Agent translates questions into SQL and retrieves results
- **Database Schema Explorer**: View table structures and sample data
- **Support Ticket Creation**: Escalate issues to human support via GitHub Issues

### Business Intelligence Dashboard
- Real-time database statistics (customers, orders, products)
- Revenue metrics and average order value
- Order status distribution (pie chart)
- Revenue by category breakdown (bar chart)
- Sample queries for quick exploration

### Safety Features
- **Read-Only Queries**: Only SELECT statements are allowed
- **Dangerous Operation Blocking**: DELETE, DROP, UPDATE, INSERT, etc. are blocked
- **SQL Injection Prevention**: Input validation and sanitization
- **Multiple Statement Blocking**: Prevents SQL injection via statement chaining

### Logging
- All operations are logged to console
- Tool calls, query execution, and errors are tracked
- Useful for debugging and monitoring

## 📋 Requirements

| Requirement | Details |
|-------------|---------|
| Python | 3.10+ |
| OpenAI API Key | Required |
| GitHub Token | Optional (for support tickets) |
| Docker | Optional (for containerized deployment) |

### Data Requirements
- SQLite database with 500+ rows ✅
- Current dataset: **2,546 total rows**
  - 150 customers
  - 50 products
  - 600 orders
  - 1,746 order items

## 🐳 Docker Installation (Recommended)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/mashkhurbek-mashrabov/chat-with-data.git
cd chat-with-data

# 2. Create environment file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Build and run
docker-compose up --build
```

The app will be available at **http://localhost:8501**

### Docker Commands

| Command | Description |
|---------|-------------|
| `docker-compose up --build` | Build and start the application |
| `docker-compose up -d` | Start in detached mode (background) |
| `docker-compose down` | Stop the application |
| `docker-compose logs -f` | View logs in real-time |
| `docker-compose restart` | Restart the application |

### Using Docker Directly

```bash
# Build
docker build -t chat-with-data .

# Run
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_api_key_here \
  -v $(pwd)/data:/app/data \
  chat-with-data
```

## 🚀 Local Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mashkhurbek-mashrabov/chat-with-data.git
cd chat-with-data
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here

# Optional: For GitHub issue creation
GITHUB_TOKEN=your_github_token_here
```

### 5. Initialize the Database

The database comes pre-populated, but you can regenerate it:

```bash
python -m src.database_setup
```

### 6. Run the Application

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 📸 Usage Examples

### Example 1: Asking About Top Products

**User**: "What are the top 5 best-selling products?"

The agent will:
1. Use `get_database_schema` to understand the table structure
2. Execute a SQL query joining products and order_items
3. Return formatted results with product names and quantities sold

<!-- Add screenshot: screenshots/01_top_products.png -->

### Example 2: Revenue Analysis

**User**: "Show me monthly revenue for the last 6 months"

The agent will:
1. Query the orders table with date grouping
2. Calculate total revenue per month
3. Present the data in a readable format

<!-- Add screenshot: screenshots/02_revenue_analysis.png -->

### Example 3: Customer Insights

**User**: "Which customers from California have placed the most orders?"

The agent will:
1. Filter customers by state
2. Join with orders table
3. Aggregate and sort by order count

<!-- Add screenshot: screenshots/03_customer_insights.png -->

### Example 4: Creating a Support Ticket

**User**: "I need to speak with a human about a billing issue"

The agent will:
1. Recognize the need for human intervention
2. Use the `create_support_ticket` tool
3. Create a GitHub issue with the conversation context

<!-- Add screenshot: screenshots/04_support_ticket.png -->

### Example 5: Safety Feature in Action

**User**: "Delete all orders from last year"

The agent will:
1. Detect the dangerous DELETE operation
2. Block the query execution
3. Explain that only read-only operations are allowed

<!-- Add screenshot: screenshots/05_safety_block.png -->

## 🛠 Architecture

### Project Structure

```
chat_with_data/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose configuration
├── .dockerignore         # Docker build exclusions
├── .env.example          # Environment variables template
├── README.md             # This file
├── data/
│   └── ecommerce.db      # SQLite database
├── src/
│   ├── __init__.py
│   ├── agent.py          # AI agent with OpenAI integration
│   ├── database_setup.py # Database initialization script
│   └── tools.py          # Function calling tools
└── screenshots/          # Usage screenshots
```

### Function Calling Tools

The agent uses **3 tools** (2+ as required):

| Tool | Description |
|------|-------------|
| `query_database` | Executes SQL SELECT queries with safety validation |
| `get_database_schema` | Returns table structures, column types, and row counts |
| `create_support_ticket` | Creates GitHub issues for human escalation |

### Database Schema

```sql
customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    city TEXT,
    state TEXT,
    created_at DATETIME
)

products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL,
    cost REAL,
    stock_quantity INTEGER,
    created_at DATETIME
)

orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER FOREIGN KEY,
    order_date DATETIME,
    status TEXT,
    payment_method TEXT,
    shipping_address TEXT,
    total_amount REAL
)

order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER FOREIGN KEY,
    product_id INTEGER FOREIGN KEY,
    quantity INTEGER,
    unit_price REAL
)
```

## 🔒 Security Features

### SQL Safety Checks

```python
DANGEROUS_KEYWORDS = [
    "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE",
    "INSERT", "UPDATE", "REPLACE", "RENAME", "GRANT",
    "REVOKE", "COMMIT", "ROLLBACK", "ATTACH", "DETACH"
]
```

- Queries must start with `SELECT`
- Dangerous keywords are blocked with word-boundary matching
- Multiple statements are rejected
- Comments are stripped before validation

### Example of Blocked Query

```
User: Run this: DELETE FROM orders; SELECT * FROM customers

Agent: I cannot execute that query. Only SELECT queries are allowed,
and your query contains the forbidden keyword: DELETE.
```

## 🌐 Deployment

### Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Select "Docker" as the SDK
3. Upload the project files
4. Add secrets in Space settings:
   - `OPENAI_API_KEY`
   - `GITHUB_TOKEN` (optional)

### Other Platforms

The Docker image can be deployed to any container platform:
- AWS ECS / Fargate
- Google Cloud Run
- Azure Container Instances
- Heroku (with container stack)

## 📝 Console Logging

The application logs all operations to the console:

```
2024-01-15 10:30:45 - ChatWithData.App - INFO - Application started
2024-01-15 10:30:50 - ChatWithData.App - INFO - User input: What are the top products?
2024-01-15 10:30:51 - ChatWithData.Agent - INFO - Processing tool call: get_database_schema
2024-01-15 10:30:51 - ChatWithData.Tools - INFO - Fetching database schema
2024-01-15 10:30:52 - ChatWithData.Agent - INFO - Processing tool call: query_database
2024-01-15 10:30:52 - ChatWithData.Tools - INFO - APPROVED: Query passed safety check
2024-01-15 10:30:52 - ChatWithData.Tools - INFO - Query successful. Returned 5 rows.
```

## 🤝 Support Ticket Integration

### GitHub Issues

When configured with a GitHub token, the agent can create issues:

1. User requests human support
2. Agent calls `create_support_ticket` tool
3. Issue is created in configured repository
4. User receives confirmation with issue link

### Configuration

In the sidebar, expand "GitHub Settings" and provide:
- Repository Owner (username or org)
- Repository Name
- Personal Access Token (with `repo` scope)

## 📄 License

This project is created for educational purposes as part of a Generative AI course.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/) GPT-4
- Charts by [Plotly](https://plotly.com/)
