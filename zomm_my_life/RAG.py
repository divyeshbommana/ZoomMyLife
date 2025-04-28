from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
import pandas as pd
from operator import itemgetter

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
CORS(app)  # Enable CORS

def initalize_environment():
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
    os.environ['LANGCHAIN_API_KEY'] = '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'
    os.environ['GROQ_API_KEY'] = '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'

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

def split_docs(docs):

    print("Splitting Documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    # Embed with HuggingFace
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=HuggingFaceEmbeddings(model_name="aspire/acge_text_embedding")
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever

def get_groq_model():

    print('Getting Groq model...')

    medical_template = """
        You are a medical recommendation system. Speak directly to the user using words such as 'you' 
        Use the following context to provide safe, evidence-based recommendations.

        Context: {context}

        User Profile:
        {user_data}

        Question: {question}

        Consider the user's profile and provide:
        1. Three personalized recommendations
        2. Potential risks based on their data

        Answer in this structure:
        - Answer to the question

        - **Recommendations**
        - [Rec 1]
        - [Rec 2]
        - [Rec 3]

        - **Risk Assessment**
        - [Risk 1]
        - [Risk 2]
        """
    medical_prompt = ChatPromptTemplate.from_template(medical_template)

    general_template = """You are a helpful assistant. Answer the following question concisely:
    Question: {question}"""
    general_prompt = ChatPromptTemplate.from_template(general_template)

    # Groq LLM
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",  # Groq model name
        temperature=0
    )

    return llm, medical_prompt, general_prompt

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

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

general_chain = (
    {"question": RunnablePassthrough()}
    | general_prompt
    | llm
    | StrOutputParser()
)



def getData(file_location):

    print(f'data_path: {file_location}')
    df = pd.read_csv(file_location)    
    return df

@app.route('/cipher', methods=['POST'])
def cipher():

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

    # text = str(data.get('messages', ''))
    # print(str(text))
    
    return jsonify({'original': original_text, 'ciphered': answer})

if __name__ == '__main__':
    app.run(debug=True)