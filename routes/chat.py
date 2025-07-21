from flask import Blueprint, request, jsonify
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory,RunnableLambda
from .shared import retrieve_context, add_session, get_chat_history
from .Chain_Route import rout
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
            context = retrieve_context(user_message,5)
            

            # if not context.strip():
            #     return jsonify({'reply': "This question is not covered in the document, so I'm unable to answer it. Please let me know if you have any other questions."})



            system = SystemMessagePromptTemplate.from_template(
                "You are an AI assistant who answers users' questions only on the basis of the provided context. "
                "Context:\n{context}\n\n"
                "If the user greets like (Hii, Hello GM GN etc), clasify 'Greeting'. If the user says thanks or goodbye or wow or express some feeelings, clasify 'Greeting'. respond politely. If the user says thanks or goodbye, respond with any polite closure statement."
                "If the user question cannot be answered from the context or on comparing input and context, you found not similer or replyable say: 'This question is not covered in the document, so I'm unable to answer it. "
                "Please let me know if you have any other questions.' "
                "if user input is can be answered from given context , then respond with the answer based on the context."
                
                
            )
            prompt = HumanMessagePromptTemplate.from_template("Question:\n{question}")
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
