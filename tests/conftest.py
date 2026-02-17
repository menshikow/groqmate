import pytest
from groqmate.core.models import LessonPlan, LessonStep, SessionState, SessionStatus
from groqmate.core.state import Session
from groqmate.core.providers import ProviderConfig, Provider


@pytest.fixture
def sample_step():
    return LessonStep(
        index=0,
        title="Self-Reference",
        concept="A recursive function calls itself to solve smaller instances.",
        quiz_question="What is the key component that stops recursion?",
        quiz_answer="base case",
    )


@pytest.fixture
def sample_plan(sample_step):
    return LessonPlan(
        topic="Recursion",
        steps=[
            sample_step,
            LessonStep(
                index=1,
                title="Base Case",
                concept="The condition that stops recursion.",
                quiz_question="What happens without a base case?",
                quiz_answer="infinite loop",
            ),
            LessonStep(
                index=2,
                title="Recursive Step",
                concept="The part where the function calls itself.",
                quiz_question="What must change in each recursive call?",
                quiz_answer="input gets smaller",
            ),
            LessonStep(
                index=3,
                title="Call Stack",
                concept="Each call is added to the stack.",
                quiz_question="What data structure tracks recursive calls?",
                quiz_answer="stack",
            ),
            LessonStep(
                index=4,
                title="Stack Overflow",
                concept="Too many recursive calls can crash the program.",
                quiz_question="What error occurs from too deep recursion?",
                quiz_answer="stack overflow",
            ),
        ],
    )


@pytest.fixture
def session(sample_plan):
    s = Session()
    s.load_plan(sample_plan)
    return s


@pytest.fixture
def empty_session():
    return Session()


@pytest.fixture
def provider_config_groq():
    return ProviderConfig(provider=Provider.GROQ)


@pytest.fixture
def provider_config_gemini():
    return ProviderConfig(provider=Provider.GEMINI, model="gemini-2.0-flash")


@pytest.fixture
def mock_litellm_response():
    """Mock response for litellm.acompletion"""

    class MockMessage:
        content = '{"topic": "Test", "steps": [{"index": 0, "title": "Intro", "concept": "Test concept", "quiz_question": "Test?", "quiz_answer": "yes"}]}'

    class MockChoice:
        message = MockMessage()
        delta = None

    class MockResponse:
        choices = [MockChoice()]

    return MockResponse()


@pytest.fixture
def mock_streaming_chunks():
    """Mock streaming response chunks"""

    class MockDelta:
        def __init__(self, content):
            self.content = content

    class MockChoice:
        def __init__(self, content):
            self.delta = MockDelta(content)

    class MockChunk:
        def __init__(self, content):
            self.choices = [MockChoice(content)]

    return [MockChunk("Hello"), MockChunk(" "), MockChunk("World")]


@pytest.fixture
def mock_empty_streaming_chunks():
    """Mock streaming response with None content"""

    class MockDelta:
        content = None

    class MockChoice:
        delta = MockDelta()

    class MockChunk:
        choices = [MockChoice()]

    return [MockChunk()]
