from abc import ABC
from typing import Optional, Tuple, Dict, Any

from langchain.memory.utils import get_prompt_input_key

from infrastructure.ai_consultant.memory.chat_message_history import BaseChatMessageHistoryAsync
from infrastructure.ai_consultant.memory.memory_async import BaseMemoryAsync


class BaseChatMemoryAsync(BaseMemoryAsync, ABC):
    """Abstract base class for chat memory."""

    chat_memory: BaseChatMessageHistoryAsync
    output_key: Optional[str] = None
    input_key: Optional[str] = None
    return_messages: bool = False

    def _get_input_output(
        self, inputs: Dict[str, Any], outputs: Dict[str, str]
    ) -> Tuple[str, str]:
        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key
        if self.output_key is None:
            if len(outputs) != 1:
                raise ValueError(f"One output key expected, got {outputs.keys()}")
            output_key = list(outputs.keys())[0]
        else:
            output_key = self.output_key
        return inputs[prompt_input_key], outputs[output_key]

    async def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        input_str, output_str = self._get_input_output(inputs, outputs)
        await self.chat_memory.add_user_message(input_str)
        await self.chat_memory.add_ai_message(output_str)

    async def clear(self) -> None:
        """Clear memory contents."""
        await self.chat_memory.clear()