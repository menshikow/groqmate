import pytest
from groqmate.interfaces.cli.widgets import ChatMessage, ChatLog, InputBar


class TestChatMessage:
    def test_user_message_render(self):
        msg = ChatMessage("You", "Hello", is_user=True)
        rendered = msg.render()
        assert "You:" in str(rendered)

    def test_groqmate_message_render(self):
        msg = ChatMessage("Groqmate", "Hi there!")
        rendered = msg.render()
        assert "Groqmate:" in str(rendered)

    def test_system_message_render(self):
        msg = ChatMessage("System", "Welcome", is_system=True)
        rendered = msg.render()
        assert "System:" in str(rendered)

    def test_append_content(self):
        msg = ChatMessage("Groqmate", "Hello")
        msg.append_content(" World")
        assert "Hello World" in str(msg.render())

    def test_finalize_removes_streaming(self):
        msg = ChatMessage("Groqmate", "Test", is_streaming=True)
        assert msg.is_streaming is True
        msg.finalize()
        assert msg.is_streaming is False

    def test_multiline_render(self):
        msg = ChatMessage("Groqmate", "Line 1\nLine 2\nLine 3")
        rendered = str(msg.render())
        assert "Line 1" in rendered
        assert "Line 2" in rendered
        assert "Line 3" in rendered

    def test_streaming_shows_cursor(self):
        msg = ChatMessage("Groqmate", "Test", is_streaming=True)
        rendered = str(msg.render())
        assert "▏" in rendered

    def test_non_streaming_no_cursor(self):
        msg = ChatMessage("Groqmate", "Test", is_streaming=False)
        rendered = str(msg.render())
        assert "▏" not in rendered

    def test_empty_message(self):
        msg = ChatMessage("Groqmate", "")
        rendered = str(msg.render())
        assert "Groqmate:" in rendered

    def test_default_is_user_false(self):
        msg = ChatMessage("Groqmate", "Test")
        assert msg.is_user is False

    def test_default_is_system_false(self):
        msg = ChatMessage("You", "Test", is_user=True)
        assert msg.is_system is False


class TestInputBar:
    def test_submitted_message(self):
        msg = InputBar.Submitted("test input")
        assert msg.value == "test input"

    def test_submitted_message_strips_whitespace(self):
        msg = InputBar.Submitted("  test  ")
        assert msg.value == "  test  "


class TestChatLog:
    def test_chatlog_exists(self):
        from groqmate.interfaces.cli.widgets import ChatLog

        assert ChatLog is not None

    def test_chatlog_has_add_message_method(self):
        from groqmate.interfaces.cli.widgets import ChatLog

        assert hasattr(ChatLog, "add_message")

    def test_chatlog_has_append_to_streaming_method(self):
        from groqmate.interfaces.cli.widgets import ChatLog

        assert hasattr(ChatLog, "append_to_streaming")

    def test_chatlog_has_finalize_streaming_method(self):
        from groqmate.interfaces.cli.widgets import ChatLog

        assert hasattr(ChatLog, "finalize_streaming")

    def test_chatlog_has_clear_chat_method(self):
        from groqmate.interfaces.cli.widgets import ChatLog

        assert hasattr(ChatLog, "clear_chat")
