from textual.widgets import Static, Input
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.message import Message
from textual.reactive import reactive
from rich.text import Text
from rich.markdown import Markdown


class ChatMessage(Static):
    DEFAULT_CSS = """
    ChatMessage {
        margin: 0 1;
        padding: 0 1;
    }
    
    ChatMessage.user {
        color: $text;
    }
    
    ChatMessage.groqmate {
        color: $success;
    }
    
    ChatMessage.system {
        color: $warning;
        text-style: italic;
    }
    """
    
    message_content: reactive[str] = reactive("")
    is_streaming: reactive[bool] = reactive(False)
    
    class StreamComplete(Message):
        pass
    
    def __init__(
        self, 
        sender: str, 
        content: str = "", 
        is_user: bool = False,
        is_system: bool = False,
        is_streaming: bool = False
    ):
        super().__init__()
        self.sender = sender
        self.is_user = is_user
        self.is_system = is_system
        self.is_streaming = is_streaming
        self.message_content = content
    
    def append_content(self, token: str) -> None:
        self.message_content += token
        self.refresh()
    
    def finalize(self) -> None:
        self.is_streaming = False
        self.refresh()
    
    def render(self) -> Text:
        lines = self.message_content.split('\n')
        result = Text()
        
        prefix = ""
        if self.is_user:
            prefix = "You: "
            style = "bold white"
        elif self.is_system:
            prefix = "System: "
            style = "italic yellow"
        else:
            prefix = "Groqmate: "
            style = "bold green"
        
        result.append(prefix, style=style)
        
        for i, line in enumerate(lines):
            if i > 0:
                result.append("\n")
                if not self.is_system:
                    result.append("          ", style="dim")
            result.append(line)
        
        if self.is_streaming:
            result.append(" ▏", style="bold green blink")
        
        return result


class ChatLog(ScrollableContainer):
    DEFAULT_CSS = """
    ChatLog {
        height: 1fr;
        padding: 1 0;
    }
    """
    
    def __init__(self):
        super().__init__()
        self._streaming_message = None
    
    def add_message(
        self, 
        sender: str, 
        content: str, 
        is_user: bool = False,
        is_system: bool = False,
        is_streaming: bool = False
    ) -> ChatMessage:
        message = ChatMessage(
            sender=sender,
            content=content,
            is_user=is_user,
            is_system=is_system,
            is_streaming=is_streaming
        )
        self.mount(message)
        self.scroll_end(animate=False)
        
        if is_streaming:
            self._streaming_message = message
        
        return message
    
    def append_to_streaming(self, token: str) -> None:
        if self._streaming_message:
            self._streaming_message.append_content(token)
            self.scroll_end(animate=False)
    
    def finalize_streaming(self) -> None:
        if self._streaming_message:
            self._streaming_message.finalize()
            self._streaming_message = None
    
    def clear_chat(self) -> None:
        for child in list(self.children):
            child.remove()


class InputBar(Container):
    DEFAULT_CSS = """
    InputBar {
        dock: bottom;
        height: auto;
        padding: 1 2;
        background: $surface-darken-1;
    }
    
    InputBar Input {
        width: 1fr;
    }
    
    InputBar .hint {
        color: $text-muted;
        text-align: center;
        height: 1;
    }
    """
    
    class Submitted(Message):
        def __init__(self, value: str):
            super().__init__()
            self.value = value
    
    def __init__(self, placeholder: str = "Type your answer or command..."):
        super().__init__()
        self.placeholder = placeholder
    
    def compose(self):
        yield Input(placeholder=self.placeholder, id="chat-input")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.post_message(self.Submitted(event.value))
            event.input.value = ""
    
    def focus_input(self) -> None:
        self.query_one(Input).focus()
    
    def set_placeholder(self, text: str) -> None:
        self.query_one(Input).placeholder = text
