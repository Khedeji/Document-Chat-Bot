import os
import sqlite3
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss

def add_session(session_id):
    conn = sqlite3.connect('sessions.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO sessions (id) VALUES (?)', (session_id,))
    conn.commit()
    conn.close()

def get_all_sessions():
    conn = sqlite3.connect('sessions.db')
    c = conn.cursor()
    c.execute('SELECT id FROM sessions')
    sessions = [row[0] for row in c.fetchall()]
    conn.close()
    return sessions

def retrieve_context(query, k=4):
    vectorstore = get_vectorstore()
    if not vectorstore:
        return ""
    docs = vectorstore.similarity_search_with_score(query, k=k)
    docs = [doc for doc, score in docs]
    return "\n\n".join([d.page_content for d in docs])

def get_vectorstore():
    if not os.path.exists("faiss_index"):
        docs = []
        if os.path.exists("Full_Employee_Report.pdf"):
            docs.extend(PyMuPDFLoader("Full_Employee_Report.pdf").load())
        if not docs:
            return None
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)
        embeddings = OllamaEmbeddings(model='nomic-embed-text', base_url='http://20.20.20.202:11434')
        vector = embeddings.embed_query("Hello World this is a test")
        index = faiss.IndexFlatL2(len(vector))
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        ids = vector_store.add_documents(documents=splits)
        vector_store.save_local("faiss_index")
        return vector_store
    else:
        embeddings = OllamaEmbeddings(model='nomic-embed-text', base_url='http://20.20.20.202:11434')
        vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        if not vectorstore:
            docs = []
            if os.path.exists("Full_Employee_Report.pdf"):
                docs.extend(PyMuPDFLoader("Full_Employee_Report.pdf").load())
            if not docs:
                return None
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
            splits = text_splitter.split_documents(docs)
            vector = embeddings.embed_query("Hello World this is a test")
            index = faiss.IndexFlatL2(len(vector))
            vectorstore = FAISS(
                embedding_function=embeddings,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )
            ids = vectorstore.add_documents(documents=splits)
            vectorstore.save_local("faiss_index")
        return vectorstore

def get_chat_history(session_id: str = "default_session"):
    history = SQLChatMessageHistory(session_id, "sqlite:///chat_history.db")
    return history
