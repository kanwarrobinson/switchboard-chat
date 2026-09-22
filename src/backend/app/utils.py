import uuid
from typing import List


def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())


def detect_query_type(message: str, conversation_history: List = None) -> str:
    """
    Simple heuristic to detect if a query is FAQ or escalation.

    Args:
        message: User's message
        conversation_history: List of previous messages in the conversation

    Returns:
        'faq' or 'escalation'
    """
    message_lower = message.lower()

    # Escalation keywords
    escalation_keywords = [
        'not working', 'still broken', 'need help', 'escalate',
        'speak to human', 'talk to person', 'manager', 'supervisor',
        'urgent', 'critical', 'emergency', 'frustrated', 'angry',
        'disappointed', 'unacceptable', 'terrible', 'awful',
        'doesn\'t work', 'won\'t work', 'can\'t', 'unable to',
        'tried everything', 'nothing works', 'help me', 'stuck'
    ]

    # Check for escalation keywords
    if any(keyword in message_lower for keyword in escalation_keywords):
        return 'escalation'

    # Check conversation length (long conversations might need escalation)
    if conversation_history and len(conversation_history) > 6:
        return 'escalation'

    # Default to FAQ
    return 'faq'


def extract_model_from_response(response_data: dict) -> tuple:
    """
    Extract model and provider information from LLM response.

    Args:
        response_data: Response from the LLM

    Returns:
        tuple: (model_name, provider, fallback_triggered)
    """
    model_used = response_data.get('model', 'unknown')

    # Determine provider from model name
    provider = 'unknown'
    if 'gpt' in model_used.lower():
        provider = 'openai'
    elif 'claude' in model_used.lower():
        provider = 'anthropic'
    elif 'llama' in model_used.lower() or 'mistral' in model_used.lower():
        provider = 'self-hosted'

    # Check for fallback metadata (if gateway provides it)
    fallback_triggered = response_data.get('metadata', {}).get('fallback_triggered', False)

    return model_used, provider, fallback_triggered
