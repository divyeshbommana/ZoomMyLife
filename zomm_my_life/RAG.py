from flask import Flask, request, jsonify
from flask_cors import CORS
import os

import bs4
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq  # Groq
from langchain_community.embeddings import HuggingFaceEmbeddings



app = Flask(__name__)
CORS(app)  # Enable CORS

def initalize_environment():
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
    os.environ['LANGCHAIN_API_KEY'] = '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'
    os.environ['GROQ_API_KEY'] = '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'

def get_docs():
    med_loader = WebBaseLoader(
    web_paths=("http://www.ncbi.nlm.nih.gov/pubmed/15858239",
                # "http://www.ncbi.nlm.nih.gov/pubmed/20598273",
                # "http://www.ncbi.nlm.nih.gov/pubmed/6650562",
                # "http://www.ncbi.nlm.nih.gov/pubmed/12239580",
                # "http://www.ncbi.nlm.nih.gov/pubmed/21995290",
                # "http://www.ncbi.nlm.nih.gov/pubmed/23001136",
                # "http://www.ncbi.nlm.nih.gov/pubmed/15617541",
                # "http://www.ncbi.nlm.nih.gov/pubmed/8896569",
                "http://www.ncbi.nlm.nih.gov/pubmed/15829955"),
        bs_kwargs=dict(
            parse_only=bs4.SoupStrainer(
                class_=("heading", "abstract")
            )
        ),
    )

    docs = med_loader.load()

    return docs

def split_docs(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # Embed with HuggingFace
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=HuggingFaceEmbeddings(model_name="aspire/acge_text_embedding")
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever

def get_groq_model():
    prompt = hub.pull("rlm/rag-prompt")

    # Groq LLM
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",  # Groq model name
        temperature=0
    )

    return llm, prompt

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def answer_question(question):
    return rag_chain.invoke(question)

# Use regular llm without retriever
def answer_question_no_rag(question):
    return llm.invoke(question)

initalize_environment()
docs = get_docs()
retriever = split_docs(docs)
llm, prompt = get_groq_model()

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


@app.route('/cipher', methods=['POST'])
def cipher():

    
    data = request.get_json()
    original_text = data.get('text', '')
    answer = answer_question(original_text)

    answer_no_rag = str(answer_question_no_rag(original_text).content)
    return jsonify({'original': original_text, 'ciphered': answer})

if __name__ == '__main__':
    app.run(debug=True)