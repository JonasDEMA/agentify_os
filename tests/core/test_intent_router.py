"""Tests for Intent Router."""

import pytest
from scheduler.core.intent_router import Intent, IntentRouter


class TestIntent:
    """Tests for Intent model."""

    def test_create_intent(self) -> None:
        """Test creating an intent."""
        intent = Intent(
            name="send_mail",
            patterns=["send email", "send mail", "email.*to"],
            description="Send an email",
        )
        assert intent.name == "send_mail"
        assert len(intent.patterns) == 3
        assert intent.description == "Send an email"

    def test_intent_serialization(self) -> None:
        """Test intent serialization."""
        intent = Intent(
            name="search_document",
            patterns=["search for", "find document"],
            description="Search for a document",
        )
        data = intent.model_dump()
        assert data["name"] == "search_document"
        assert data["patterns"] == ["search for", "find document"]


class TestIntentRouter:
    """Tests for IntentRouter class."""

    def test_create_router(self) -> None:
        """Test creating an intent router."""
        router = IntentRouter()
        assert router is not None
        assert len(router.intents) == 0

    def test_register_intent(self) -> None:
        """Test registering an intent."""
        router = IntentRouter()
        intent = Intent(
            name="send_mail",
            patterns=["send email", "send mail"],
            description="Send an email",
        )
        router.register_intent(intent)
        assert len(router.intents) == 1
        assert "send_mail" in router.intents

    def test_register_multiple_intents(self) -> None:
        """Test registering multiple intents."""
        router = IntentRouter()
        
        intent1 = Intent(name="send_mail", patterns=["send email"], description="Send email")
        intent2 = Intent(name="search_doc", patterns=["search"], description="Search")
        intent3 = Intent(name="export_pdf", patterns=["export pdf"], description="Export")
        
        router.register_intent(intent1)
        router.register_intent(intent2)
        router.register_intent(intent3)
        
        assert len(router.intents) == 3

    def test_route_exact_match(self) -> None:
        """Test routing with exact pattern match."""
        router = IntentRouter()
        intent = Intent(
            name="send_mail",
            patterns=["send email", "send mail"],
            description="Send an email",
        )
        router.register_intent(intent)
        
        result = router.route("send email")
        assert result == "send_mail"

    def test_route_case_insensitive(self) -> None:
        """Test routing is case insensitive."""
        router = IntentRouter()
        intent = Intent(
            name="send_mail",
            patterns=["send email"],
            description="Send an email",
        )
        router.register_intent(intent)
        
        assert router.route("SEND EMAIL") == "send_mail"
        assert router.route("Send Email") == "send_mail"
        assert router.route("send email") == "send_mail"

    def test_route_regex_pattern(self) -> None:
        """Test routing with regex patterns."""
        router = IntentRouter()
        intent = Intent(
            name="send_mail",
            patterns=[r"send.*email", r"email.*to.*"],
            description="Send an email",
        )
        router.register_intent(intent)
        
        assert router.route("send an email") == "send_mail"
        assert router.route("send the email") == "send_mail"
        assert router.route("email this to john") == "send_mail"

    def test_route_partial_match(self) -> None:
        """Test routing with partial matches."""
        router = IntentRouter()
        intent = Intent(
            name="search_document",
            patterns=["search for", "find document"],
            description="Search for a document",
        )
        router.register_intent(intent)
        
        assert router.route("search for invoice") == "search_document"
        assert router.route("please find document xyz") == "search_document"

    def test_route_unknown_intent(self) -> None:
        """Test routing unknown intent returns fallback."""
        router = IntentRouter()
        intent = Intent(
            name="send_mail",
            patterns=["send email"],
            description="Send an email",
        )
        router.register_intent(intent)
        
        result = router.route("do something random")
        assert result == "unknown"

    def test_route_empty_message(self) -> None:
        """Test routing empty message."""
        router = IntentRouter()
        result = router.route("")
        assert result == "unknown"

    def test_route_priority_first_match(self) -> None:
        """Test that first matching intent is returned."""
        router = IntentRouter()
        
        intent1 = Intent(name="general_email", patterns=["email"], description="Email")
        intent2 = Intent(name="send_mail", patterns=["send email"], description="Send email")
        
        router.register_intent(intent1)
        router.register_intent(intent2)
        
        # "send email" matches both, but should return first registered
        result = router.route("send email")
        assert result == "general_email"

    def test_route_multiple_patterns(self) -> None:
        """Test intent with multiple patterns."""
        router = IntentRouter()
        intent = Intent(
            name="export_pdf",
            patterns=["export.*pdf", "save.*pdf", "create.*pdf"],
            description="Export to PDF",
        )
        router.register_intent(intent)
        
        assert router.route("export to pdf") == "export_pdf"
        assert router.route("save as pdf") == "export_pdf"
        assert router.route("create a pdf") == "export_pdf"

    def test_get_intent(self) -> None:
        """Test getting an intent by name."""
        router = IntentRouter()
        intent = Intent(
            name="send_mail",
            patterns=["send email"],
            description="Send an email",
        )
        router.register_intent(intent)
        
        retrieved = router.get_intent("send_mail")
        assert retrieved is not None
        assert retrieved.name == "send_mail"

    def test_get_nonexistent_intent(self) -> None:
        """Test getting a non-existent intent."""
        router = IntentRouter()
        result = router.get_intent("nonexistent")
        assert result is None

    def test_load_from_dict(self) -> None:
        """Test loading intents from dictionary."""
        router = IntentRouter()
        intents_data = [
            {
                "name": "send_mail",
                "patterns": ["send email", "send mail"],
                "description": "Send an email",
            },
            {
                "name": "search_doc",
                "patterns": ["search", "find"],
                "description": "Search for document",
            },
        ]
        
        router.load_from_dict(intents_data)
        assert len(router.intents) == 2
        assert router.route("send email") == "send_mail"
        assert router.route("search for file") == "search_doc"

    def test_complex_routing_scenario(self) -> None:
        """Test complex routing scenario with multiple intents."""
        router = IntentRouter()
        
        intents = [
            Intent(
                name="send_mail",
                patterns=[r"send.*email", r"email.*to"],
                description="Send email",
            ),
            Intent(
                name="search_document",
                patterns=[r"search.*for", r"find.*document"],
                description="Search document",
            ),
            Intent(
                name="export_pdf",
                patterns=[r"export.*pdf", r"save.*pdf"],
                description="Export PDF",
            ),
            Intent(
                name="open_app",
                patterns=[r"open.*", r"start.*", r"launch.*"],
                description="Open application",
            ),
        ]
        
        for intent in intents:
            router.register_intent(intent)
        
        assert router.route("send email to john") == "send_mail"
        assert router.route("search for invoice") == "search_document"
        assert router.route("export to pdf") == "export_pdf"
        assert router.route("open chrome") == "open_app"
        assert router.route("random text") == "unknown"

    def test_special_characters_in_message(self) -> None:
        """Test routing with special characters."""
        router = IntentRouter()
        intent = Intent(
            name="send_mail",
            patterns=["send email"],
            description="Send email",
        )
        router.register_intent(intent)
        
        # Should handle special characters gracefully
        assert router.route("send email!") == "send_mail"
        assert router.route("send email?") == "send_mail"
        assert router.route("send email.") == "send_mail"

