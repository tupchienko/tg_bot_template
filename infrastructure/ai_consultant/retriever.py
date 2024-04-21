import logging
from dataclasses import dataclass
from typing import List

from faiss import FileIOReader
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from infrastructure.ai_consultant.chat_history import SQLChatMessageHistory
from infrastructure.ai_consultant.memory import ConversationSummaryBufferMemoryAsync
from infrastructure.ai_consultant.prompt import PROMPT
from infrastructure.database.models.message import Message


@dataclass
class LLMArgs:
    messages: List[Message]
    session_id: str
    question: str
    session_pool: AsyncSession


async def create_or_load_index(index_name: str, chunks: List[Document]) -> FAISS:
    embeddings = OpenAIEmbeddings()
    vectorstore_path = f"./vectorstore/{index_name}"
    try:
        vectorstore = FAISS.load_local(folder_path=vectorstore_path, index_name=index_name, embeddings=embeddings,
                                       allow_dangerous_deserialization=True)
    except Exception as e:
        logging.error(e)
        try:
            vectorstore = FAISS.from_documents(chunks, embeddings)
            vectorstore.save_local(vectorstore_path, index_name)
        except Exception as save_error:
            logging.error(f"Failed to save new index: {save_error}")
            raise
    return vectorstore


async def retrieve_answer(qa: BaseConversationalRetrievalChain, question: str, history_dict: str) -> str:
    response = await qa.ainvoke({
        "question": question,
        "chat_history": [],
        "history": history_dict,
    })
    return response["answer"]


async def run_index_llm(llm_args: LLMArgs) -> str:
    llm = ChatOpenAI(temperature="0", model="gpt-4-turbo")
    message_history = SQLChatMessageHistory(session_id=llm_args.session_id, session_pool=llm_args.session_pool,
                                            message_history=llm_args.messages)

    memory = ConversationSummaryBufferMemoryAsync(llm=llm, max_token_limit=1000, chat_memory=message_history)

    history_dict = await memory.prep_history()
    loader = PyPDFLoader("./data/university_data.pdf")
    pages = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0, length_function=len)
    chunks = text_splitter.split_documents(documents=pages)

    index_name = "university_data"
    vectorstore = await create_or_load_index(index_name, chunks)

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        condense_question_llm=llm,
        combine_docs_chain_kwargs={"prompt": PROMPT}
    )

    response = await retrieve_answer(
        qa,
        llm_args.question,
        history_dict=history_dict["history"],
    )
    await memory.save_context({"input": llm_args.question}, {"response": response})
    return response
