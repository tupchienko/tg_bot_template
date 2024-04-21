from typing import Type, List

from langchain.chains.llm import LLMChain
from langchain.memory.prompt import SUMMARY_PROMPT
from langchain.schema import BaseMessage, SystemMessage, get_buffer_string
from langchain.schema.language_model import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate
from pydantic import v1 as pydantic_v1


class SummarizerMixinAsync(pydantic_v1.BaseModel):
    """Mixin for summarizer."""

    human_prefix: str = "Human"
    ai_prefix: str = "AI"
    llm: BaseLanguageModel
    prompt: BasePromptTemplate = SUMMARY_PROMPT
    summary_message_cls: Type[BaseMessage] = SystemMessage

    async def predict_new_summary(
        self, messages: List[BaseMessage], existing_summary: str
    ) -> str:
        new_lines = get_buffer_string(
            messages,
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )

        chain = LLMChain(llm=self.llm, prompt=self.prompt)
        return await chain.apredict(summary=existing_summary, new_lines=new_lines)
