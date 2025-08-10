from app.agents.conversation_agent.ConversationAgent import ConversationAgent


class ConversationService:
    """Service class for handling conversation-related operations with RAG support using agent architecture."""

    def __init__(self, conversation_agent: ConversationAgent):
        self.conversation_agent = conversation_agent

    async def process_question(self, question: str, use_rag: bool = True):
        return await self.conversation_agent.invoke(question, use_rag)