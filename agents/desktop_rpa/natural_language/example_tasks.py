"""Example tasks for natural language agent.

This module provides pre-defined task templates for common scenarios.
These can be used for testing and as examples for users.
"""

from typing import Any


class ExampleTasks:
    """Collection of example tasks."""
    
    # Calendar & Appointments
    CALENDAR_TASKS = [
        {
            "command": "Check my next appointment with Dieter",
            "description": "Find the next calendar appointment with a specific person",
            "expected_actions": [
                "Open Outlook",
                "Navigate to Calendar",
                "Search for appointments with 'Dieter'",
                "Find next upcoming appointment",
                "Return appointment details",
            ],
        },
        {
            "command": "Show me my calendar for today",
            "description": "Display all appointments for today",
            "expected_actions": [
                "Open Outlook",
                "Navigate to Calendar",
                "Switch to Day view",
                "Show today's appointments",
            ],
        },
        {
            "command": "Find all meetings this week",
            "description": "List all meetings scheduled for this week",
            "expected_actions": [
                "Open Outlook",
                "Navigate to Calendar",
                "Switch to Week view",
                "List all meetings",
            ],
        },
    ]
    
    # Email Tasks
    EMAIL_TASKS = [
        {
            "command": "Find all emails from John",
            "description": "Search for emails from a specific sender",
            "expected_actions": [
                "Open Outlook",
                "Navigate to Inbox",
                "Use search function",
                "Filter by sender: John",
                "Display results",
            ],
        },
        {
            "command": "Check my unread emails",
            "description": "Show all unread emails",
            "expected_actions": [
                "Open Outlook",
                "Navigate to Inbox",
                "Filter by unread",
                "Display count and list",
            ],
        },
        {
            "command": "Send an email to Sarah",
            "description": "Compose and send an email",
            "expected_actions": [
                "Open Outlook",
                "Click New Email",
                "Enter recipient: Sarah",
                "Ask user for subject and body",
                "Send email",
            ],
        },
    ]
    
    # Application Tasks
    APPLICATION_TASKS = [
        {
            "command": "Open Outlook",
            "description": "Launch Outlook application",
            "expected_actions": [
                "Search for Outlook in Start Menu",
                "Click to open",
                "Wait for application to load",
            ],
        },
        {
            "command": "Open Word and create a new document",
            "description": "Launch Word and create new document",
            "expected_actions": [
                "Search for Word in Start Menu",
                "Click to open",
                "Wait for application to load",
                "Click 'New Document'",
            ],
        },
        {
            "command": "Open Excel and load Budget.xlsx",
            "description": "Launch Excel and open specific file",
            "expected_actions": [
                "Search for Excel in Start Menu",
                "Click to open",
                "Wait for application to load",
                "Click 'Open'",
                "Navigate to file",
                "Open Budget.xlsx",
            ],
        },
    ]
    
    # System Tasks
    SYSTEM_TASKS = [
        {
            "command": "Activate Ransomware Protection in Windows",
            "description": "Enable Windows Defender Ransomware Protection",
            "expected_actions": [
                "Open Windows Security",
                "Navigate to Virus & threat protection",
                "Click Ransomware protection",
                "Enable Controlled folder access",
                "Confirm changes",
            ],
        },
        {
            "command": "Check Windows Defender status",
            "description": "Check if Windows Defender is active",
            "expected_actions": [
                "Open Windows Security",
                "Check protection status",
                "Report status to user",
            ],
        },
        {
            "command": "Take a screenshot",
            "description": "Capture current screen",
            "expected_actions": [
                "Capture screenshot",
                "Save to file",
                "Return file path",
            ],
        },
    ]
    
    # Web Tasks
    WEB_TASKS = [
        {
            "command": "Open Google and search for Python tutorials",
            "description": "Open browser and perform web search",
            "expected_actions": [
                "Open Chrome/Edge",
                "Navigate to google.com",
                "Enter search query",
                "Press Enter",
            ],
        },
        {
            "command": "Go to GitHub and check my notifications",
            "description": "Navigate to GitHub notifications",
            "expected_actions": [
                "Open Chrome/Edge",
                "Navigate to github.com",
                "Click notifications icon",
                "Display notifications",
            ],
        },
    ]
    
    @classmethod
    def get_all_tasks(cls) -> list[dict[str, Any]]:
        """Get all example tasks."""
        return (
            cls.CALENDAR_TASKS
            + cls.EMAIL_TASKS
            + cls.APPLICATION_TASKS
            + cls.SYSTEM_TASKS
            + cls.WEB_TASKS
        )
    
    @classmethod
    def get_random_task(cls) -> dict[str, Any]:
        """Get a random example task."""
        import random
        return random.choice(cls.get_all_tasks())
    
    @classmethod
    def search_tasks(cls, query: str) -> list[dict[str, Any]]:
        """Search for tasks matching query."""
        query_lower = query.lower()
        return [
            task
            for task in cls.get_all_tasks()
            if query_lower in task["command"].lower()
            or query_lower in task["description"].lower()
        ]

