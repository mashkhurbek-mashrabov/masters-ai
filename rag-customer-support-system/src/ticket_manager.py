"""
Ticket Manager Module
Handles GitHub Issues API integration for support ticket creation
"""
import requests
import json
from typing import Dict, Optional
from datetime import datetime

class TicketManager:
    """Manage support tickets via GitHub Issues"""

    def __init__(self, github_token: str, github_repo: str):
        """
        Initialize ticket manager

        Args:
            github_token: GitHub personal access token
            github_repo: Repository in format 'owner/repo'
        """
        self.github_token = github_token
        self.github_repo = github_repo
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def create_ticket(
        self,
        user_name: str,
        user_email: str,
        title: str,
        description: str
    ) -> Dict:
        """
        Create a support ticket as a GitHub Issue

        Args:
            user_name: Name of the user
            user_email: Email of the user
            title: Ticket title/summary
            description: Detailed description

        Returns:
            Dictionary with ticket information or error
        """
        if not self.github_token or not self.github_repo:
            return {
                'success': False,
                'error': 'GitHub configuration missing. Please set GITHUB_TOKEN and GITHUB_REPO in .env file'
            }

        # Format issue body
        issue_body = f"""**Support Ticket**

**User Information:**
- Name: {user_name}
- Email: {user_email}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Description:**
{description}

---
*This ticket was automatically created by the Tesla Cybertruck Support System*
"""

        # Create issue payload
        payload = {
            "title": f"[Support] {title}",
            "body": issue_body,
            "labels": ["support", "customer-inquiry"]
        }

        # API endpoint
        url = f"{self.api_base}/repos/{self.github_repo}/issues"

        try:
            response = requests.post(url, headers=self.headers, json=payload)

            if response.status_code == 201:
                issue_data = response.json()
                return {
                    'success': True,
                    'ticket_id': issue_data['number'],
                    'ticket_url': issue_data['html_url'],
                    'title': title,
                    'user_name': user_name,
                    'user_email': user_email
                }
            else:
                return {
                    'success': False,
                    'error': f"GitHub API error: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create ticket: {str(e)}"
            }

    def validate_config(self) -> bool:
        """
        Validate GitHub configuration

        Returns:
            True if configuration is valid
        """
        if not self.github_token or not self.github_repo:
            return False

        # Test API access
        url = f"{self.api_base}/repos/{self.github_repo}"
        try:
            response = requests.get(url, headers=self.headers)
            return response.status_code == 200
        except:
            return False
