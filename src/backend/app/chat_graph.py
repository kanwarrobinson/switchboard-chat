from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from app.config import settings
from app.database import db
import structlog

logger = structlog.get_logger()


# Define the state
class State(TypedDict):
    """State for the chat graph"""
    messages: Annotated[list[BaseMessage], add_messages]
    query_type: str


class ChatGraph:
    """LangGraph-based chat system with MongoDB checkpointing"""

    def __init__(self, llm_client):
        """
        Initialize the chat graph.

        Args:
            llm_client: LLM client (LangChain-compatible)
        """
        self.llm_client = llm_client
        self.checkpointer = None
        self.graph = None

    def setup_checkpointer(self):
        """Set up MongoDB checkpointer"""
        try:
            mongo_db = db.get_database()
            self.checkpointer = MongoDBSaver(
                client=db.client,
                db_name=settings.MONGODB_DATABASE
            )
            logger.info("langgraph_checkpointer_initialized")
        except Exception as e:
            logger.error("langgraph_checkpointer_failed", error=str(e))
            raise

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
        Async invoke the chat graph.

        Args:
            message: User message
            session_id: Session/thread ID
            query_type: Type of query (faq or escalation)

        Returns:
            AI response message
        """
        try:
            # Create input state
            input_state = {
                "messages": [HumanMessage(content=message)],
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

            return ai_message

        except Exception as e:
            logger.error("chat_graph_invoke_failed", error=str(e), session_id=session_id)
            raise

    def get_conversation_history(self, session_id: str):
        """
        Get conversation history for a session.

        Args:
            session_id: Session ID

        Returns:
            List of messages
        """
        try:
            config = {"configurable": {"thread_id": session_id}}
            state = self.graph.get_state(config)

            if state and state.values:
                return state.values.get("messages", [])

            return []
        except Exception as e:
            logger.error("get_conversation_history_failed", error=str(e), session_id=session_id)
            return []
