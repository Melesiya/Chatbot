from flask import Flask, request, jsonify
from langdetect import detect
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
import os
from flask import render_template
from flask_cors import CORS 

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Set up environment variables (ensure these are managed securely)
os.environ["OPENAI_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "MilaProject"

# Initialize ChatOpenAI instance
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

# Function to load PDFs and chunk by page
def load_pdf(file_path):
    pdf_reader = PyPDFLoader(file_path)
    return pdf_reader.load_and_split()

# Initialize vector store retriever
pdf_files_eng = [
    "Accounts_Eng.pdf", "ATMs_Eng.pdf","Credit Cards_Eng.pdf",
    "Debit cards_Eng.pdf", "Mobile - Online banking_Eng.pdf"
]

pdf_files_ar = [
    "Accounts_Ar.pdf", "ATMs_Ar.pdf",
    "Credit Cards_Ar.pdf", "Debit cards_Ar.pdf","Mobile - Online banking_Ar.pdf"
]

# Load English documents
documents_eng = []
for file_name in pdf_files_eng:
    file_path = os.path.join(r"C:\Users\DELL\Desktop\M_Project", file_name)
    pages = load_pdf(file_path)
    documents_eng.extend(pages)

# Load Arabic documents
documents_ar = []
for file_name in pdf_files_ar:
    file_path = os.path.join(r"C:\Users\DELL\Desktop\M_Project", file_name)
    pages = load_pdf(file_path)
    documents_ar.extend(pages)

# Create embeddings for English and Arabic documents separately
embeddings = OpenAIEmbeddings()
vector_store_eng = Chroma.from_documents(documents=documents_eng, embedding=embeddings)
vector_store_ar = Chroma.from_documents(documents=documents_ar, embedding=embeddings)

# Route to handle incoming chat messages
@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        user_message = data['message']

        # Detect language of user input
        lang = detect(user_message)

        # Determine response language context
        if lang == "en":
            retriever = VectorStoreRetriever(vectorstore=vector_store_eng)
        else:
            retriever = VectorStoreRetriever(vectorstore=vector_store_ar)

        # Create a new runnable chain for each new input
        rag_chain = create_rag_chain()

        # Retrieve relevant documents based on user input
        relevant_documents = retriever.get_relevant_documents(user_message)

        # Construct the input dictionary
        input_dict = {"context": relevant_documents, "question": user_message}

        # Apply each step of the function chain separately
        prompt_response = rag_chain.invoke(input_dict)
        response_text = prompt_response

        return jsonify({'message': response_text})

    except Exception as e:
        return jsonify({'error': str(e)})

# Function to create a runnable chain
def create_rag_chain():
    prompt = """Use the following Context ONLY to get a concise Answer for the Question. 
    Be specific about your Answer.
    If the Question NOT RELATED to the Context, just say Appologies, I don't have an answer for that and ask if you want any further help.
    Respond with the same language as the Question.
    If the Question is Hello or Hi, respond with Hi, how can I help you?
    Context: {context}
    Question: {question}
    Answer:"""

    return (
        RunnableLambda(lambda x: prompt.format(question=x["question"], context=x["context"]))
        | llm
        | StrOutputParser()
    )

@app.route('/')
def index():
    return render_template('index.html')