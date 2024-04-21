from abc import ABC, abstractmethod
from typing import List

from langchain.schema import BaseMessage, HumanMessage, AIMessage


class BaseChatMessageHistoryAsync(ABC):
    messages: List[BaseMessage]
    """A list of Messages stored in-memory."""

    async def add_user_message(self, message: str) -> None:
        """Convenience method for adding a human message string to the store.

        Args:
            message: The string contents of a human message.
        """
        await self.add_message(HumanMessage(content=message))

    async def add_ai_message(self, message: str) -> None:
        """Convenience method for adding an AI message string to the store.

        Args:
            message: The string contents of an AI message.
        """
        await self.add_message(AIMessage(content=message))

    @abstractmethod
    async def add_message(self, message: BaseMessage) -> None:
        """Add a Message object to the store.

        Args:
            message: A BaseMessage object to store.
        """
        raise NotImplementedError

    @abstractmethod
    async def clear(self) -> None:
        """Remove all messages from the store"""