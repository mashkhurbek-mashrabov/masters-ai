"""
RAG Engine Module
Core RAG system integrating retrieval, LLM, and function calling
"""
from openai import OpenAI
from typing import List, Dict, Optional
import json
from src.vector_store import VectorStore
from src.ticket_manager import TicketManager
import config

class RAGEngine:
    """Main RAG engine for question answering and ticket creation"""

    def __init__(self):
        """Initialize RAG engine"""
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.vector_store = VectorStore(persist_directory=config.VECTOR_DB_PATH)
        self.ticket_manager = TicketManager(
            github_token=config.GITHUB_TOKEN,
            github_repo=config.GITHUB_REPO
        )
        self.conversation_history = []

    def search_documents(self, query: str) -> List[Dict]:
        """
        Search for relevant documents

        Args:
            query: User query

        Returns:
            List of relevant document chunks
        """
        return self.vector_store.search(query, top_k=config.TOP_K_RESULTS)

    def format_context(self, results: List[Dict]) -> str:
        """
        Format search results into context string

        Args:
            results: Search results from vector store

        Returns:
            Formatted context string with citations
        """
        if not results:
            return "No relevant information found in the documentation."

        context_parts = []
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            text = result['text']

            context_parts.append(
                f"[Source {i}: {metadata['filename']}, Page {metadata['page_number']}]\n{text}\n"
            )

        return "\n".join(context_parts)

    def query(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Process user query with RAG

        Args:
            user_message: User's question or request
            conversation_history: Previous conversation messages

        Returns:
            Dictionary with response and metadata
        """
        # Search for relevant documents
        search_results = self.search_documents(user_message)
        context = self.format_context(search_results)

        # Prepare messages
        messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT}
        ]

        # Add conversation history (last 10 messages)
        if conversation_history:
            messages.extend(conversation_history[-10:])

        # Add current query with context
        user_content = f"""User Question: {user_message}

Relevant Documentation:
{context}

Please answer the question based on the documentation above. Always cite your sources using the format [Source: filename, Page: X]. If the answer is not in the documentation, suggest creating a support ticket."""

        messages.append({"role": "user", "content": user_content})

        # Call OpenAI with function calling
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=messages,
                tools=config.FUNCTIONS,
                tool_choice="auto",
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS
            )

            message = response.choices[0].message

            # Check if function was called
            if message.tool_calls:
                return self._handle_function_call(message, user_message)
            else:
                return {
                    'type': 'answer',
                    'content': message.content,
                    'sources': search_results
                }

        except Exception as e:
            return {
                'type': 'error',
                'content': f"Error processing query: {str(e)}",
                'sources': []
            }

    def _handle_function_call(self, message, user_message: str) -> Dict:
        """
        Handle function calling from LLM

        Args:
            message: OpenAI message with function call
            user_message: Original user message

        Returns:
            Dictionary with function result
        """
        tool_call = message.tool_calls[0]
        function_name = tool_call.function.name

        if function_name == "create_support_ticket":
            try:
                arguments = json.loads(tool_call.function.arguments)

                # Create ticket
                result = self.ticket_manager.create_ticket(
                    user_name=arguments.get('user_name'),
                    user_email=arguments.get('user_email'),
                    title=arguments.get('title'),
                    description=arguments.get('description')
                )

                if result['success']:
                    return {
                        'type': 'ticket_created',
                        'content': f"✓ Support ticket created successfully!\n\n**Ticket #{result['ticket_id']}**: {result['title']}\n\nYou can track your ticket at: {result['ticket_url']}\n\nWe'll contact you at {result['user_email']} soon.",
                        'ticket_info': result
                    }
                else:
                    return {
                        'type': 'ticket_error',
                        'content': f"✗ Failed to create ticket: {result['error']}\n\nPlease contact us directly at {config.COMPANY_EMAIL} or call {config.COMPANY_PHONE}",
                        'error': result['error']
                    }

            except Exception as e:
                return {
                    'type': 'ticket_error',
                    'content': f"✗ Error creating ticket: {str(e)}",
                    'error': str(e)
                }

        return {
            'type': 'error',
            'content': 'Unknown function called',
            'sources': []
        }

    def get_stats(self) -> Dict:
        """Get system statistics"""
        return self.vector_store.get_collection_stats()
