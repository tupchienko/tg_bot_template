import json
from typing import List

from langchain.schema import messages_from_dict, _message_to_dict, BaseMessage
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from infrastructure.ai_consultant.memory import BaseChatMessageHistoryAsync
from infrastructure.database.models.message import Message


class SQLChatMessageHistory(BaseChatMessageHistoryAsync):
    """Chat message history stored in an SQL database."""

    def __init__(
            self,
            message_history: list[Message],
            session_id: str,
            session_pool: AsyncSession,
    ):
        self.message_history = message_history
        self.Message = Message
        self.session_id = session_id
        self.session = session_pool

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve all messages from db"""
        if len(self.message_history):
            items = [json.loads(record.message) for record in self.message_history]
        else:
            items = []
        messages = messages_from_dict(items)
        return messages

    async def add_message(self, message: BaseMessage) -> None:
        jsonstr = json.dumps(_message_to_dict(message), ensure_ascii=False)
        self.session.add(self.Message(session_id=self.session_id, message=jsonstr))
        await self.session.commit()

    async def clear(self) -> None:
        """Clear session memory from db"""
        await self.session.query(self.Message).filter(
            self.Message.session_id == self.session_id
        ).delete()
        await self.session.commit()
