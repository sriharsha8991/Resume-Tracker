import streamlit as st
import pickle
import re
from pdfminer.high_level import extract_text
import numpy as np
import pandas as pd
from io import StringIO
import base64

# ------------------- Helper Functions -------------------
def load_model(model_file):
    """Loads a pickled model."""
    try:
        with open(model_file, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file with progress bar."""
    try:
        with st.spinner('Extracting text from PDF...'):
            text = extract_text(pdf_file)
            if text.strip():
                st.success("PDF text extraction successful!")
                return text
            else:
                st.warning("The PDF appears to be empty or unreadable")
                return None
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def preprocess_text(text):
    """Preprocess the resume text."""
    with st.spinner('Preprocessing text...'):
        # Remove special characters and convert to lowercase
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

def predict_category(resume_text, vectorizer, model):
    """Predicts the job category with confidence scores."""
    cleaned_resume = preprocess_text(resume_text)
    X_tfidf = vectorizer.transform([cleaned_resume])
    
    # Get prediction and probabilities
    prediction = model.predict(X_tfidf)[0]
    probabilities = model.predict_proba(X_tfidf)[0]
    
    # Create dictionary of class probabilities
    class_probs = dict(zip(model.classes_, probabilities))
    return prediction, class_probs

def create_download_link(text):
    """Generate a download link for text content"""
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="resume_text.txt">Download extracted text</a>'

def main():
    st.set_page_config(layout="wide")
    
    st.markdown("""
        <style>
        .main { padding: 2rem; }
        .stButton>button { width: 100%; margin-top: 1rem; }
        .upload-section {
            padding: 1.5rem;
            border-radius: 8px;
            border: 2px dashed #4CAF50;
            margin-bottom: 1rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 4px;
            padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4CAF50 !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🎯 Smart Resume Classifier")
    
    # Load models first
    try:
        with st.spinner("Loading models..."):
            model = load_model(r'pages\resume_classifier_model.pkl')
            vectorizer = load_model(r'pages\tfidf_vectorizer (2).pkl')
            if not (model and vectorizer):
                st.error("❌ Error loading models")
                st.stop()
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()

    # Main tabs
    input_tab, preview_tab, results_tab = st.tabs(["📥 Input Resume", "👀 Document Preview", "📊 Classification Results"])
    
    with input_tab:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📄 File Upload")
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Drag and drop your resume (PDF/TXT)",
                type=["txt", "pdf"],
                help="Supported formats: PDF, TXT"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("### ✍️ Manual Input")
            manual_text = st.text_area(
                "Paste resume content here",
                height=250,
                help="Copy and paste the resume content if you don't have a file"
            )

        resume_text = None
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                resume_text = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
        elif manual_text:
            resume_text = manual_text

        if resume_text:
            st.success("Resume text loaded successfully!")
            st.session_state['resume_text'] = resume_text
            if st.button("👉 Classify Resume", key="classify_btn", use_container_width=True):
                try:
                    prediction, class_probabilities = predict_category(resume_text, vectorizer, model)
                    st.session_state['prediction'] = prediction
                    st.session_state['probabilities'] = class_probabilities
                except Exception as e:
                    st.error(f"An error occurred during classification: {str(e)}")

    with preview_tab:
        if 'resume_text' in st.session_state:
            st.markdown("### 📄 Document Content")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.text_area(
                    "Extracted Text",
                    value=st.session_state['resume_text'],
                    height=400,
                    disabled=True
                )
            
            with col2:
                st.markdown("### 🛠️ Actions")
                st.markdown(create_download_link(st.session_state['resume_text']), unsafe_allow_html=True)
                word_count = len(st.session_state['resume_text'].split())
                st.metric("Word Count", word_count)
                char_count = len(st.session_state['resume_text'])
                st.metric("Character Count", char_count)
        else:
            st.info("Upload or enter resume text to preview content")

    with results_tab:
        if 'prediction' in st.session_state:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎯 Primary Classification")
                prediction = st.session_state['prediction']
                probabilities = st.session_state['probabilities']
                
                # Create a styled box for the prediction
                st.markdown(f"""
                    <div style='padding: 20px; border-radius: 10px; background-color: #f0f2f6;'>
                        <h2 style='color: #4CAF50; margin: 0;'>{prediction}</h2>
                        <p style='margin: 10px 0 0 0;'>Confidence: {probabilities[prediction]*100:.2f}%</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.progress(probabilities[prediction])

            with col2:
                st.markdown("### 📊 Probability Distribution")
                prob_df = pd.DataFrame({
                    'Category': probabilities.keys(),
                    'Probability': [f"{v*100:.2f}%" for v in probabilities.values()]
                }).sort_values(by='Category')
                st.dataframe(prob_df, hide_index=True, use_container_width=True)
                
                # Add a download button for the results
                csv = prob_df.to_csv(index=False)
                st.download_button(
                    "Download Results CSV",
                    csv,
                    "classification_results.csv",
                    "text/csv",
                    key='download-csv'
                )
        else:
            st.info("Classify a resume to see results here")

if __name__ == "__main__":
    main()