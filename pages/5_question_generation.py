import streamlit as st
from utils.question_generator import QuestionGenerator

def main():
    st.title("Interview Question Generator")
    
    role = st.text_input("Enter Job Role")
    skills = st.text_area("Enter Required Skills (comma-separated)")
    experience_level = st.selectbox("Select Experience Level", 
                                  ["Entry Level", "Mid Level", "Senior Level"])
    
    if st.button("Generate Questions") and role and skills:
        generator = QuestionGenerator()
        questions = generator.generate_questions(
            role=role,
            skills=skills.split(","),
            experience_level=experience_level
        )
        
        st.markdown(questions)

if __name__ == "__main__":
    main()