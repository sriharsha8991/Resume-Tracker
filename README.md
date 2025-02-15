# Resume Filtering System Documentation 

## Overview 

The Resume Filtering System is a Streamlit-based application designed to simplify the recruitment process for HR professionals. The system allows users to filter, analyze, and manage resumes efficiently using advanced Natural Language Processing (NLP) techniques and data-driven insights. 

## Key Features 

- **Automated Resume Filtering and Ranking**
Upload resumes (in PDF format), compare them against a job description using TF-IDF and cosine similarity, and rank the resumes based on relevance. 

- **Top Resumes Processing**
Copy and manage the top-ranked resumes into a dedicated folder (top_resumes) for further review. 

- **Feature Analysis** 
Analyze candidate skills via NLP using spaCy, computation of technical proficiency scores, and identification of strengths and areas for improvement. 

- **Market Salary Analysis** 
Generate comprehensive compensation analysis reports using an AI agent. The system integrates with external tools (e.g., Gemini, DuckDuckGoTools) to provide market insights and recommendations. 

- **Interview Question Generation** 
Automatically generate a set of role-specific interview questions including technical, behavioral, and scenario-based queries. 

- **Email Management** 
Send acceptance or rejection emails to candidates directly from the application using SMTP integration. 

- **Resume Visualizations** 
Visualize candidate analysis results with interactive charts using Plotly and Matplotlib. This includes bar charts for technical proficiency, pie charts for skills distribution, and radar charts for individual candidate analysis. 

## Project Structure 

The project is segmented into several key modules and pages: 

### Main Application Files 

- **app.py** 
Provides an overview and navigation through the different functionalities. There are two versions:  

- **User-Facing Overview:** 
Located at /Resume-Tracker/app.py, it displays system features and provides navigation instructions. 

- **Salary Analysis Entry Point:** 
Located at /Resume-Tracker/src/app.py, it manages salary analysis by rendering UI components and integrating with the salary research agent. 

### Pages 

Each page in the pages/ directory handles a specific functionality: 

- **1_ats_resume.py**
Implements resume filtering and ranking. It uses spaCy and scikit-learn to process resumes and compute their similarity with a job description. 

- **2_feature.py**
Analyzes the top resumes using document loaders and vector embeddings, integrates with Qdrant for similarity search, and generates analysis reports. 

- **3_top_cvs.py** 
Reads PDF resumes from the top_resumes directory, extracts text with PyPDF2, and displays the content for further processing. 

- **4_email_handler_page.py** 
Manages email operations where HR can send status emails (acceptance/rejection) to candidates. 

- **5_question_generation.py**
Generates interview questions based on the candidate resume and job description, utilizing a Groq client for AI-driven content. 

- **6_visualization.py**
Provides detailed candidate analysis and comparison using Plotly for interactive charts and visual insights. 

- **7_Market_Salary_Analysis.py**
Integrates with a Salary Research Agent to generate comprehensive compensation analysis reports. 

### Source Modules 

- **src/ui_components.py**
Contains the header rendering and input form components used in the salary analysis section. 

- **src/config.py**
Stores configuration data such as app titles, industry sectors, skills by category, and analysis parameters. 

### Utility Modules 

- **utils/pdf_processor.py** 
Handles PDF text extraction and text processing using spaCy. 

- **utils/question_generator.py**
Implements interview question generation using Groq’s AI services. 

- **utils/email_handler.py**
Manages email sending functionalities using SMTP and handles both acceptance and rejection emails. 

- **utils/ai_analyzer.py** 
Provides utilities for advanced candidate analysis including Named Entity Recognition (NER), proficiency scoring, strengths/gap identification, and salary analysis using external AI models. 

- **utils/__init__.py** 
Acts as a package initializer for utility functions. 

### Additional Files 

- **.env **
Contains environment variables for API keys and SMTP credentials. 

- **requirements.txt** 
Lists all Python dependencies required for the project. 

- **.gitignore** 
Specifies files and directories ignored by Git. 

### Installation & Setup 

1. Clone the Repository 

git clone <repository_link> 

cd Resume-Tracker 

2. Install Dependencies 

pip install -r requirements.txt 

3. Download spaCy Model 

python -m spacy download en_core_web_sm 

4. Setup Environment Variables 

Update the .env file with your API keys and email credentials. 

Running the Application 

Start the application using Streamlit: 

streamlit run app.py 

Navigate through the application using the left sidebar to access different functionalities such as resume filtering, market salary analysis, interview question generation, email management, and visualizations. 

### Usage Scenarios 

- **Resume Filtering** 

HR professionals can upload a set of resumes, define a job description, and filter out the top candidates based on textual similarity. 

- **Market Salary Analysis**

Analyze compensation details for roles and generate full reports with actionable insights. 

- **Candidate Interview Preparation**

Generate role-specific interview questions to assist hiring managers in candidate screening. 

- **Candidate Follow-Up** 

Manage email communications with candidates for interview scheduling or application updates. 

- **Security & Best Practices** 

Sensitive Information 

Ensure credentials like API keys and SMTP passwords stored in .env are kept secure and not exposed in public repositories. 

Modularity 

The project is designed with modularity in mind. Each functionality is isolated into its own module or page to simplify development, testing, and maintenance. 

### Summary 

The Resume Filtering System integrates several advanced components such as NLP-driven resume ranking, AI-powered salary analysis, interactive data visualizations, and automated email management. This comprehensive system streamlines recruitment workflows and improves candidate shortlisting efficiency. 

For further details and technical support, please refer to the inline documentation in each module or contact the development team. 

 