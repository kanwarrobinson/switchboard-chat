from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from app.config import settings
from app.database import db
from datetime import datetime
import structlog

logger = structlog.get_logger()


# Define the state
class State(TypedDict):
    """State for the chat graph"""
    messages: Annotated[list[BaseMessage], add_messages]
    query_type: str


class ChatGraph:
    """LangGraph-based chat system with MongoDB storage"""

    def __init__(self, llm_client):
        """
        Initialize the chat graph.

        Args:
            llm_client: LLM client (LangChain-compatible)
        """
        self.llm_client = llm_client
        self.checkpointer = MemorySaver()  # In-memory checkpointing for graph state
        self.graph = None

    def setup_checkpointer(self):
        """Set up checkpointer (using in-memory)"""
        logger.info("langgraph_checkpointer_initialized", type="memory")

    def call_model(self, state: State) -> State:
        """
        Call the LLM model.

        Args:
            state: Current state

        Returns:
            Updated state with AI response
        """
        try:
            # Get conversation history
            messages = state["messages"]

            # Call LLM
            response = self.llm_client.invoke(messages)

            # Return updated state
            return {
                "messages": [response],
                "query_type": state.get("query_type", "faq")
            }
        except Exception as e:
            logger.error("llm_call_failed", error=str(e))
            # Return error message
            error_message = AIMessage(
                content=f"I apologize, but I encountered an error: {str(e)}. Please try again."
            )
            return {
                "messages": [error_message],
                "query_type": state.get("query_type", "faq")
            }

    def build_graph(self):
        """Build the LangGraph workflow"""
        # Create graph
        workflow = StateGraph(State)

        # Add node
        workflow.add_node("chat", self.call_model)

        # Add edges
        workflow.add_edge(START, "chat")
        workflow.add_edge("chat", END)

        # Compile with checkpointer
        self.graph = workflow.compile(checkpointer=self.checkpointer)

        logger.info("langgraph_workflow_compiled")

    async def ainvoke(self, message: str, session_id: str, query_type: str = "faq"):
        """
        Async invoke the chat graph and save to MongoDB.

        Args:
            message: User message
            session_id: Session/thread ID
            query_type: Type of query (faq or escalation)

        Returns:
            AI response message
        """
        try:
            # Get previous messages from MongoDB
            previous_messages = self._load_from_mongodb(session_id)

            # Create input state with full history
            input_state = {
                "messages": previous_messages + [HumanMessage(content=message)],
                "query_type": query_type
            }

            # Configure with thread_id
            config = {
                "configurable": {
                    "thread_id": session_id
                }
            }

            # Invoke graph
            result = await self.graph.ainvoke(input_state, config)

            # Extract AI message
            ai_message = result["messages"][-1]

            # Save conversation to MongoDB
            self._save_to_mongodb(session_id, message, ai_message.content, query_type, ai_message.additional_kwargs)

            return ai_message

        except Exception as e:
            logger.error("chat_graph_invoke_failed", error=str(e), session_id=session_id)
            raise

    def _load_from_mongodb(self, session_id: str) -> list[BaseMessage]:
        """Load conversation history from MongoDB"""
        try:
            mongo_db = db.get_database()
            conversations = mongo_db["conversations"]

            session = conversations.find_one({"session_id": session_id})
            if not session:
                return []

            messages = []
            for msg in session.get("messages", []):
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(
                        content=msg["content"],
                        additional_kwargs=msg.get("metadata", {})
                    ))

            return messages
        except Exception as e:
            logger.error("load_from_mongodb_failed", error=str(e), session_id=session_id)
            return []

    def _save_to_mongodb(self, session_id: str, user_message: str, ai_message: str, query_type: str, metadata: dict):
        """Save conversation to MongoDB"""
        try:
            mongo_db = db.get_database()
            conversations = mongo_db["conversations"]

            # Prepare messages
            user_msg = {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow(),
                "query_type": query_type
            }

            ai_msg = {
                "role": "assistant",
                "content": ai_message,
                "timestamp": datetime.utcnow(),
                "query_type": query_type,
                "metadata": metadata
            }

            # Upsert session
            conversations.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": {"$each": [user_msg, ai_msg]}},
                    "$set": {
                        "updated_at": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )

            logger.info("saved_to_mongodb", session_id=session_id, message_count=2)

        except Exception as e:
            logger.error("save_to_mongodb_failed", error=str(e), session_id=session_id)

    def get_conversation_history(self, session_id: str):
        """
        Get conversation history for a session from MongoDB.

        Args:
            session_id: Session ID

        Returns:
            List of messages
        """
        try:
            mongo_db = db.get_database()
            conversations = mongo_db["conversations"]

            session = conversations.find_one({"session_id": session_id})
            if not session:
                return []

            return session.get("messages", [])

        except Exception as e:
            logger.error("get_conversation_history_failed", error=str(e), session_id=session_id)
            return []
