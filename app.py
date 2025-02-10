import streamlit as st
import os

def main():
    st.set_page_config(page_title="Resume Analysis System", layout="wide")
    
    st.title("Advanced Resume Analysis System 🚀")
    
    st.markdown("""
        ## System Features
        
        ### Core Features
        - Resume filtering and ranking
        - ATS score calculation
        - PDF text extraction
        - Email notifications
        
        ### Advanced AI Analysis
        - 🎯 Skills Gap Analysis
        - 💰 Market Salary Analysis
        - 📝 Interview Question Generator
        
        ### Requirements
        - PDF format resumes
        - Internet connection
        - API access (for AI features)
    """)
    
    st.sidebar.success("System Status: Ready")
    if os.path.exists("top_resumes"):
        filtered_count = len([f for f in os.listdir("top_resumes") if f.endswith('.pdf')])
        st.sidebar.metric("Processed Resumes", filtered_count)

if __name__ == "__main__":
    main()