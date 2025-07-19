import streamlit as st
import os
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib
import pickle

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Qdrant
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

class EnhancedFeatureAnalyzer:
    def __init__(self):
        self.target_directory = "top_resumes"
        self.cache_dir = Path("cache/feature_analysis")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.cache_dir / "analysis_history.json"
        
        # Initialize session state for job description continuity
        if 'ats_job_description' not in st.session_state:
            st.session_state.ats_job_description = ""
        if 'selected_candidates' not in st.session_state:
            st.session_state.selected_candidates = []
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
    
    @st.cache_resource
    def load_embeddings(_self):
        """Cache embeddings model"""
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    @st.cache_resource  
    def load_llm(_self):
        """Cache LLM model"""
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_tokens=4000
        )
    
    def get_analysis_cache_key(self, job_desc: str, file_hashes: List[str]) -> str:
        """Generate cache key for analysis results"""
        combined = job_desc + "".join(sorted(file_hashes))
        return hashlib.md5(combined.encode()).hexdigest()
    
    def load_cached_analysis(self, cache_key: str) -> Optional[Dict]:
        """Load cached analysis results"""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                pass
        return None
    
    def save_analysis_cache(self, cache_key: str, results: Dict):
        """Save analysis results to cache"""
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(results, f)
        except Exception as e:
            st.warning(f"Failed to cache results: {e}")
    
    def load_previous_job_description(self) -> Optional[str]:
        """Load job description from ATS analysis"""
        try:
            summary_file = Path(self.target_directory) / "shortlist_summary.txt"
            if summary_file.exists():
                # Extract job description from summary if available
                # This is a placeholder - you might want to save job desc separately
                return st.session_state.get('ats_job_description', "")
        except Exception:
            pass
        return None
    
    def get_enhanced_documents(self) -> Tuple[List[Document], List[str]]:
        """Load and enhance documents with metadata"""
        if not os.path.exists(self.target_directory):
            return [], []
        
        documents = []
        file_hashes = []
        
        # Load PDF documents
        loader = PyPDFDirectoryLoader(self.target_directory)
        docs = loader.load()
        
        # Enhance documents with metadata from filenames
        for doc in docs:
            # Extract rank and score from filename if available
            filename = os.path.basename(doc.metadata.get('source', ''))
            
            # Parse enhanced filename from ATS system
            rank_match = None
            score_match = None
            if 'rank_' in filename and 'score_' in filename:
                try:
                    parts = filename.split('_')
                    rank_idx = parts.index('rank') + 1
                    score_idx = parts.index('score') + 1
                    if rank_idx < len(parts):
                        rank_match = int(parts[rank_idx])
                    if score_idx < len(parts):
                        score_match = float(parts[score_idx])
                except (ValueError, IndexError):
                    pass
            
            doc.metadata.update({
                'filename': filename,
                'rank': rank_match or len(documents) + 1,
                'ats_score': score_match or 0.0,
                'analysis_timestamp': datetime.now().isoformat()
            })
            
            documents.append(doc)
            
            # Generate file hash for caching
            file_hash = hashlib.md5(doc.page_content.encode()).hexdigest()
            file_hashes.append(file_hash)
        
        return documents, file_hashes
    
    def create_enhanced_prompt_template(self, analysis_type: str = "comprehensive") -> str:
        """Create dynamic prompt templates based on analysis type"""
        
        base_context = """You are an expert HR analyst and recruiter with deep expertise in talent assessment. 
        Analyze the provided resumes against the specific job requirements with precision and insight."""
        
        if analysis_type == "comprehensive":
            return f"""{base_context}

**ANALYSIS CONTEXT:**
{{resume}}

**JOB REQUIREMENTS:**
{{question}}

**ANALYSIS FRAMEWORK:**
Provide a detailed analysis for each candidate following this structure:

## 📋 CANDIDATE ANALYSIS REPORT

### 🎯 Overall Assessment Summary
- Total candidates analyzed: [number]
- Top recommendation: [candidate name with reasoning]
- Key insights: [2-3 strategic insights]

---

### 👤 INDIVIDUAL CANDIDATE PROFILES

**CANDIDATE 1: [Name from document]**
📄 **Source Document:** [filename]
⭐ **ATS Rank:** [if available in metadata]
📊 **Match Score:** [X/10]

**🎯 STRENGTHS:**
- **Primary Strength:** [Most relevant to role]
- **Secondary Strengths:** [2-3 additional strengths]
- **Unique Value:** [What sets them apart]

**⚠️ DEVELOPMENT AREAS:**
- **Skill Gaps:** [Specific missing skills]
- **Experience Gaps:** [Areas needing growth]
- **Recommendations:** [How to address gaps]

**💼 ROLE FIT ANALYSIS:**
- **Technical Match:** [X/10] - [specific reasoning]
- **Experience Level:** [Junior/Mid/Senior] - [X years relevant]
- **Cultural Indicators:** [team fit, leadership, etc.]

**🎤 INTERVIEW FOCUS:**
- **Key Questions:** [3 specific questions to ask]
- **Skills to Validate:** [Technical/soft skills to test]

---

**CANDIDATE 2: [Name from document]**
[Same detailed structure as above]

---

### 📊 COMPARATIVE ANALYSIS

**🏆 RANKING RECOMMENDATION:**
1. **[Candidate Name]** - [Score] - [Primary reason]
2. **[Candidate Name]** - [Score] - [Primary reason]
3. **[Candidate Name]** - [Score] - [Primary reason]

**📈 SKILLS MATRIX:**
[Create a comparison table of key skills across candidates]

**⚖️ HIRING DECISION MATRIX:**
- **Immediate Hire:** [Candidates ready now]
- **Potential with Development:** [Need training/growth]
- **Future Consideration:** [Not current fit but potential]

### 🎯 STRATEGIC RECOMMENDATIONS

**IMMEDIATE ACTIONS:**
1. [Specific next step for top candidate]
2. [Interview scheduling recommendations]
3. [Skills assessment suggestions]

**TALENT PIPELINE:**
- [Long-term potential candidates]
- [Skills gaps to address in future hiring]

---

*Analysis completed on {{analysis_date}}*
*Based on {{document_count}} candidate resumes*"""

        elif analysis_type == "skills_focused":
            return f"""{base_context}

**CONTEXT:** {{resume}}
**JOB REQUIREMENTS:** {{question}}

## 🛠️ SKILLS-FOCUSED ANALYSIS

### 📊 TECHNICAL SKILLS MATRIX
For each candidate, provide:

**CANDIDATE [Name]:**
- **Core Technical Skills:** [Rate 1-10 with evidence]
- **Programming Languages:** [List with proficiency level]
- **Frameworks/Tools:** [Relevant to role]
- **Certifications:** [Professional credentials]
- **Years of Experience:** [In relevant technologies]
- **Project Evidence:** [Specific examples from resume]
- **Skill Gaps:** [What's missing for this role]
- **Learning Trajectory:** [Evidence of continuous learning]

### 🔍 SKILLS GAP ANALYSIS
- **Critical Missing Skills:** [Across all candidates]
- **Training Opportunities:** [How to address gaps]
- **Alternative Solutions:** [Different skill combinations]"""

        elif analysis_type == "culture_fit":
            return f"""{base_context}

**CONTEXT:** {{resume}}
**JOB REQUIREMENTS:** {{question}}

## 👥 CULTURE & TEAM FIT ANALYSIS

### 🤝 BEHAVIORAL INDICATORS

**CANDIDATE [Name]:**
- **Leadership Style:** [Evidence from experience]
- **Communication Skills:** [Written/verbal indicators]
- **Team Collaboration:** [Examples from resume]
- **Problem-Solving Approach:** [Method evidence]
- **Adaptability:** [Change management examples]
- **Work Style:** [Remote/office, independent/collaborative]
- **Career Motivation:** [Growth trajectory analysis]
- **Values Alignment:** [Based on company choices]"""

        return ""  # Default fallback

    def perform_enhanced_analysis(
        self, 
        job_description: str, 
        analysis_type: str = "comprehensive",
        selected_candidates: List[str] = None
    ) -> Dict:
        """Perform enhanced analysis with caching and progress tracking"""
        
        # Load documents
        documents, file_hashes = self.get_enhanced_documents()
        if not documents:
            return {"error": "No documents found in the top_resumes directory"}
        
        # Filter documents if specific candidates selected
        if selected_candidates:
            documents = [doc for doc in documents 
                        if any(candidate in doc.metadata.get('filename', '') 
                              for candidate in selected_candidates)]
        
        # Check cache
        cache_key = self.get_analysis_cache_key(job_description, file_hashes)
        cached_result = self.load_cached_analysis(cache_key)
        
        if cached_result and st.checkbox("Use cached analysis (faster)", value=True):
            st.info("📋 Using cached analysis results")
            return cached_result
        
        try:
            # Create progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Initialize embeddings and vector store
            status_text.text("🔄 Loading embeddings model...")
            progress_bar.progress(10)
            
            embeddings = self.load_embeddings()
            
            # Split documents for better retrieval
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            status_text.text("📄 Processing documents...")
            progress_bar.progress(30)
            
            split_docs = text_splitter.split_documents(documents)
            
            # Create vector store
            status_text.text("🧠 Creating knowledge base...")
            progress_bar.progress(50)
            
            qdrant_collection = Qdrant.from_documents(
                split_docs,
                embeddings,
                location=":memory:",
                collection_name=f"enhanced_resumes_{len(documents)}",
            )
            
            # Configure retriever for better results
            retriever = qdrant_collection.as_retriever(
                search_type="mmr",  # Maximum marginal relevance
                search_kwargs={"k": 8, "fetch_k": 16, "lambda_mult": 0.7}
            )
            
            # Create enhanced prompt
            status_text.text("🎯 Preparing analysis framework...")
            progress_bar.progress(70)
            
            prompt_template = self.create_enhanced_prompt_template(analysis_type)
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            # Load LLM
            llm = self.load_llm()
            
            # Create analysis chain
            chain = (
                {
                    "resume": RunnablePassthrough() | retriever,
                    "question": RunnablePassthrough(),
                    "analysis_date": lambda _: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "document_count": lambda _: len(documents)
                }
                | prompt
                | llm
                | StrOutputParser()
            )
            
            # Execute analysis
            status_text.text("🤖 Performing AI analysis...")
            progress_bar.progress(90)
            
            analysis_result = chain.invoke(job_description)
            
            # Prepare results
            results = {
                "analysis": analysis_result,
                "metadata": {
                    "analysis_type": analysis_type,
                    "candidate_count": len(documents),
                    "job_description": job_description,
                    "timestamp": datetime.now().isoformat(),
                    "candidates": [doc.metadata.get('filename', f'doc_{i}') 
                                 for i, doc in enumerate(documents)]
                },
                "raw_documents": [
                    {
                        "filename": doc.metadata.get('filename', ''),
                        "rank": doc.metadata.get('rank', 0),
                        "ats_score": doc.metadata.get('ats_score', 0.0)
                    }
                    for doc in documents
                ]
            }
            
            # Save to cache
            status_text.text("💾 Saving results...")
            progress_bar.progress(100)
            
            self.save_analysis_cache(cache_key, results)
            self.save_to_history(results)
            
            # Clean up progress indicators
            progress_bar.empty()
            status_text.empty()
            
            return results
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def save_to_history(self, results: Dict):
        """Save analysis to history"""
        try:
            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            
            history.append({
                "timestamp": results["metadata"]["timestamp"],
                "analysis_type": results["metadata"]["analysis_type"],
                "candidate_count": results["metadata"]["candidate_count"],
                "job_title": results["metadata"]["job_description"][:100] + "..." 
                           if len(results["metadata"]["job_description"]) > 100 
                           else results["metadata"]["job_description"]
            })
            
            # Keep only last 50 analyses
            history = history[-50:]
            
            with open(self.history_file, 'w') as f:
                json.dump(history, indent=2, fp=f)
        except Exception:
            pass  # Don't fail on history save error
    
    def load_analysis_history(self) -> List[Dict]:
        """Load previous analysis history"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def create_analysis_visualizations(self, results: Dict) -> Dict:
        """Create visualizations from analysis results"""
        if "error" in results:
            return {}
        
        metadata = results.get("metadata", {})
        candidates = results.get("raw_documents", [])
        
        # Basic candidate overview
        fig_overview = go.Figure()
        
        if candidates:
            names = [c.get('filename', f'Candidate {i+1}')[:20] + '...' 
                    for i, c in enumerate(candidates)]
            ranks = [c.get('rank', i+1) for i, c in enumerate(candidates)]
            scores = [c.get('ats_score', 0) for c in candidates]
            
            fig_overview.add_trace(go.Bar(
                x=names,
                y=scores,
                text=[f"Rank #{r}" for r in ranks],
                textposition='auto',
                marker_color='lightblue'
            ))
            
            fig_overview.update_layout(
                title="Candidate ATS Scores",
                xaxis_title="Candidates",
                yaxis_title="ATS Score",
                height=400
            )
        
        return {
            "candidate_overview": fig_overview,
            "analysis_date": metadata.get("timestamp", ""),
            "candidate_count": metadata.get("candidate_count", 0)
        }

def main():
    st.set_page_config(
        page_title="Enhanced Feature Analysis", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧠 Enhanced Candidate Feature Analysis")
    st.markdown("### AI-Powered Deep Insights into Top Candidates")
    
    analyzer = EnhancedFeatureAnalyzer()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Analysis Configuration")
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "Analysis Focus",
            ["comprehensive", "skills_focused", "culture_fit"],
            help="Choose the type of analysis to perform"
        )
        
        # Load available candidates
        docs, _ = analyzer.get_enhanced_documents()
        if docs:
            st.subheader("📋 Available Candidates")
            candidate_names = [doc.metadata.get('filename', f'Document {i}') 
                             for i, doc in enumerate(docs)]
            
            select_all = st.checkbox("Select All Candidates", value=True)
            
            if select_all:
                selected_candidates = candidate_names
            else:
                selected_candidates = st.multiselect(
                    "Choose specific candidates:",
                    candidate_names,
                    default=candidate_names[:3]
                )
            
            st.session_state.selected_candidates = selected_candidates
            
            # Show candidate preview
            if st.checkbox("Show Candidate Preview"):
                for doc in docs[:3]:  # Show first 3
                    with st.expander(f"📄 {doc.metadata.get('filename', 'Unknown')}"):
                        st.write(f"**ATS Rank:** {doc.metadata.get('rank', 'N/A')}")
                        st.write(f"**ATS Score:** {doc.metadata.get('ats_score', 'N/A')}")
                        st.write(f"**Content Preview:** {doc.page_content[:200]}...")
        
        # Analysis history
        st.subheader("📚 Recent Analyses")
        history = analyzer.load_analysis_history()
        if history:
            for i, h in enumerate(history[-5:]):  # Show last 5
                st.text(f"{h['timestamp'][:16]}")
                st.caption(f"{h['analysis_type']} - {h['candidate_count']} candidates")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Job description input with smart loading
        st.subheader("📋 Job Requirements")
        
        # Try to load previous job description
        previous_job_desc = analyzer.load_previous_job_description()
        if previous_job_desc and st.checkbox("Use job description from ATS filtering", value=True):
            job_description = st.text_area(
                "Job Description (from ATS analysis):",
                value=previous_job_desc,
                height=150,
                help="This job description was used in the ATS filtering process"
            )
        else:
            job_description = st.text_area(
                "Enter or update job description:",
                height=150,
                placeholder="Paste detailed job description including required skills, experience, and qualifications...",
                help="Provide detailed requirements for accurate candidate analysis"
            )
        
        # Store in session state for continuity
        if job_description:
            st.session_state.ats_job_description = job_description
    
    with col2:
        st.subheader("🎯 Analysis Options")
        
        # Quick analysis tips
        with st.expander("💡 Analysis Tips", expanded=True):
            if analysis_type == "comprehensive":
                st.info("Comprehensive analysis provides overall candidate assessment with rankings and recommendations.")
            elif analysis_type == "skills_focused":
                st.info("Skills-focused analysis deep-dives into technical competencies and skill gaps.")
            elif analysis_type == "culture_fit":
                st.info("Culture fit analysis evaluates behavioral indicators and team compatibility.")
        
        # Analysis settings
        st.subheader("⚙️ Advanced Settings")
        
        include_recommendations = st.checkbox("Include hiring recommendations", value=True)
        include_interview_questions = st.checkbox("Generate interview questions", value=True)
        detailed_scoring = st.checkbox("Detailed scoring breakdown", value=False)
    
    # Analysis execution
    if st.button("🚀 Start Enhanced Analysis", type="primary", use_container_width=True):
        if not job_description.strip():
            st.error("Please enter a job description")
            return
            
        if not docs:
            st.error("No candidate documents found in the top_resumes directory")
            st.info("Please run the ATS Resume Filtering first to generate candidate data")
            return
        
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        # Perform analysis
        results = analyzer.perform_enhanced_analysis(
            job_description,
            analysis_type,
            st.session_state.selected_candidates
        )
        
        if "error" in results:
            st.error(f"Analysis failed: {results['error']}")
            return
        
        # Store results in session state
        st.session_state.analysis_results = results
        
        # Display results
        st.success(f"✅ Analysis completed for {results['metadata']['candidate_count']} candidates")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Analysis Report", "📊 Visualizations", "📋 Summary", "💾 Export"])
        
        with tab1:
            st.markdown("### 🎯 Detailed Analysis Report")
            st.markdown(results["analysis"])
        
        with tab2:
            st.markdown("### 📊 Visual Insights")
            visualizations = analyzer.create_analysis_visualizations(results)
            
            if visualizations.get("candidate_overview"):
                st.plotly_chart(visualizations["candidate_overview"], use_container_width=True)
            
            # Additional charts could be added based on analysis results
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Candidates Analyzed", visualizations.get("candidate_count", 0))
            with col2:
                st.metric("Analysis Date", visualizations.get("analysis_date", "")[:10])
        
        with tab3:
            st.markdown("### 📋 Executive Summary")
            
            metadata = results.get("metadata", {})
            candidates_data = results.get("raw_documents", [])
            
            # Create summary DataFrame
            if candidates_data:
                summary_df = pd.DataFrame([
                    {
                        "Candidate": c.get('filename', f'Candidate {i+1}'),
                        "ATS Rank": c.get('rank', 'N/A'),
                        "ATS Score": c.get('ats_score', 'N/A'),
                        "Status": "Analyzed" if c.get('filename') in st.session_state.selected_candidates else "Not Selected"
                    }
                    for i, c in enumerate(candidates_data)
                ])
                
                st.dataframe(summary_df, use_container_width=True)
            
            # Key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Analysis Type", metadata.get("analysis_type", "").title())
            with col2:
                st.metric("Total Candidates", metadata.get("candidate_count", 0))
            with col3:
                st.metric("Analysis Duration", "~30 seconds")
        
        with tab4:
            st.markdown("### 💾 Export & Save Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export analysis as markdown
                analysis_content = f"""# Candidate Analysis Report

## Analysis Details
- **Date:** {results['metadata'].get('timestamp', '')}
- **Type:** {results['metadata'].get('analysis_type', '').title()}
- **Candidates:** {results['metadata'].get('candidate_count', 0)}

## Job Requirements
{job_description}

## Analysis Results
{results['analysis']}

---
Generated by Enhanced Resume Filtering System
"""
                
                st.download_button(
                    label="📄 Download Analysis Report",
                    data=analysis_content,
                    file_name=f"candidate_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col2:
                # Export summary as CSV
                if candidates_data:
                    summary_df = pd.DataFrame([
                        {
                            "Candidate": c.get('filename', f'Candidate {i+1}'),
                            "ATS_Rank": c.get('rank', ''),
                            "ATS_Score": c.get('ats_score', ''),
                            "Analysis_Type": metadata.get("analysis_type", ""),
                            "Analysis_Date": metadata.get("timestamp", "")
                        }
                        for i, c in enumerate(candidates_data)
                    ])
                    
                    csv_data = summary_df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download Summary CSV",
                        data=csv_data,
                        file_name=f"candidate_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col3:
                # Save analysis report to target directory
                if st.button("💾 Save to Reports Folder", use_container_width=True):
                    try:
                        report_filename = os.path.join(
                            analyzer.target_directory,
                            f"enhanced_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        )
                        
                        with open(report_filename, 'w', encoding='utf-8') as f:
                            f.write(analysis_content)
                        
                        st.success(f"✅ Report saved to {report_filename}")
                    except Exception as e:
                        st.error(f"Failed to save report: {e}")

if __name__ == "__main__":
    main()