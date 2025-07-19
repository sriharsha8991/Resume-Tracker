import streamlit as st

def main():
    st.set_page_config(
        page_title="Resume Filtering System",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .feature-card {
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            background-color: #ffffff;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .feature-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transform: translateY(-2px);
            transition: all 0.3s ease;
        }
        .metric-card {
            text-align: center;
            padding: 1rem;
            border-radius: 8px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
        }
        .section-header {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 1.5rem;
            color: #1f1f1f;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #4CAF50;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    col1, col2 = st.columns([2,1])
    with col1:
        st.title("🚀 Smart Resume Filtering System")
        st.markdown("### Transform your recruitment process with AI-powered insights")
    with col2:
        st.success("System Status: Active ✅")
        
    # Quick Stats
    st.markdown("## 📊 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h3>97%</h3>
                <p>Accuracy Rate</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="metric-card">
                <h3>50+</h3>
                <p>Job Categories</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="metric-card">
                <h3>< 90 secs</h3>
                <p>Processing Time</p>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
            <div class="metric-card">
                <h3>24/7</h3>
                <p>Availability</p>
            </div>
        """, unsafe_allow_html=True)

    # Feature Cards
    st.markdown("## 🎯 Key Features")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="feature-card">
                <h3>🔍 Smart Resume Filtering</h3>
                <p>Upload and filter resumes based on job descriptions using advanced NLP algorithms.</p>
                <ul>
                    <li>Automated ranking system</li>
                    <li>Keyword matching</li>
                    <li>Skills assessment</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h3>📊 Data Visualization</h3>
                <p>Interactive charts and graphs for better insights:</p>
                <ul>
                    <li>Candidate comparison</li>
                    <li>Skills distribution</li>
                    <li>Experience analysis</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="feature-card">
                <h3>🤖 AI-Powered Analysis</h3>
                <p>Get deep insights into candidate profiles:</p>
                <ul>
                    <li>Skills gap analysis</li>
                    <li>Experience validation</li>
                    <li>Culture fit prediction</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card">
                <h3>📧 Automated Communications</h3>
                <p>Streamline candidate interactions:</p>
                <ul>
                    <li>Status updates</li>
                    <li>Interview scheduling</li>
                    <li>Feedback collection</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # Quick Start Guide
    st.markdown("## 🚀 Getting Started")
    with st.expander("How to use the system"):
        st.markdown("""
            1. **Upload Resumes**: Use the Filter Resumes page to upload candidate resumes
            2. **Set Criteria**: Define job requirements and filtering criteria
            3. **Review Results**: Analyze the filtered results and candidate rankings
            4. **Take Action**: Generate reports, send emails, or schedule interviews
        """)

    # Sidebar Enhancement
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/administrator-male.png")
        st.markdown("### Quick Navigation")
        st.markdown("""
            - [📑 Resume Filter](Filter_Resumes)
            - [🎯 Feature Analysis](Feature_Analysis)
            - [📊 Visualizations](Visualizations)
            - [💼 Market Analysis](Market_Analysis)
            - [📧 Email Management](Email_Management)
        """)
        
        st.markdown("---")
        st.markdown("### 📚 Resources")
        if st.button("Documentation"):
            st.markdown("Opening documentation...")
        if st.button("Tutorial"):
            st.markdown("Starting tutorial...")
        
        st.markdown("---")
        st.markdown("### 🔧 Support")
        st.markdown("Need help? [Contact Support](mailto:support@example.com)")

if __name__ == "__main__":
    main()