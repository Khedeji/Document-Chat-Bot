from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder, ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
def retrieve_context(question):
    # Dummy implementation, replace with actual context retrieval logic
    return "This is the context for the question."

def Greeting_Chain(user_input):
    print("Greeting Chain Called")
    llm = ChatOllama(base_url="http://localhost:11434", model='mistral', project_name="chatbot")
    Greeting_Prompt = f"""If the user greets, respond politely. If the user says thanks or goodbye, respond with a polite closure. 
    User Input: {user_input}
    Response: 
    
    """
    Greeting_chain = Greeting_Prompt | llm | StrOutputParser()
    return Greeting_chain

def Error_Chain(user_input):
    print("Error Chain Called")
    Error_Prompt = f"""If the answer is not in the context, say: 'This question is not covered in the document, so I'm unable to answer it. 
    Please let me know if you have any other questions.' 
    User Input: {user_input}
    Response:
    
    """
    llm = ChatOllama(base_url="http://localhost:11434", model='mistral', project_name="chatbot")
    Error_chain = Error_Prompt | llm | StrOutputParser()
    return Error_chain

def Answer_Chain(context, question):
    print("Answer Chain Called")
    system = SystemMessagePromptTemplate.from_template(
        "You are an AI assistant who answers users' questions only on the basis of the provided context. "
        "If the user greets, respond politely. If the user says thanks or goodbye, respond with a polite closure."
        "If the answer is not in the context, say: 'This question is not covered in the document, so I'm unable to answer it. "
        "Please let me know if you have any other questions.' "
    )
    prompt = HumanMessagePromptTemplate.from_template(f"Context:\n{context}\n\nQuestion:\n{question}")
    messages = [system, MessagesPlaceholder(variable_name="history"), prompt]
    template = ChatPromptTemplate(messages)
    llm = ChatOllama(base_url="http://localhost:11434", model='mistral', project_name="chatbot")
    Answer_chain = template | llm | StrOutputParser()
    return Answer_chain


def  decide_context_scope(user_input):
    # Dummy implementation, replace with actual logic to decide which chain to use
    print("Deciding context scope based on user input")
    template = ChatPromptTemplate.from_template(
        "You are an AI classifier who classify user questions on basis of requirement "
        "first you need to analyze the user_input"
        "then"
        "If the user_input is involving any specific information or context,which can be answered by similarty searching  Classify it as 'vector' "
        "for example,  'What is the employee detail?' or tell me about this topic or give this detial etc"
        "If the user_input is involving any query ,which can be required to load whole vector database classify it as 'non-vector' "
        "for example, 'how many are in this ' or 'summarize the topic' or someone asks about 'starting of data' and 'someone ask end' or 'tell me about all from <topic>'  or give me all etc"
        "User Input: {user_input}   " 
        "Classify as 'vector' or 'non-vector' based on the user input."
        
    )
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    classification_chain = template | llm | StrOutputParser()
    result = classification_chain.invoke({"user_input": user_input})
    return result

def rout(result):
    if 'greeting' in result["sentiment"].lower() or 'hello' in result["sentiment"].lower() or 'hi' in result["sentiment"].lower():
        return Greeting_Chain(result['question'])
    elif 'error' in result["sentiment"].lower() or 'not covered' in result["sentiment"].lower():
        return Error_Chain(result['question'])
    else:
        context = retrieve_context(result['question'])
        if not context.strip():
            return Error_Chain(result['question'])
        return Answer_Chain(context, result['question'])