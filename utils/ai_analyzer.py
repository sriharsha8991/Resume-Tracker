import os
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
from sentence_transformers import SentenceTransformer
import groq
import google.generativeai as genai
from dotenv import load_dotenv
import numpy as np
import spacy

class AIAnalyzer:
    def __init__(self):
        load_dotenv()
        # Load NLP models
        self.ner_tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        self.ner_model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        self.sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.nlp = spacy.load("en_core_web_sm")
        
        # Configure API clients
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.groq_client = groq.Client(api_key=os.getenv('GROQ_API_KEY'))

    def extract_skills(self, text):
        """Extract technical and soft skills from text using NER and keyword matching."""
        # Use NER for technical skills
        inputs = self.ner_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.ner_model(**inputs)
        predictions = outputs.logits.argmax(-1)
        tokens = self.ner_tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        
        technical_skills = set()
        current_skill = []
        
        for token, pred in zip(tokens, predictions[0]):
            if pred == 1:  # Skill tag
                current_skill.append(token.replace("##", ""))
            elif current_skill:
                skill = " ".join(current_skill).strip()
                if skill and len(skill) > 2:  # Filter out short tokens
                    technical_skills.add(skill)
                current_skill = []
        
        # Use spaCy for additional skill extraction
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["SKILL", "PRODUCT", "ORG"]:
                technical_skills.add(ent.text)
        
        return list(technical_skills)

    def determine_experience_level(self, text):
        """Determine experience level based on text analysis."""
        doc = self.nlp(text.lower())
        
        # Look for various year patterns
        year_patterns = [
            r'(\d+)[\s-]*(year|yr|yrs|years)',
            r'(\d+)[\s-]*\+[\s-]*(year|yr|yrs|years)',
            r'(\d{4})\s*-\s*(\d{4}|present|current)'
        ]
        
        total_years = 0
        
        # Check each pattern
        for pattern in year_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                for match in matches:
                    if len(match) == 2:
                        if match[1] in ['present', 'current']:
                            # Calculate years if end date is present/current
                            start_year = int(match[0])
                            from datetime import datetime
                            current_year = datetime.now().year
                            total_years += (current_year - start_year)
                        else:
                            try:
                                years = int(match[0])
                                total_years = max(total_years, years)
                            except ValueError:
                                continue
        
        # Define experience levels
        if total_years == 0:
            return "Entry Level (0-2 years)"
        elif total_years < 3:
            return f"Junior Level ({total_years} years)"
        elif total_years < 6:
            return f"Mid Level ({total_years} years)"
        elif total_years < 10:
            return f"Senior Level ({total_years} years)"
        else:
            return f"Expert Level ({total_years}+ years)"

    def calculate_proficiency(self, text):
        """Calculate technical proficiency score based on skills and experience."""
        skills = self.extract_skills(text)
        experience_text = self.determine_experience_level(text)
        years = int(re.search(r'\d+', experience_text).group() or 0)
        
        # Base score calculations
        skill_score = min(len(skills) * 5, 40)  # Max 40 points for skills
        exp_score = min(years * 5, 30)  # Max 30 points for experience
        
        # Additional points for education level
        education_level = self.determine_education_level(text)
        edu_scores = {
            "PhD": 30,
            "Master's": 25,
            "Bachelor's": 20,
            "Associate's": 15,
            "High School": 10
        }
        edu_score = edu_scores.get(education_level, 10)
        
        total_score = skill_score + exp_score + edu_score
        return min(total_score, 100)  # Ensure max score is 100

    def determine_education_level(self, text):
        """Extract highest education level from text."""
        text = text.lower()
        
        education_patterns = {
            "PhD": [
                r"ph\.?d|doctor of philosophy|doctorate",
                r"doctoral candidate|dissertation"
            ],
            "Master's": [
                r"master'?s|m\.s\.|ms\b|msc\b|m\.sc\.",
                r"mba|m\.b\.a|master of business",
                r"m\.eng|master of engineering",
                r"m\.tech|master of technology"
            ],
            "Bachelor's": [
                r"bachelor'?s|b\.s\.|bs\b|bsc\b|b\.sc\.",
                r"b\.eng|bachelor of engineering",
                r"b\.tech|bachelor of technology",
                r"ba\b|b\.a\.|bachelor of arts"
            ],
            "Associate's": [
                r"associate'?s|aas\b|a\.a\.s\.",
                r"associate degree|associate diploma"
            ],
            "High School": [
                r"high school|diploma|ged",
                r"secondary school|hsc\b|12th"
            ]
        }
        
        # Check each education level
        for level, patterns in education_patterns.items():
            if any(re.search(pattern, text) for pattern in patterns):
                return level
        
        return "Not Specified"

    def identify_strengths(self, text):
        """Identify key strengths based on resume content."""
        prompt = f"""
        Analyze the following resume text and identify the top 5 strengths based on achievements, 
        experience, and skills mentioned. Be specific and factual:
        
        {text[:2000]}
        """
        
        completion = self.groq_client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": "You are an expert HR analyst. Provide concise, specific strengths."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        strengths = completion.choices[0].message.content.split('\n')
        return [s.strip('- ') for s in strengths if s.strip('- ')][:5]

    def identify_gaps(self, text):
        """Identify areas for improvement based on industry standards and job market demands."""
        skills = self.extract_skills(text)
        experience_level = self.determine_experience_level(text)
        
        prompt = f"""
        Based on the candidate's profile:
        - Skills: {', '.join(skills)}
        - Experience Level: {experience_level}
        
        Identify 3-5 specific areas for improvement considering:
        1. Current industry trends
        2. Market demands
        3. Career progression requirements
        
        Provide specific, actionable areas only.
        """
        
        completion = self.groq_client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": "You are a career development expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        gaps = completion.choices[0].message.content.split('\n')
        return [g.strip('- ') for g in gaps if g.strip('- ')][:5]