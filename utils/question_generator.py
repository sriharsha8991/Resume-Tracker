import os
import groq
from dotenv import load_dotenv

class QuestionGenerator:
    def __init__(self):
        load_dotenv()
        self.groq_client = groq.Client(api_key=os.getenv('GROQ_API_KEY'))
        
    def generate_questions(self, role, skills, experience_level):
        prompt = f"""
        Generate interview questions for:
        Role: {role}
        Required Skills: {skills}
        Experience Level: {experience_level}

        Provide:
        1. 3 Technical questions specific to the role and skills
        2. 3 Behavioral questions focusing on past experiences
        3. 2 Problem-solving scenarios
        
        Format each section clearly with headers.
        """
        
        completion = self.groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content