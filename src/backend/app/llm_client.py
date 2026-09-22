from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from app.config import settings
import structlog
import random

logger = structlog.get_logger()


class MockLLM(BaseChatModel):
    """
    Mock LLM for local testing without a real AI gateway.
    Simulates responses with different models based on query type.
    """

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """Generate mock response"""
        # Get the last user message
        last_message = messages[-1].content if messages else ""

        # Simulate different responses based on query type
        query_type = kwargs.get("query_type", "faq")

        if query_type == "escalation":
            model_name = random.choice(["gpt-4", "claude-3-5-sonnet"])
            response = f"I understand this is important. Let me provide detailed assistance: {last_message[:50]}..."
        else:
            model_name = random.choice(["gpt-3.5-turbo", "llama-3-8b"])
            response = f"Here's a quick answer: {last_message[:50]}..."

        # Simulate fallback 10% of the time
        fallback_triggered = random.random() < 0.1

        ai_message = AIMessage(
            content=response,
            additional_kwargs={
                "model": model_name,
                "fallback_triggered": fallback_triggered
            }
        )

        from langchain_core.outputs import ChatGeneration, ChatResult
        generation = ChatGeneration(message=ai_message)
        return ChatResult(generations=[generation])

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        """Async generate - calls sync version"""
        return self._generate(messages, stop, run_manager, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "mock"

    def invoke(self, messages, **kwargs):
        """Invoke the mock LLM"""
        result = self._generate(messages, **kwargs)
        return result.generations[0].message


class GatewayLLM(ChatOpenAI):
    """
    LLM client that connects to the AI Gateway.
    Uses OpenAI-compatible API format.
    """

    def __init__(self, query_type: str = "faq"):
        """
        Initialize gateway LLM client.

        Args:
            query_type: Query type for routing (faq or escalation)
        """
        super().__init__(
            base_url=settings.GATEWAY_BASE_URL,
            api_key="dummy",  # Gateway handles auth
            model="default",  # Gateway decides actual model
            timeout=settings.GATEWAY_TIMEOUT,
            default_headers={
                "x-query-type": query_type,
                "x-department": "support"
            }
        )
        self.query_type = query_type
        logger.info("gateway_llm_initialized", query_type=query_type)


def get_llm_client(query_type: str = "faq", use_mock: bool = None):
    """
    Factory function to get LLM client.

    Args:
        query_type: Query type (faq or escalation)
        use_mock: Force mock mode (None = auto-detect based on environment)

    Returns:
        LLM client instance
    """
    # Auto-detect: use mock in development if no gateway configured
    if use_mock is None:
        use_mock = settings.is_dev() and "localhost:8080" in settings.GATEWAY_BASE_URL

    if use_mock:
        logger.info("using_mock_llm", query_type=query_type)
        return MockLLM()
    else:
        logger.info("using_gateway_llm", query_type=query_type, gateway_url=settings.GATEWAY_BASE_URL)
        return GatewayLLM(query_type=query_type)
