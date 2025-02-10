import os
from transformers import AutoTokenizer, AutoModelForTokenClassification
from sentence_transformers import SentenceTransformer
import groq
import google.generativeai as genai
from dotenv import load_dotenv
import faiss
import numpy as np

class AIAnalyzer:
    def __init__(self):
        load_dotenv()
        self.ner_tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        self.ner_model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        self.sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.groq_client = groq.Client(api_key=os.getenv('GROQ_API_KEY'))
    
    def extract_skills(self, text):
        inputs = self.ner_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.ner_model(**inputs)
        predictions = outputs.logits.argmax(-1)
        tokens = self.ner_tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        skills = []
        current_skill = []
        
        for token, pred in zip(tokens, predictions[0]):
            if pred == 1:  # Skill tag
                current_skill.append(token)
            elif current_skill:
                skills.append(" ".join(current_skill))
                current_skill = []
        
        return skills

    def analyze_skills_gap(self, resume_skills, job_requirements):
        prompt = f"""
        Analyze the skills gap between:
        Resume skills: {resume_skills}
        Job requirements: {job_requirements}
        
        Provide:
        1. Missing critical skills
        2. Training recommendations
        3. Upskilling priorities
        """
        
        completion = self.groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a skilled HR analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content

    def analyze_salary(self, experience, skills, location):
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Analyze market salary for:
        Experience: {experience} years
        Skills: {skills}
        Location: {location}
        
        Provide:
        1. Salary range (yearly)
        2. Market trends
        3. Factors affecting compensation
        """
        response = model.generate_content(prompt)
        return response.text

    def generate_interview_questions(self, resume_text, job_description):
        prompt = f"""
        Based on:
        Resume: {resume_text[:1000]}...
        Job Description: {job_description[:500]}...
        
        Generate:
        1. 3 Technical questions
        2. 3 Behavioral questions
        3. 2 Experience-based questions
        """
        
        completion = self.groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content