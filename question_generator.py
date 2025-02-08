import os
from openai import OpenAI
import json
from question_bank import get_stored_question

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

class QuestionGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.subjects = {
            'physics': ['Mechanics', 'Thermodynamics', 'Electromagnetism', 'Modern Physics'],
            'chemistry': ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry'],
            'mathematics': ['Calculus', 'Algebra', 'Trigonometry', 'Statistics'],
            'biology': ['Cell Biology', 'Genetics', 'Human Physiology', 'Ecology']
        }

    async def generate_question(self, subject, topic=None, difficulty='medium'):
        try:
            # First try to get a question from our question bank
            stored_question = get_stored_question(subject, topic)
            if stored_question:
                return stored_question

            # If no stored question is found, generate one using OpenAI
            prompt = self._create_prompt(subject, topic, difficulty)
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an educational question generator for class 11 and 12 students."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            raise Exception(f"Failed to generate question: {e}")

    def _create_prompt(self, subject, topic, difficulty):
        return f"""
        Generate a question for {subject} {'on ' + topic if topic else ''} at {difficulty} difficulty level.
        The response should be in JSON format with the following structure:
        {{
            "question": "The question text",
            "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
            "correct_answer": "The correct option letter (A, B, C, or D)",
            "explanation": "Detailed explanation of the answer"
        }}
        """

    def get_subjects(self):
        return list(self.subjects.keys())

    def get_topics(self, subject):
        return self.subjects.get(subject, [])