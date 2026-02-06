import sqlite3
import re
import logging
import requests
from typing import Optional
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ChatWithData.Tools")

DANGEROUS_KEYWORDS = [
    "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE",
    "REPLACE", "RENAME", "GRANT", "REVOKE", "COMMIT", "ROLLBACK",
    "ATTACH", "DETACH", "VACUUM", "REINDEX", "PRAGMA"
]


def is_safe_query(query: str) -> tuple[bool, str]:
    normalized = query.upper().strip()
    normalized = re.sub(r'--.*$', '', normalized, flags=re.MULTILINE)
    normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)

    if not normalized.startswith("SELECT"):
        logger.warning(f"BLOCKED: Query does not start with SELECT: {query[:50]}...")
        return False, "Only SELECT queries are allowed. This query does not start with SELECT."

    for keyword in DANGEROUS_KEYWORDS:
        pattern = rf'\b{keyword}\b'
        if re.search(pattern, normalized):
            logger.warning(f"BLOCKED: Query contains dangerous keyword '{keyword}': {query[:50]}...")
            return False, f"Query contains forbidden keyword: {keyword}. Only read-only SELECT queries are allowed."

    statements = [s.strip() for s in query.split(';') if s.strip()]
    if len(statements) > 1:
        logger.warning(f"BLOCKED: Query contains multiple statements: {query[:50]}...")
        return False, "Multiple SQL statements are not allowed. Please submit one query at a time."

    logger.info(f"APPROVED: Query passed safety check: {query[:50]}...")
    return True, "Query is safe to execute."


def query_database(query: str, db_path: str = "data/ecommerce.db") -> dict:
    logger.info(f"Executing query: {query}")

    is_safe, message = is_safe_query(query)
    if not is_safe:
        logger.error(f"Query rejected: {message}")
        return {
            "success": False,
            "error": message,
            "data": None,
            "columns": None
        }

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        data = cursor.fetchall()

        conn.close()

        logger.info(f"Query successful. Returned {len(data)} rows.")

        max_rows = 100
        if len(data) > max_rows:
            logger.info(f"Truncating results from {len(data)} to {max_rows} rows")
            data = data[:max_rows]
            truncated = True
        else:
            truncated = False

        return {
            "success": True,
            "data": data,
            "columns": columns,
            "row_count": len(data),
            "truncated": truncated
        }

    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "data": None,
            "columns": None
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "data": None,
            "columns": None
        }


def get_database_schema(db_path: str = "data/ecommerce.db") -> dict:
    logger.info("Fetching database schema")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema[table] = [
                {
                    "name": col[1],
                    "type": col[2],
                    "nullable": not col[3],
                    "primary_key": bool(col[5])
                }
                for col in columns
            ]

            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            schema[table] = {
                "columns": schema[table],
                "row_count": row_count
            }

        conn.close()

        logger.info(f"Schema retrieved successfully. Found {len(tables)} tables.")
        return {
            "success": True,
            "schema": schema
        }

    except Exception as e:
        logger.error(f"Error fetching schema: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "schema": None
        }


def create_github_issue(
    title: str,
    body: str,
    repo_owner: str,
    repo_name: str,
    github_token: Optional[str] = None
) -> dict:
    logger.info(f"Creating GitHub issue: {title}")

    token = github_token or os.environ.get("GITHUB_TOKEN")

    if not token:
        logger.warning("No GitHub token provided - returning simulated response")
        return {
            "success": True,
            "simulated": True,
            "message": "Support ticket would be created (GitHub token not configured)",
            "issue": {
                "title": title,
                "body": body,
                "repo": f"{repo_owner}/{repo_name}",
                "url": f"https://github.com/{repo_owner}/{repo_name}/issues/new"
            }
        }

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "title": f"[Support] {title}",
        "body": body,
        "labels": ["support", "user-request"]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            issue_data = response.json()
            logger.info(f"GitHub issue created successfully: {issue_data['html_url']}")
            return {
                "success": True,
                "simulated": False,
                "issue": {
                    "number": issue_data["number"],
                    "title": issue_data["title"],
                    "url": issue_data["html_url"],
                    "state": issue_data["state"]
                }
            }
        else:
            logger.error(f"GitHub API error: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"GitHub API error: {response.status_code}",
                "details": response.text
            }

    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return {
            "success": False,
            "error": f"Request error: {str(e)}"
        }


def get_sample_queries() -> list[dict]:
    return [
        {
            "description": "Total sales revenue",
            "query": "SELECT SUM(total_amount) as total_revenue FROM orders WHERE status = 'delivered'"
        },
        {
            "description": "Top 5 customers by orders",
            "query": "SELECT c.first_name, c.last_name, COUNT(o.order_id) as order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id ORDER BY order_count DESC LIMIT 5"
        },
        {
            "description": "Products by category",
            "query": "SELECT category, COUNT(*) as product_count, AVG(price) as avg_price FROM products GROUP BY category"
        },
        {
            "description": "Monthly order trends",
            "query": "SELECT strftime('%Y-%m', order_date) as month, COUNT(*) as orders, SUM(total_amount) as revenue FROM orders GROUP BY month ORDER BY month DESC LIMIT 12"
        },
        {
            "description": "Order status distribution",
            "query": "SELECT status, COUNT(*) as count FROM orders GROUP BY status"
        }
    ]


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Execute a SQL SELECT query on the e-commerce database. Use this to retrieve data about customers, products, orders, and order items. Only SELECT queries are allowed for security reasons.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL SELECT query to execute. Must be a valid SELECT statement."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_database_schema",
            "description": "Get the database schema including all tables, their columns, data types, and row counts. Use this to understand the database structure before writing queries.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Create a support ticket (GitHub issue) to escalate an issue to human support. Use this when the user explicitly requests human help, when you cannot resolve their issue, or when the query seems to require human intervention.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief title summarizing the support request"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue or request, including any relevant context from the conversation"
                    }
                },
                "required": ["title", "description"]
            }
        }
    }
]


def execute_tool(tool_name: str, arguments: dict, config: dict = None) -> dict:
    config = config or {}
    db_path = config.get("db_path", "data/ecommerce.db")

    logger.info(f"Executing tool: {tool_name} with args: {arguments}")

    if tool_name == "query_database":
        return query_database(arguments.get("query", ""), db_path=db_path)

    elif tool_name == "get_database_schema":
        return get_database_schema(db_path=db_path)

    elif tool_name == "create_support_ticket":
        return create_github_issue(
            title=arguments.get("title", "Support Request"),
            body=arguments.get("description", "No description provided"),
            repo_owner=config.get("github_owner", "owner"),
            repo_name=config.get("github_repo", "repo"),
            github_token=config.get("github_token")
        )

    else:
        logger.error(f"Unknown tool: {tool_name}")
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
