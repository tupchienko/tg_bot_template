from typing import List, Dict, Any
from langchain.schema import BaseMessage, get_buffer_string
from pydantic import v1 as pydantic_v1

from infrastructure.ai_consultant.memory.chat_memory import BaseChatMemoryAsync
from infrastructure.ai_consultant.memory.summarizer_mixin_async import SummarizerMixinAsync


class ConversationSummaryBufferMemoryAsync(BaseChatMemoryAsync, SummarizerMixinAsync):
    """Buffer with summarizer for storing conversation memory."""

    max_token_limit: int = 2000
    moving_summary_buffer: str = ""
    memory_key: str = "history"

    @property
    def buffer(self) -> List[BaseMessage]:
        return self.chat_memory.messages

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return [self.memory_key]

    async def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return history buffer."""
        await self.prune()
        buffer = self.buffer
        if self.moving_summary_buffer != "":
            first_messages: List[BaseMessage] = [
                self.summary_message_cls(content=self.moving_summary_buffer)
            ]
            buffer = first_messages + buffer[-2:]
        if self.return_messages:
            final_buffer: Any = buffer
        else:
            final_buffer = get_buffer_string(
                buffer, human_prefix=self.human_prefix, ai_prefix=self.ai_prefix
            )
        return {self.memory_key: final_buffer}

    @pydantic_v1.root_validator()
    def validate_prompt_input_variables(cls, values: Dict) -> Dict:
        """Validate that prompt input variables are consistent."""
        prompt_variables = values["prompt"].input_variables
        expected_keys = {"summary", "new_lines"}
        if expected_keys != set(prompt_variables):
            raise ValueError(
                "Got unexpected prompt input variables. The prompt expects "
                f"{prompt_variables}, but it should have {expected_keys}."
            )
        return values

    async def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        await super().save_context(inputs, outputs)

    async def prune(self) -> None:
        """Prune buffer if it exceeds max token limit"""
        buffer = self.chat_memory.messages
        curr_buffer_length = self.llm.get_num_tokens_from_messages(buffer)
        if curr_buffer_length > self.max_token_limit:
            pruned_memory = []
            while curr_buffer_length > self.max_token_limit:
                pruned_memory.append(buffer.pop(0))
                curr_buffer_length = self.llm.get_num_tokens_from_messages(buffer)
            self.moving_summary_buffer = await self.predict_new_summary(
                pruned_memory, self.moving_summary_buffer
            )

    async def clear(self) -> None:
        """Clear memory contents."""
        await super().clear()
        self.moving_summary_buffer = ""

    async def prep_history(self) -> Dict[str, str]:
        _input_keys = set()
        _input_keys = _input_keys.difference(self.memory_variables)
        external_context = await self.load_memory_variables({})
        inputs = dict(**external_context)
        return inputs
