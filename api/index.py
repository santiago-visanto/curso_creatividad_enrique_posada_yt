from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Any
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from pydantic import BaseModel
from contextlib import asynccontextmanager
#from api.libs.markdowndocuments import MarkdownFileProcessor
import os
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from dotenv import load_dotenv
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
load_dotenv()

# Global variables for chat history and vector store
chat_history = [AIMessage(content="Hello, I am a bot. How can I help you?")]
vector_store = None

class MarkdownFileProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.headers_to_split_on = [
            ("#", "Título"),
            ("##", "Header 2"),
        ]
        self.chunk_size = 5000
        self.chunk_overlap = 500

    def process_files(self):
        files = os.listdir(self.folder_path)
        all_docs = []
        for file_name in files:
            if file_name.endswith(".md"):
                docs = self.process_file(file_name)
                all_docs.extend(docs)
        return all_docs

    def process_file(self, file_name):
        with open(os.path.join(self.folder_path, file_name), "r") as file:
            lines = file.readlines()

        start_index, end_index = self.find_metadata_indices(lines)
        markdown_document = self.exclude_metadata(lines, start_index, end_index)

        md_header_splits = self.split_markdown(markdown_document)
        docs = self.split_text(md_header_splits)
        return docs

    def find_metadata_indices(self, lines):
        start_index = end_index = None
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if start_index is None:
                    start_index = i
                else:
                    end_index = i
                    break
        return start_index, end_index

    def exclude_metadata(self, lines, start_index, end_index):
        if start_index is not None and end_index is not None:
            return ''.join(lines[end_index + 1:])
        else:
            return ''.join(lines)

    def split_markdown(self, markdown_document):
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=self.headers_to_split_on)
        return markdown_splitter.split_text(markdown_document)

    def split_text(self, md_header_splits):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        return text_splitter.split_documents(md_header_splits)

class folderContent (BaseModel):
    folder: str

# Function to initialize vector store
async def initialize_vector_store(folder: str):
    try:
        documents_markdown = MarkdownFileProcessor(folder)
        all_docs = documents_markdown.process_files()

        # Create the vector store in Chroma
        vector_store = Chroma.from_documents(
            documents=all_docs,  
            embedding=OpenAIEmbeddings()
        )
        logger.info("Vector store initialized")
        return vector_store
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Define async context manager for lifespan
@asynccontextmanager
async def lifespan(app):
    global vector_store
    folder = '/home/santiago/app/nextjs-fastapi-your-chat/api/curso_creatividad'
    logger.info(f"Initializing vector store from folder: {folder}")

    vector_store = await initialize_vector_store(folder)
    try:
        yield
    finally:
        # Clean up the vector store and release resources if needed
        logger.info("Shutting down vector store")
        # Clean up code here if needed

# Pass the lifespan async context manager to FastAPI
app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str


@app.post("/api/chat")
async def chat(request: ChatRequest):
    global chat_history, vector_store
    if vector_store is None:
        raise HTTPException(status_code=404, detail="Vector store not found")

    try:
        user_message = HumanMessage(content=request.message)

        retriever_chain = get_context_retriever_chain(vector_store)
        conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

        logger.info(f"User message: {user_message.content}")
        logger.info(f"Chat history: {chat_history}")
        response = conversation_rag_chain.invoke(
            {"chat_history": chat_history, "input": user_message}
        )

        chat_history.append(user_message)

        ai_message = AIMessage(content=response["answer"])
        chat_history.append(ai_message)

        return response["answer"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_context_retriever_chain(vector_store):
    logger.info("Creating context retriever chain")
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            (
                "user",
                "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation",
            ),
        ]
    )

    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

    return retriever_chain


def get_conversational_rag_chain(retriever_chain):

    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the user's questions based on the below context:\n\n{context}",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ]
    )

    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)




if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
