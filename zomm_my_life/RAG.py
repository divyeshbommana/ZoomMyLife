from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
import pandas as pd
from operator import itemgetter
import yaml

import bs4
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq  # Groq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader


app = Flask(__name__)
CORS(app)

# Load yml file with API Keys
def load_keys(file_location):
    with open(file_location, 'r') as f:
        keys = yaml.safe_load(f)
    return keys

# Initalize environmental variables from .yml file
def initalize_environment():

    config = load_keys('API_KEYS.yml')

    os.environ['LANGCHAIN_TRACING_V2'] = config['LANGCHAIN_TRACING_V2']
    os.environ['LANGCHAIN_ENDPOINT'] = config['LANGCHAIN_ENDPOINT']
    os.environ['LANGCHAIN_API_KEY'] = config['LANGCHAIN_API_KEY']
    os.environ['GROQ_API_KEY'] = config['GROQ_API_KEY']

# Loads in the document
def get_docs():
    # med_loader = WebBaseLoader(
    # web_paths=("http://www.n cbi.nlm.nih.gov/pubmed/15858239",
    #             # "http://www.ncbi.nlm.nih.gov/pubmed/20598273",
    #             # "http://www.ncbi.nlm.nih.gov/pubmed/6650562",
    #             # "http://www.ncbi.nlm.nih.gov/pubmed/12239580",
    #             # "http://www.ncbi.nlm.nih.gov/pubmed/21995290",
    #             # "http://www.ncbi.nlm.nih.gov/pubmed/23001136",
    #             # "http://www.ncbi.nlm.nih.gov/pubmed/15617541",
    #             # "http://www.ncbi.nlm.nih.gov/pubmed/8896569",
    #             "https://www.dietaryguidelines.gov/sites/default/files/2024-12/Scientific_Report_of_the_2025_Dietary_Guidelines_Advisory_Committee_508c.pdf"),
    #     bs_kwargs=dict(
    #         parse_only=bs4.SoupStrainer(
    #             class_=("heading", "abstract")
    #         )
    #     ),
    # )

    print("Loading in medical document...")
    med_loader = PyPDFLoader(f'./Scientific Report of the 2025 Dietary Guidelines Advisory Committee_sample_15.pdf')

    docs = med_loader.load()

    return docs

# Splits document into chucks of 1000 with an overlap of 100
def split_docs(docs):

    print("Splitting Documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    # Embed with HuggingFace
    print("Embedding Split Documents...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=HuggingFaceEmbeddings(model_name="aspire/acge_text_embedding")
    )

    # Defines a retriever that gets 3 closest documents
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever

# Gets medical/non-medical prompts and groq llm model
def get_groq_model():

    print('Getting Groq model...')

    # Initilizes the prompt template for medical related questions
    medical_template = """
        You are a medical recommendation system. Speak directly to the user using words such as 'you' 
        Use the following context to provide safe, evidence-based recommendations.

        For the user data, the data near the top signifies the most recent inputs. 

        Context: {context}

        User Profile:
        {user_data}

        Question: {question}

        If a health question can be answered without using the user's profile, do so without providing any recommendations or risks
        
        If not, consider the user's profile and provide:
        1. Three personalized recommendations
        2. Potential risks based on their data

        Answer in this structure:
        - Answer to the question

        (Include only if necessary)
        - **Recommendations**
        - [Rec 1]
        - [Rec 2]
        - [Rec 3]

        - **Risk Assessment**
        - [Risk 1]
        - [Risk 2]
        """
    medical_prompt = ChatPromptTemplate.from_template(medical_template)

    # Initilizes the prompt template for non-medical related questions
    general_template = """You are a helpful assistant. Answer the following question concisely:
    Question: {question}"""
    general_prompt = ChatPromptTemplate.from_template(general_template)

    # Initilizes Groq LLM
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",  # Groq model name
        temperature=0
    )

    return llm, medical_prompt, general_prompt

# Formats the documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Check if question is health related
def is_health_related(question, llm):
    classifier_prompt = ChatPromptTemplate.from_template(
        "Classify the following question into 'health' or 'general'. "
        "Respond only with 'health' or 'general'.\nQuestion: {question}"
    )
    classifier_chain = classifier_prompt | llm | StrOutputParser()
    response = classifier_chain.invoke({"question": question})
    return response.strip().lower() == 'health'


# Use regular llm without retriever
def answer_question_no_rag(question):
    return llm.invoke(question)

initalize_environment()
docs = get_docs()
retriever = split_docs(docs)
llm, medical_prompt, general_prompt = get_groq_model()

# Initilizes the medical chain pipeline
medical_chain = (
    {
        "context": itemgetter("question") | retriever | format_docs,
        "question": itemgetter("question"),
        "user_data": itemgetter("user_data")
    }
    | medical_prompt
    | llm
    | StrOutputParser()
)

# Initilizes the non-medical chain pipeline
general_chain = (
    {"question": RunnablePassthrough()}
    | general_prompt
    | llm
    | StrOutputParser()
)

# Gets user data
def getData(file_location):

    print(f'data_path: {file_location}')
    df = pd.read_csv(file_location)    
    return df

# Main code
@app.route('/RAG', methods=['POST'])
def RAG():

    data = request.get_json()
    original_text = data.get('text', '')
    file_location = data.get('file_location', '')

    health_related = is_health_related(original_text, llm)

    if health_related:

        user_data = getData(file_location)
        print(user_data)

        input_dict = {
            "question": original_text,
            "user_data": user_data.to_markdown()
        }
        answer = medical_chain.invoke(input_dict)
    else:
        answer = general_chain.invoke(original_text)

    return jsonify({'original': original_text, 'response': answer})

if __name__ == '__main__':
    app.run(debug=False)