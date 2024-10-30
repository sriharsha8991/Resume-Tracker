import streamlit as st
import os
import pandas as pd
from pdfminer.high_level import extract_text

def read_resumes_from_directory(directory_path):
    resumes = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory_path, filename)
            text = extract_text(file_path)
            resumes.append({'name': filename, 'text': text})
    return resumes

def display_resumes(directory):
    st.title("Process Top Resumes")
    if directory:
        resumes = read_resumes_from_directory(directory)
        for resume in resumes:
            st.subheader(resume['name'])
            st.write(resume['text'])

def main():
    top_resumes_directory = "top_resumes"
    if st.sidebar.button("Load Resumes"):
        display_resumes(top_resumes_directory)

if __name__ == "__main__":
    main()
