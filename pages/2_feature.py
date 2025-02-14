import os
import streamlit as st
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Qdrant
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
target_directory = "top_resumes"

def save_analysis_report(text, filename):
    with open(filename, 'w') as file:
        file.write(text)

def main():
    st.title("Analyse the Top Candidates CVs")
    
    try:
        loader = PyPDFDirectoryLoader("top_resumes")
        docs = loader.load()
        
        if docs:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            
            qdrant_collection = Qdrant.from_documents(
                docs,
                embeddings,
                location=":memory:",
                collection_name="it_resumes",
            )
            
            qdrant_retriever = qdrant_collection.as_retriever()
            
            template = """You are a helpful assistant to a recruiter at a technology firm. Answer the question based only on the context from IT professionals' resumes with top ATS scores. Provide source documents with best match based on Job Description and give one strength point per resume based on the Job Description for interviewer understanding.

{resume}
Job Description: {question}

Output:
### Candidate Analysis
1. **Candidate 1**
- **Source Document:**
- **Strengths:**
- **Weak areas:**

2. **Candidate 2**
- **Source Document:**
- **Strength:**
- **Weak areas:**

[Continue for all candidates]"""
            
            prompt = ChatPromptTemplate.from_template(template)
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
            )
            
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
        else:
            st.error("No documents found in the top_resumes directory")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()