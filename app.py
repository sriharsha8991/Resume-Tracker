import streamlit as st

def main():
    st.set_page_config(page_title="Resume Filtering System", layout="wide")
    
    st.title("Welcome to the Resume Filtering System 🌟")

    st.markdown("""
        ## Overview
        This application assists HR professionals in filtering and processing resumes efficiently. 
        Utilize the navigation on the left to switch between the various features of the application:
        
        - **Filter Resumes**: Upload and filter resumes based on job descriptions to find the top candidates. 🔍
        - **Process Top Resumes**: Review and further process the resumes that have been ranked highest by the filter system. 📂
        
        ## Features
        - **Automated Resume Filtering**: Automatically ranks resumes based on their relevance to the job description provided. 🤖
        - **Resume Ranking Visualization**: Visualize the ranking and scoring of each resume. 📊
        - **Top Resume Management**: View and manage the resumes that have been identified as top candidates. 🏆
        - **Top Candidate Analysis**: Analyse the Candidate Strengths and weakness before the interview from the resume 🔍
        
        ## How to Navigate
        Use the left sidebar to navigate between the different pages of the application. Each page is dedicated to a specific function, allowing you to focus on one task at a time.
        
        ## Further Information
        This tool is built to streamline the initial phases of the recruitment process, helping you to focus on engaging with the most promising candidates. 🚀
    """)

if __name__ == "__main__":
    main()
