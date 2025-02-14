import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.email_handler import EmailHandler

def main():
    st.title("Email Management")
    
    if not os.path.exists("top_resumes"):
        st.error("No filtered resumes found. Please filter resumes first.")
        return
        
    email_handler = EmailHandler()
    
    st.header("Send Emails to Candidates")
    emails_data = []
    
    for filename in os.listdir("top_resumes"):
        if filename.endswith('.pdf'):
            name = filename.split('.')[0]
            email = st.text_input(f"Email for {name}")
            if email:
                emails_data.append({"name": name, "email": email})
    
    if emails_data and st.button("Send Emails"):
        for data in emails_data:
            if email_handler.send_acceptance_email(data["email"], data["name"]):
                st.success(f"Email sent to {data['name']}")
            else:
                st.error(f"Failed to send email to {data['name']}")

if __name__ == "__main__":
    main()