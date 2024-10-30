import os
import streamlit as st
from operator import itemgetter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.vectorstores import Qdrant
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain.schema import format_document
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()
target_directory = "top_resumes"
def save_analysis_report(text, filename):
    """Save the analysis report into a text file."""
    with open(filename, 'w') as file:
        file.write(text)

st.title("Analyse the Top Candidates CVs")
loader = PyPDFDirectoryLoader("top_resumes")
docs = loader.load()
# print(len(docs))
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# create a qdrant collection - a vector based index of all resumes
qdrant_collection = Qdrant.from_documents(
docs,
embeddings,
location=":memory:", # Local mode with in-memory storage only
collection_name="it_resumes",
)
# construct a retriever on top of the vector store
qdrant_retriever = qdrant_collection.as_retriever()

template = """You are a helpful assistant to a recruiter at a technology firm. You are be provided the following input context \
from a dataset of resumes of IT professionals who has the top ATS scores.
- Answer the question based only on the context. Also provide the source documents with best match based on Job Description.
-for each resume, give in one point about the Strengths based on the Job Description to give better understanding for the interviewer.
{resume}
Job Description: {question}
<important >Make sure to follow below output structure every time and no extra unwanted information should be given other than  the below requested ones<important>
Output:<follow it strictly>
### Candidate Analysis
1. **Candidate 1**
- **Source Document:**
- **Strengths:**
- **Weak areas:**
\n
2. **Candidate 2**
- **Source Document:**
- **Strength:**
- **Weak areas:**
\n
As many candidates as the number of resume docs 
"""
prompt = ChatPromptTemplate.from_template(template)

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
)
# Construct the chain, with two variables - resume and question to be passed onto the prompt.
chain = (
{"resume": RunnablePassthrough()|qdrant_retriever, "question": RunnablePassthrough()}
| prompt
| llm
| StrOutputParser()
)
job_desc = st.text_area("Enter Job Description")
if st.button("Analyse top candidates"):
    with st.spinner('Analysing...'):
        result_docs = chain.invoke(job_desc)
        st.write(result_docs[:])
        report_filename = os.path.join(target_directory, "analysis_report.txt")
        save_analysis_report(result_docs, report_filename)
        st.success(f"Analysis report has been saved to {report_filename}")