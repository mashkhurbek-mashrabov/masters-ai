import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

COMPANY_NAME = os.getenv("COMPANY_NAME", "Tesla Cybertruck Support")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "support@cybertruck-support.com")
COMPANY_PHONE = os.getenv("COMPANY_PHONE", "+1-800-TESLA-CT")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))

DATASOURCE_DIR = "datasource"
VECTOR_DB_PATH = "chroma_db"

SYSTEM_PROMPT = f"""You are a helpful customer support assistant for {COMPANY_NAME}.

Your role is to:
1. Answer questions about Tesla Cybertruck using the provided documentation
2. Always cite your sources with document name and page number
3. If you cannot find the answer in the documentation, suggest creating a support ticket
4. Help users create support tickets when they request it

Company Contact Information:
- Email: {COMPANY_EMAIL}
- Phone: {COMPANY_PHONE}

When answering questions:
- Be accurate and cite sources in format: [Source: filename, Page: X]
- If uncertain, acknowledge it and offer to create a support ticket
- Be friendly and professional
"""

FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Create a support ticket in the issue tracking system when the user requests help that cannot be answered from documentation or when they explicitly ask to create a ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_name": {
                        "type": "string",
                        "description": "The name of the user requesting support"
                    },
                    "user_email": {
                        "type": "string",
                        "description": "The email address of the user"
                    },
                    "title": {
                        "type": "string",
                        "description": "A brief summary/title of the support ticket"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue or request"
                    }
                },
                "required": ["user_name", "user_email", "title", "description"]
            }
        }
    }
]
