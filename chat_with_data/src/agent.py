import json
import logging
from typing import Generator, Optional
from openai import OpenAI

from src.tools import TOOL_DEFINITIONS, execute_tool, get_database_schema

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ChatWithData.Agent")


SYSTEM_PROMPT = """You are a helpful data assistant for an e-commerce business. You help users query and understand data from the company's database.

## Your Capabilities:
1. **Query Database**: You can execute SQL SELECT queries to retrieve data about customers, products, orders, and order items.
2. **Explain Schema**: You can show and explain the database structure.
3. **Create Support Tickets**: You can escalate issues to human support by creating GitHub issues.

## Database Overview:
The database contains the following tables:
- **customers**: Customer information (id, name, email, phone, city, state)
- **products**: Product catalog (id, name, category, price, cost, stock)
- **orders**: Order records (id, customer_id, date, status, payment, total)
- **order_items**: Order line items (id, order_id, product_id, quantity, price)

## Safety Guidelines:
- You can ONLY execute SELECT queries (read-only)
- DELETE, UPDATE, INSERT, DROP and other modifying operations are blocked
- If a user asks for data modifications, explain that you can only read data

## When to Create Support Tickets:
- When the user explicitly asks to speak with a human or create a ticket
- When you encounter issues you cannot resolve
- When the user has complaints or complex requests requiring human judgment
- When you suggest it and the user confirms

## Response Guidelines:
- Be concise and helpful
- Format query results in readable tables when appropriate
- Explain what the data means in business terms
- Suggest follow-up queries when relevant
- If you're unsure, use get_database_schema to understand the structure first

Remember: Always use the tools available to you to help the user. Don't make up data - always query the database."""


class DataAgent:

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        config: Optional[dict] = None
    ):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.config = config or {}
        self.conversation_history = []

        logger.info(f"Agent initialized with model: {model}")

        self.conversation_history.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })

    def reset_conversation(self):
        self.conversation_history = [{
            "role": "system",
            "content": SYSTEM_PROMPT
        }]
        logger.info("Conversation history reset")

    def _process_tool_calls(self, tool_calls: list) -> list[dict]:
        results = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            logger.info(f"Processing tool call: {function_name}")
            logger.info(f"Arguments: {json.dumps(arguments, indent=2)}")

            result = execute_tool(function_name, arguments, self.config)

            logger.info(f"Tool result: {json.dumps(result, indent=2)[:500]}...")

            results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": json.dumps(result)
            })

        return results

    def chat(self, user_message: str) -> Generator[str, None, None]:
        logger.info(f"User message: {user_message}")

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            stream=False
        )

        assistant_message = response.choices[0].message

        while assistant_message.tool_calls:
            logger.info(f"Tool calls detected: {len(assistant_message.tool_calls)}")

            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            tool_results = self._process_tool_calls(assistant_message.tool_calls)

            for result in tool_results:
                self.conversation_history.append(result)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                stream=False
            )

            assistant_message = response.choices[0].message

        final_content = assistant_message.content or ""

        self.conversation_history.append({
            "role": "assistant",
            "content": final_content
        })

        logger.info(f"Final response length: {len(final_content)} chars")

        yield final_content

    def chat_sync(self, user_message: str) -> str:
        response_parts = list(self.chat(user_message))
        return "".join(response_parts)

    def get_schema_summary(self) -> dict:
        return get_database_schema(self.config.get("db_path", "data/ecommerce.db"))
