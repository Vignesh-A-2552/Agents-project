import json
from datetime import datetime
from langgraph.graph import StateGraph, END
from loguru import logger

from app.models.types import CodeReviewState
from app.core.llm_service import LLMService
from app.core.prompt_service import PromptService
from app.agents.code_review_agent.CodeReviewAgent import CodeReviewAgent


class CodeReviewService:
    def __init__(self, code_review_agent: CodeReviewAgent):
        self.code_review_agent = code_review_agent

    async def analyze_code(self, state: 'CodeReviewState'):
        """Analyze code using the code review agent.
        Args:
            state (CodeReviewState): The state containing code to analyze.
        Returns:
            CodeReviewState: The state after analysis.
        """
        return await self.code_review_agent.invoke(state) 