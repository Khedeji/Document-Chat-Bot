from flask import Blueprint, request, jsonify
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory,RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage
from .shared import retrieve_context, add_session, get_chat_history,all_chunks_loader
from .Chain_Route import rout, decide_context_scope
import os
from langchain_google_genai import ChatGoogleGenerativeAI

class ChatHandler:
    bp = Blueprint('chat', __name__)

    

    

    @staticmethod
    @bp.route('/ChatHome', methods=['GET', 'POST'])
    def chat_home():
        if request.method == 'POST':
            data = request.get_json()
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id') or request.cookies.get('session_id') or request.headers.get('Session-Id') or 'default_session'
            add_session(session_id)
            os.environ['GOOGLE_API_KEY'] = "AIzaSyAoXIWqgGLgWypjsXw2j8MeN7qVP1PIV_Q"

            # llm = ChatOllama(base_url="http://20.20.20.202:11434", model='llama3', project_name="chatbot")
            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


            history = get_chat_history(session_id)
            if not history:
                history = []
            historydocs = ''
            for msg in history.messages:
                if isinstance(msg, HumanMessage):
                    historydocs += f"User: {msg.content}\n"
                elif isinstance(msg, AIMessage):
                    historydocs += f"Bot: {msg.content}\n"
            
            scope = decide_context_scope(user_message)
            if scope == 'vector':
                context = retrieve_context(user_message ,20)
            else:
                context = all_chunks_loader()
            context += f"\n\nPrevious Chat History:\n{historydocs}"
                
                
                
            # )
            system = SystemMessagePromptTemplate.from_template(
                    "You are an AI assistant that answers user questions strictly based on the context and chat history in summarized way.\n\n"
                    "Context may include retrieved documents and previous conversation.\n\n"
                    "- If the user greets (e.g., 'Hi', 'Hello', 'GM', 'GN'), Respond with proper wishing.(for eg. Hello, How can i assist you)\n"
                    "- If the user says 'Thanks', 'Bye', or expresses feelings (e.g., 'wow'), Respond with proper  Greeting reply Message or respond with polite closure message.\n"
                    "Use prior conversation to maintain continuity.\n"
                    "- If the user question is answerable from the context, give a summarized response.\n"
                    "- If the question can't be answered from context or history, reply: 'This question is not covered in the document, so I'm unable to answer it.'"
                )
            prompt = HumanMessagePromptTemplate.from_template("Context:\n{context}\n\n""Question:\n{question} " "\n\nAnswer:")
            messages = [system, MessagesPlaceholder(variable_name="history"), prompt]
            template = ChatPromptTemplate(messages)
            

            qna_chain = template | llm | StrOutputParser()
            qna_chain = RunnableWithMessageHistory(
                runnable=qna_chain,
                get_session_history=get_chat_history,
                input_messages_key="question",
                history_messages_key="history",
            )
            try:
                answer = qna_chain.invoke({'question': user_message, 'context': context}, config={'configurable': {'session_id': session_id}})
                return jsonify({'reply': str(answer)})
            except Exception as e:
                return jsonify({'reply': f'Error: {str(e)}'}), 500
        return 'Hello, Flask!'
