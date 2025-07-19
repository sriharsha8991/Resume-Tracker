import streamlit as st
import os
import shutil
import PyPDF2
import spacy
import docx2txt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import List, Dict, Tuple, Optional
import hashlib
import pickle
import re
from collections import Counter
import io
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Target directory for storing top resumes
TARGET_DIRECTORY = "top_resumes"

@st.cache_resource
def load_nlp_model():
    """Cache the spaCy model to avoid reloading"""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        st.error("spaCy English model not found. Please run: python -m spacy download en_core_web_sm")
        return None

nlp = load_nlp_model()

class EnhancedResumeProcessor:
    def __init__(self):
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.target_directory = TARGET_DIRECTORY
        
        # Ensure target directory exists
        Path(self.target_directory).mkdir(exist_ok=True)
        
        # Define skill categories and keywords for better matching
        self.skill_categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'scala', 'kotlin'],
            'web_development': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'oracle', 'sqlite'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'data_science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'matplotlib', 'seaborn'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem-solving', 'analytical', 'creative'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'trello', 'figma', 'photoshop']
        }
        
        # Common section headers in resumes
        self.section_headers = {
            'experience': ['experience', 'work experience', 'employment', 'career', 'professional experience'],
            'education': ['education', 'academic', 'qualification', 'degree', 'university', 'college'],
            'skills': ['skills', 'technical skills', 'competencies', 'expertise', 'proficiencies'],
            'projects': ['projects', 'portfolio', 'work samples', 'achievements']
        }
    
    def clear_top_resumes_directory(self):
        """Clear the top_resumes directory before saving new results"""
        try:
            if os.path.exists(self.target_directory):
                for filename in os.listdir(self.target_directory):
                    file_path = os.path.join(self.target_directory, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                st.info(f"🧹 Cleared previous results from {self.target_directory}")
        except Exception as e:
            logger.error(f"Error clearing target directory: {e}")
    
    def save_uploaded_file_to_target(self, uploaded_file, target_filename: str) -> bool:
        """Save uploaded file to target directory"""
        try:
            target_path = os.path.join(self.target_directory, target_filename)
            
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            
            with open(target_path, "wb") as f:
                f.write(uploaded_file.read())
            
            return True
        except Exception as e:
            logger.error(f"Error saving file {target_filename}: {e}")
            return False
    
    def extract_text_from_uploaded_file(self, uploaded_file) -> str:
        """Extract text from uploaded files"""
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        try:
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            
            if file_extension == 'pdf':
                reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            elif file_extension == 'docx':
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file.flush()
                    text = docx2txt.process(tmp_file.name)
                    os.unlink(tmp_file.name)  # Clean up temp file
                return text
            elif file_extension == 'txt':
                return uploaded_file.read().decode('utf-8')
            else:
                st.error(f"Unsupported file format: {file_extension}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text from {uploaded_file.name}: {e}")
            return ""
    
    def extract_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract keywords by category from text"""
        text_lower = text.lower()
        extracted_keywords = {}
        
        for category, keywords in self.skill_categories.items():
            found_keywords = []
            for keyword in keywords:
                # Use word boundaries for exact matches
                if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower):
                    found_keywords.append(keyword)
            extracted_keywords[category] = found_keywords
        
        return extracted_keywords
    
    def extract_years_experience(self, text: str) -> int:
        """Extract years of experience from resume text"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
            r'experience\s*(?:of\s*)?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:field|industry)',
        ]
        
        years = 0
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                years = max(years, max([int(match) for match in matches]))
        
        return years
    
    def calculate_section_scores(self, resume_text: str, job_desc: str) -> Dict[str, float]:
        """Calculate scores for different resume sections"""
        resume_lower = resume_text.lower()
        job_lower = job_desc.lower()
        
        scores = {}
        
        # Extract job requirements
        job_keywords = self.extract_keywords(job_desc)
        resume_keywords = self.extract_keywords(resume_text)
        
        # Skills matching score (40% weight)
        total_job_skills = sum(len(skills) for skills in job_keywords.values())
        matched_skills = 0
        
        for category in job_keywords:
            job_skills_set = set(job_keywords[category])
            resume_skills_set = set(resume_keywords[category])
            matched_skills += len(job_skills_set.intersection(resume_skills_set))
        
        skills_score = (matched_skills / max(total_job_skills, 1)) * 100
        scores['skills'] = min(skills_score, 100)
        
        # Experience relevance score (25% weight)
        required_years = self.extract_years_experience(job_desc)
        candidate_years = self.extract_years_experience(resume_text)
        
        if required_years > 0:
            experience_ratio = min(candidate_years / required_years, 2.0)  # Cap at 200%
            experience_score = experience_ratio * 50
        else:
            experience_score = 75 if candidate_years > 0 else 25
        
        scores['experience'] = min(experience_score, 100)
        
        # Education relevance score (15% weight)
        education_keywords = ['degree', 'bachelor', 'master', 'phd', 'certification', 'diploma']
        job_edu_mentions = sum(1 for keyword in education_keywords if keyword in job_lower)
        resume_edu_mentions = sum(1 for keyword in education_keywords if keyword in resume_lower)
        
        if job_edu_mentions > 0:
            education_score = min((resume_edu_mentions / job_edu_mentions) * 100, 100)
        else:
            education_score = 50  # Neutral score if no education requirements
        
        scores['education'] = education_score
        
        # Keyword density score (20% weight)
        # Extract important terms from job description
        job_words = re.findall(r'\b[a-zA-Z]{3,}\b', job_desc.lower())
        job_word_freq = Counter(job_words)
        
        # Get top 20 most frequent words from job description (excluding common words)
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'will', 'with', 'have', 'this', 'that', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'}
        
        important_job_words = [word for word, freq in job_word_freq.most_common(20) 
                              if word not in common_words and len(word) > 3]
        
        resume_words = re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower())
        resume_word_set = set(resume_words)
        
        keyword_matches = len([word for word in important_job_words if word in resume_word_set])
        keyword_score = (keyword_matches / max(len(important_job_words), 1)) * 100
        scores['keyword_density'] = min(keyword_score, 100)
        
        return scores
    
    def calculate_comprehensive_score(self, resume_text: str, job_desc: str) -> Dict[str, float]:
        """Calculate comprehensive score with detailed breakdown"""
        section_scores = self.calculate_section_scores(resume_text, job_desc)
        
        # Weighted scoring
        weights = {
            'skills': 0.40,
            'experience': 0.25,
            'education': 0.15,
            'keyword_density': 0.20
        }
        
        # Calculate weighted final score
        final_score = sum(section_scores[section] * weight 
                         for section, weight in weights.items())
        
        # Add bonus for well-structured resume
        structure_bonus = self.calculate_structure_bonus(resume_text)
        final_score = min(final_score + structure_bonus, 100)
        
        return {
            'final_score': final_score,
            'breakdown': section_scores,
            'structure_bonus': structure_bonus
        }
    
    def calculate_structure_bonus(self, resume_text: str) -> float:
        """Calculate bonus points for well-structured resume"""
        text_lower = resume_text.lower()
        bonus = 0
        
        # Check for common resume sections
        section_count = 0
        for section_type, headers in self.section_headers.items():
            for header in headers:
                if header in text_lower:
                    section_count += 1
                    break
        
        # Bonus for having multiple sections (max 5 points)
        bonus += min(section_count * 1.25, 5)
        
        # Bonus for having contact information (2 points)
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
            bonus += 2
        
        # Bonus for having phone number (1 point)
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', resume_text):
            bonus += 1
        
        # Bonus for adequate length (2 points if between 200-2000 words)
        word_count = len(resume_text.split())
        if 200 <= word_count <= 2000:
            bonus += 2
        
        return min(bonus, 10)  # Cap at 10 bonus points
    
    def process_uploaded_resumes(self, uploaded_files, job_desc: str) -> List[Dict]:
        """Process uploaded resume files"""
        resumes = []
        
        if not uploaded_files:
            return resumes
        
        progress_bar = st.progress(0)
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                # Extract text from uploaded file
                text = self.extract_text_from_uploaded_file(uploaded_file)
                
                if text.strip():
                    # Calculate comprehensive score
                    score_data = self.calculate_comprehensive_score(text, job_desc)
                    
                    resume_data = {
                        'name': uploaded_file.name,
                        'text': text,
                        'score': score_data['final_score'],
                        'breakdown': score_data['breakdown'],
                        'structure_bonus': score_data['structure_bonus'],
                        'word_count': len(text.split()),
                        'file_size': uploaded_file.size,
                        'uploaded_file': uploaded_file  # Keep reference for saving
                    }
                    resumes.append(resume_data)
                else:
                    st.warning(f"No text extracted from {uploaded_file.name}")
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                logger.error(f"Error processing {uploaded_file.name}: {e}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        progress_bar.empty()
        
        # Sort resumes by score
        resumes.sort(key=lambda x: x['score'], reverse=True)
        
        # Assign ranks
        for rank, resume in enumerate(resumes, 1):
            resume['rank'] = rank
        
        return resumes
    
    def save_top_resumes_to_directory(self, top_resumes: List[Dict], min_threshold: float) -> Tuple[int, List[str]]:
        """Save top scoring resumes to the target directory"""
        saved_count = 0
        saved_files = []
        failed_files = []
        
        try:
            # Clear previous results
            self.clear_top_resumes_directory()
            
            for resume in top_resumes:
                if resume['score'] >= min_threshold:
                    try:
                        # Generate a clean filename with score
                        original_name = resume['name']
                        name_parts = original_name.rsplit('.', 1)
                        if len(name_parts) == 2:
                            clean_name = f"rank_{resume['rank']}_score_{resume['score']:.1f}_{name_parts[0]}.{name_parts[1]}"
                        else:
                            clean_name = f"rank_{resume['rank']}_score_{resume['score']:.1f}_{original_name}"
                        
                        # Save the file
                        success = self.save_uploaded_file_to_target(resume['uploaded_file'], clean_name)
                        
                        if success:
                            saved_count += 1
                            saved_files.append(clean_name)
                        else:
                            failed_files.append(original_name)
                            
                    except Exception as e:
                        logger.error(f"Error saving resume {resume['name']}: {e}")
                        failed_files.append(resume['name'])
            
            # Create a summary file
            self.create_summary_file(top_resumes, min_threshold)
            
            return saved_count, saved_files, failed_files
            
        except Exception as e:
            logger.error(f"Error in save_top_resumes_to_directory: {e}")
            return 0, [], [resume['name'] for resume in top_resumes]
    
    def create_summary_file(self, top_resumes: List[Dict], min_threshold: float):
        """Create a summary file of the analysis"""
        try:
            summary_path = os.path.join(self.target_directory, "shortlist_summary.txt")
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("=== RESUME SHORTLIST SUMMARY ===\n")
                f.write(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Minimum threshold: {min_threshold}%\n")
                f.write(f"Total candidates analyzed: {len(top_resumes)}\n")
                
                qualified_resumes = [r for r in top_resumes if r['score'] >= min_threshold]
                f.write(f"Candidates meeting threshold: {len(qualified_resumes)}\n\n")
                
                f.write("=== SHORTLISTED CANDIDATES ===\n")
                for i, resume in enumerate(qualified_resumes, 1):
                    f.write(f"\n{i}. {resume['name']}\n")
                    f.write(f"   Overall Score: {resume['score']:.1f}%\n")
                    f.write(f"   Grade: {'A' if resume['score'] >= 80 else 'B' if resume['score'] >= 60 else 'C' if resume['score'] >= 40 else 'D'}\n")
                    f.write(f"   Skills Score: {resume['breakdown']['skills']:.1f}%\n")
                    f.write(f"   Experience Score: {resume['breakdown']['experience']:.1f}%\n")
                    f.write(f"   Education Score: {resume['breakdown']['education']:.1f}%\n")
                    f.write(f"   Keywords Score: {resume['breakdown']['keyword_density']:.1f}%\n")
                    f.write(f"   Structure Bonus: +{resume['structure_bonus']:.1f}\n")
                    f.write(f"   Word Count: {resume['word_count']}\n")
                
                if len(top_resumes) > len(qualified_resumes):
                    f.write(f"\n=== CANDIDATES BELOW THRESHOLD ===\n")
                    below_threshold = [r for r in top_resumes if r['score'] < min_threshold]
                    for i, resume in enumerate(below_threshold, 1):
                        f.write(f"\n{i}. {resume['name']} - Score: {resume['score']:.1f}%\n")
            
            logger.info(f"Summary file created at {summary_path}")
            
        except Exception as e:
            logger.error(f"Error creating summary file: {e}")

def create_detailed_visualization(ranked_df: pd.DataFrame, detailed_scores: List[Dict]):
    """Create detailed visualization with score breakdown"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # Main ranking bar chart
    colors = plt.cm.RdYlGn(ranked_df['Score'] / 100)
    bars = ax1.barh(ranked_df['Resume'], ranked_df['Score'], color=colors)
    ax1.set_xlabel('Overall Score (%)')
    ax1.set_ylabel('Resume')
    ax1.set_title('Resume Ranking - Overall Scores', fontsize=14, fontweight='bold')
    ax1.invert_yaxis()
    
    # Add score labels
    for bar, score in zip(bars, ranked_df['Score']):
        ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                f'{score:.1f}%', va='center', fontweight='bold')
    
    # Score distribution histogram
    ax2.hist(ranked_df['Score'], bins=min(10, len(ranked_df)), alpha=0.7, 
             color='skyblue', edgecolor='black')
    ax2.set_xlabel('Score Range (%)')
    ax2.set_ylabel('Number of Resumes')
    ax2.set_title('Score Distribution', fontsize=14, fontweight='bold')
    ax2.axvline(ranked_df['Score'].mean(), color='red', linestyle='--', 
                label=f'Mean: {ranked_df["Score"].mean():.1f}%')
    ax2.legend()
    
    # Skills breakdown for top 5 resumes
    if detailed_scores:
        top_5_scores = detailed_scores[:5]
        categories = ['Skills', 'Experience', 'Education', 'Keywords']
        
        x = np.arange(len(categories))
        width = 0.15
        
        for i, resume_score in enumerate(top_5_scores):
            breakdown = resume_score['breakdown']
            values = [
                breakdown['skills'],
                breakdown['experience'], 
                breakdown['education'],
                breakdown['keyword_density']
            ]
            
            ax3.bar(x + i * width, values, width, 
                   label=f"#{i+1} {resume_score['name'][:15]}...")
        
        ax3.set_xlabel('Score Categories')
        ax3.set_ylabel('Score (%)')
        ax3.set_title('Top 5 Resumes - Category Breakdown', fontsize=14, fontweight='bold')
        ax3.set_xticks(x + width * 2)
        ax3.set_xticklabels(categories)
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Grade distribution pie chart
        grade_counts = ranked_df['Grade'].value_counts()
        colors_pie = ['#2E8B57', '#FFD700', '#FF8C00', '#DC143C']  # Green, Gold, Orange, Red
        ax4.pie(grade_counts.values, labels=grade_counts.index, autopct='%1.1f%%',
                colors=colors_pie[:len(grade_counts)], startangle=90)
        ax4.set_title('Grade Distribution', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig

def main():
    st.set_page_config(page_title="Enhanced ATS Resume Filtering", layout="wide")
    st.title("🎯 Enhanced ATS Resume Filtering System")
    
    # Enhanced system info
    with st.expander("🚀 Advanced ATS Features", expanded=False):
        st.markdown(f"""
        **Advanced Scoring Algorithm:**
        - 📊 **Skills Matching (40%)**: Exact keyword and skill matching with job requirements
        - 🏢 **Experience Relevance (25%)**: Years of experience alignment with job requirements  
        - 🎓 **Education Matching (15%)**: Educational qualifications and certifications
        - 🔍 **Keyword Density (20%)**: Contextual keyword matching from job description
        - ⭐ **Structure Bonus**: Well-formatted resume with proper sections (+10 points max)
        
        **Automatic Shortlisting:**
        - 📁 Top candidates automatically saved to `{TARGET_DIRECTORY}` folder
        - 📋 Detailed summary report generated
        - 🏆 File names include rank and score for easy identification
        
        **Grading System:**
        - 🅰️ **Grade A**: 80-100% (Excellent match)
        - 🅱️ **Grade B**: 60-79% (Good match) 
        - 🆑 **Grade C**: 40-59% (Fair match)
        - 🅳 **Grade D**: <40% (Poor match)
        """)
    
    processor = EnhancedResumeProcessor()
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload option
        st.subheader("📁 Upload Resume Files")
        uploaded_files = st.file_uploader(
            "Choose resume files",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'txt'],
            help="Upload multiple resume files (PDF, DOCX, TXT formats supported)"
        )
        
        # Job description input
        st.subheader("📋 Job Description")
        job_desc = st.text_area(
            "Enter detailed job description with requirements",
            height=200,
            placeholder="Enter job title, required skills, experience level, education requirements, etc.",
            help="Be specific about required skills, experience years, and qualifications for better matching"
        )
    
    with col2:
        st.subheader("⚙️ Filtering Options")
        
        num_shortlist = st.number_input(
            "🔢 Number of top resumes to shortlist", 
            min_value=1, 
            max_value=50, 
            value=5, 
            step=1
        )
        
        min_score_threshold = st.slider(
            "📊 Minimum score threshold for shortlisting (%)",
            min_value=0,
            max_value=100,
            value=50,
            help="Only resumes above this score will be saved to top_resumes folder"
        )
        
        st.info(f"📁 Shortlisted resumes will be saved to: `{TARGET_DIRECTORY}/`")
        
        show_detailed_breakdown = st.checkbox(
            "📈 Show detailed score breakdown",
            value=True,
            help="Display individual category scores for each resume"
        )
        
        clear_previous_results = st.checkbox(
            "🧹 Clear previous results",
            value=True,
            help="Clear previous shortlisted resumes before saving new ones"
        )
    
    # Analysis button
    if st.button("🚀 Analyze & Shortlist Resumes", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("Please upload at least one resume file")
            return
        
        if not job_desc.strip():
            st.error("Please enter a job description")
            return
        
        if len(job_desc.split()) < 10:
            st.warning("Job description seems too short. Consider adding more details for better matching.")
        
        with st.spinner('🔄 Processing resumes with advanced ATS scoring...'):
            try:
                # Process uploaded resumes
                resumes = processor.process_uploaded_resumes(uploaded_files, job_desc)
                
                if not resumes:
                    st.error("No resumes could be processed successfully")
                    return
                
                st.success(f"✅ Successfully processed {len(resumes)} resume(s)")
                
                # Get top resumes for shortlisting
                top_resumes = resumes[:num_shortlist]
                
                # Save qualified resumes to target directory
                saved_count, saved_files, failed_files = processor.save_top_resumes_to_directory(
                    top_resumes, min_score_threshold
                )
                
                # Show save results
                if saved_count > 0:
                    st.success(f"🎉 Successfully saved {saved_count} resume(s) to `{TARGET_DIRECTORY}` folder!")
                    
                    with st.expander("📁 Saved Files", expanded=True):
                        for filename in saved_files:
                            st.write(f"✅ {filename}")
                else:
                    st.warning(f"⚠️ No resumes met the minimum threshold of {min_score_threshold}%")
                
                if failed_files:
                    with st.expander("❌ Failed to Save", expanded=False):
                        for filename in failed_files:
                            st.write(f"❌ {filename}")
                
                # Filter results for display
                filtered_resumes = [r for r in resumes if r['score'] >= min_score_threshold]
                if not filtered_resumes:
                    st.info("Showing all results (none met the threshold)")
                    filtered_resumes = resumes
                
                # Create results DataFrame
                ranked_df = pd.DataFrame([
                    {
                        'Rank': res['rank'],
                        'Resume': res['name'],
                        'Score': round(res['score'], 1),
                        'Grade': ('A' if res['score'] >= 80 else 
                                'B' if res['score'] >= 60 else 
                                'C' if res['score'] >= 40 else 'D'),
                        'Status': '✅ Shortlisted' if res['score'] >= min_score_threshold else '❌ Below Threshold',
                        'Words': res['word_count'],
                        'Size (KB)': round(res['file_size'] / 1024, 1)
                    }
                    for res in resumes
                ])
                
                # Display results
                st.header("📊 Resume Analysis Results")
                
                # Summary metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("📄 Total Resumes", len(resumes))
                with col2:
                    st.metric("✅ Shortlisted", saved_count)
                with col3:
                    st.metric("📈 Average Score", f"{ranked_df['Score'].mean():.1f}%")
                with col4:
                    st.metric("🏆 Top Score", f"{ranked_df['Score'].max():.1f}%")
                with col5:
                    grade_a_count = len([r for r in resumes if r['score'] >= 80])
                    st.metric("🅰️ Grade A Count", grade_a_count)
                
                # Enhanced results table
                st.subheader("🏆 Ranking Results")
                st.dataframe(
                    ranked_df,
                    use_container_width=True,
                    column_config={
                        "Score": st.column_config.ProgressColumn(
                            "Score (%)",
                            help="Overall ATS matching score",
                            min_value=0,
                            max_value=100,
                        ),
                        "Grade": st.column_config.TextColumn(
                            "Grade",
                            help="A: 80-100%, B: 60-79%, C: 40-59%, D: <40%"
                        ),
                        "Status": st.column_config.TextColumn(
                            "Shortlist Status",
                            help="Whether resume was saved to top_resumes folder"
                        ),
                        "Words": st.column_config.NumberColumn(
                            "Word Count",
                            help="Total words in resume"
                        ),
                        "Size (KB)": st.column_config.NumberColumn(
                            "File Size",
                            help="File size in KB"
                        )
                    }
                )
                
                # Show shortlisted candidates prominently
                if saved_count > 0:
                    st.subheader("🎯 Shortlisted Candidates")
                    shortlisted_df = ranked_df[ranked_df['Status'] == '✅ Shortlisted']
                    st.dataframe(
                        shortlisted_df[['Rank', 'Resume', 'Score', 'Grade']],
                        use_container_width=True,
                        column_config={
                            "Score": st.column_config.ProgressColumn(
                                "Score (%)",
                                min_value=0,
                                max_value=100,
                            ),
                        }
                    )
                
                # Detailed breakdown for top resumes
                if show_detailed_breakdown:
                    st.subheader("📈 Detailed Score Breakdown - Top Candidates")
                    
                    display_resumes = [r for r in resumes if r['score'] >= min_score_threshold][:3]
                    if not display_resumes:
                        display_resumes = resumes[:3]
                    
                    for i, resume in enumerate(display_resumes, 1):
                        status_icon = "🎯" if resume['score'] >= min_score_threshold else "⚠️"
                        with st.expander(f"{status_icon} #{i} {resume['name']} - {resume['score']:.1f}%", expanded=(i==1)):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Category Scores:**")
                                breakdown = resume['breakdown']
                                
                                # Create mini bar chart for categories
                                fig_mini, ax_mini = plt.subplots(figsize=(8, 4))
                                categories = list(breakdown.keys())
                                scores = list(breakdown.values())
                                colors_mini = plt.cm.RdYlGn([s/100 for s in scores])
                                
                                bars = ax_mini.barh(categories, scores, color=colors_mini)
                                ax_mini.set_xlabel('Score (%)')
                                ax_mini.set_title(f'Score Breakdown - {resume["name"][:20]}...')
                                
                                # Add score labels
                                for bar, score in zip(bars, scores):
                                    ax_mini.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                                               f'{score:.1f}%', va='center')
                                
                                st.pyplot(fig_mini, use_container_width=True)
                            
                            with col2:
                                st.write("**Resume Statistics:**")
                                st.write(f"• **Overall Score:** {resume['score']:.1f}%")
                                st.write(f"• **Structure Bonus:** +{resume['structure_bonus']:.1f}")
                                st.write(f"• **Word Count:** {resume['word_count']:,}")
                                st.write(f"• **File Size:** {resume['file_size']/1024:.1f} KB")
                                st.write(f"• **Rank:** #{resume['rank']}")
                                
                                status_text = "✅ **SHORTLISTED**" if resume['score'] >= min_score_threshold else "❌ **BELOW THRESHOLD**"
                                st.write(f"• **Status:** {status_text}")
                                
                                # Show top skills found
                                extracted_keywords = processor.extract_keywords(resume['text'])
                                all_skills = []
                                for category, skills in extracted_keywords.items():
                                    all_skills.extend(skills)
                                
                                if all_skills:
                                    st.write("**Key Skills Detected:**")
                                    st.write(", ".join(all_skills[:10]))
                
                # Enhanced visualization
                st.subheader("📊 Visual Analysis")
                detailed_score_data = [
                    {
                        'name': r['name'],
                        'breakdown': r['breakdown'],
                        'score': r['score']
                    }
                    for r in resumes
                ]
                
                fig = create_detailed_visualization(ranked_df, detailed_score_data)
                st.pyplot(fig, use_container_width=True)
                
                # Download section
                st.subheader("📥 Download Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # CSV download
                    csv_data = ranked_df.to_csv(index=False)
                    st.download_button(
                        label="📄 Download Rankings (CSV)",
                        data=csv_data,
                        file_name=f"ats_resume_rankings_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # Detailed analysis download
                    detailed_analysis = []
                    for resume in resumes:
                        detailed_analysis.append({
                            'Resume': resume['name'],
                            'Overall_Score': resume['score'],
                            'Skills_Score': resume['breakdown']['skills'],
                            'Experience_Score': resume['breakdown']['experience'],
                            'Education_Score': resume['breakdown']['education'],
                            'Keywords_Score': resume['breakdown']['keyword_density'],
                            'Structure_Bonus': resume['structure_bonus'],
                            'Word_Count': resume['word_count'],
                            'Shortlisted': 'Yes' if resume['score'] >= min_score_threshold else 'No'
                        })
                    
                    detailed_df = pd.DataFrame(detailed_analysis)
                    detailed_csv = detailed_df.to_csv(index=False)
                    
                    st.download_button(
                        label="📊 Download Detailed Analysis",
                        data=detailed_csv,
                        file_name=f"detailed_ats_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col3:
                    # Summary report download
                    try:
                        summary_path = os.path.join(TARGET_DIRECTORY, "shortlist_summary.txt")
                        if os.path.exists(summary_path):
                            with open(summary_path, 'r', encoding='utf-8') as f:
                                summary_content = f.read()
                            
                            st.download_button(
                                label="📋 Download Summary Report",
                                data=summary_content,
                                file_name=f"shortlist_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        else:
                            st.write("Summary file not available")
                    except Exception as e:
                        st.write(f"Error loading summary: {e}")
                
                # Final message
                st.success(f"""
                🎉 **Analysis Complete!** 
                
                - **{len(resumes)} resumes** analyzed
                - **{saved_count} candidates** shortlisted to `{TARGET_DIRECTORY}` folder  
                - **Summary report** generated for next steps
                
                You can now proceed to **Feature Analysis** page to get detailed AI insights on the shortlisted candidates.
                """)
                
            except Exception as e:
                st.error(f"❌ An error occurred during processing: {str(e)}")
                logger.error(f"Error in main processing: {e}")
                st.info("Please check your files and try again. If the problem persists, contact support.")

if __name__ == "__main__":
    main()