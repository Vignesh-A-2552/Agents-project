import json
from datetime import datetime
from langgraph.graph import StateGraph, END
from loguru import logger

from models.types import CodeReviewState
from core.llm_service import LLMService
from core.prompt_service import PromptService
from agents.code_review_agent import CodeReviewAgent


class CodeReviewService:
    def __init__(self, code_review_agent: CodeReviewAgent):
        self.code_review_agent = code_review_agent

    def analyze_code(self, question: str, use_rag: bool = True):
        """Analyze code using the code review agent.
        Args:
            question (str): The code or question to analyze.
            use_rag (bool): Whether to use RAG for the analysis.
        Returns:
            ConversationState: The state after analysis.
        """
        return self.code_review_agent.invoke(question) 