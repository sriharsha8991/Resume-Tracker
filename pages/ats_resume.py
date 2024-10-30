import streamlit as st
import os
import shutil
from pdfminer.high_level import extract_text
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import pandas as pd

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def process_text(text):
    """Process and tokenize text."""
    doc = nlp(text)
    return ' '.join([token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop])

def extract_text_from_pdf(file_path):
    """Extract text from a single PDF file."""
    return extract_text(file_path)

def read_resumes_from_directory(directory_path):
    """Read and extract text from all PDF files in a directory."""
    resumes = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory_path, filename)
            text = extract_text_from_pdf(file_path)
            resumes.append({'name': filename, 'path': file_path, 'text': text})
    return resumes

def compute_similarity(resumes, job_desc):
    """Compute TF-IDF vectorization and cosine similarity scores."""
    vectorizer = TfidfVectorizer()
    documents = [job_desc] + [resume['text'] for resume in resumes]
    tfidf_matrix = vectorizer.fit_transform(documents)
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    return cosine_sim.flatten()

def rank_resumes(resumes, job_desc):
    """Rank resumes based on cosine similarity scores with the job description."""
    scores = compute_similarity(resumes, job_desc)
    for index, resume in enumerate(resumes):
        resume['score'] = scores[index]
    ranked_resumes = sorted(resumes, key=lambda x: x['score'], reverse=True)
    return ranked_resumes

def save_top_resumes(top_resumes, target_dir):
    """Save top-ranked resumes to a specified directory."""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for resume in top_resumes:
        shutil.copy(resume['path'], os.path.join(target_dir, os.path.basename(resume['path'])))

# Streamlit App
def main():
    st.title("Resume Filtering System")
    
    # Specify directory for resumes
    resume_directory = st.text_input("Enter the directory where resumes are stored")
    job_desc = st.text_area("Enter Job Description")
    num_shortlist = st.number_input("Number of resumes to shortlist", min_value=1, value=5, step=1)
    target_directory = "top_resumes"

    if st.button("Analyze and Save Top Resumes"):
        if resume_directory and job_desc:
            resumes = read_resumes_from_directory(resume_directory)
            processed_job_desc = process_text(job_desc)
            ranked_resumes = rank_resumes(resumes, processed_job_desc)
            
            # Save top resumes
            top_resumes = ranked_resumes[:num_shortlist]
            if target_directory:
                save_top_resumes(top_resumes, target_directory)
                st.success(f"Top {num_shortlist} resumes have been saved to {target_directory}")
            
            # Display ranked resumes and plotting
            ranked_df = pd.DataFrame([(res['name'], res['score']*100) for res in ranked_resumes], columns=['Resume', 'Score']).sort_values(by="Score",ascending=False)
            st.write("Ranked Resumes Based on Keywords:")
            st.dataframe(ranked_df)
            plt.figure(figsize=(10, 8))
            plt.barh(ranked_df['Resume'], ranked_df['Score'], color='skyblue')
            plt.xlabel('Matching Score')
            plt.ylabel('Resume')
            plt.title('Resume Ranking Based on Keywords')
            plt.gca().invert_yaxis()
            st.pyplot(plt)

if __name__ == "__main__":
    main()
