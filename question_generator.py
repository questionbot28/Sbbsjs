import os
from openai import OpenAI
import json
from question_bank_11 import get_stored_question_11
from question_bank_12 import get_stored_question_12
import logging

class QuestionGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.logger = logging.getLogger('discord_bot')
        self.subjects = {
            'physics': ['Mechanics', 'Waves', 'Thermodynamics', 'Electrostatics'],
            'chemistry': ['Chemical Bonding', 'Electrochemistry', 'Organic Chemistry', 'Physical Chemistry'],
            'mathematics': ['Calculus', 'Algebra', 'Trigonometry', 'Statistics'],
            'biology': ['Cell Biology', 'Genetics', 'Human Physiology', 'Ecology'],
            'business_studies': ['Business Environment', 'Business Organization', 'Management Principles', 'Financial Markets'],
            'accountancy': ['Basic Accounting', 'Trial Balance', 'Financial Statements', 'Partnership Accounts'],
            'economics': ['Microeconomics', 'Macroeconomics', 'Money and Banking', 'International Trade'],
            'english': {
                11: [
                    'Hornbill - Prose',
                    'Hornbill - Poetry',
                    'Snapshots',
                    'Grammar and Language Skills',
                    'Writing Skills'
                ],
                12: [
                    'Flamingo - Prose',
                    'Flamingo - Poetry',
                    'Vistas',
                    'Grammar and Language Skills',
                    'Writing Skills'
                ]
            }
        }

    def get_subjects(self):
        """Get all available subjects"""
        return list(self.subjects.keys())

    def get_topics(self, subject):
        if subject == 'english':
            return self.subjects['english'].get(11, [])  # Only return class 11 topics by default
        return self.subjects.get(subject, [])

    def get_class_specific_topics(self, subject, class_level):
        """Get topics specific to a class level for subjects that have different topics per class"""
        if subject == 'english':
            return self.subjects['english'].get(class_level, [])
        return self.subjects.get(subject, [])

    async def generate_question(self, subject, topic=None, class_level=11, difficulty='medium'):
        try:
            # First try to get a question from our question bank based on class level
            stored_question = None
            if class_level == 11:
                stored_question = get_stored_question_11(subject, topic)
            elif class_level == 12:
                stored_question = get_stored_question_12(subject, topic)

            if stored_question:
                return stored_question

            # If no stored question is found, generate one using OpenAI
            prompt = self._create_prompt(subject, topic, class_level, difficulty)

            # Verify OpenAI API key
            if not os.getenv('OPENAI_API_KEY'):
                self.logger.error("OpenAI API key is not set")
                raise Exception("OpenAI API key is not configured")

            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using GPT-3.5-turbo model
                    messages=[
                        {"role": "system", "content": f"You are an educational question generator for class {class_level} students focusing on NCERT curriculum."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )

                result = json.loads(response.choices[0].message.content)
                return result

            except Exception as api_error:
                self.logger.error(f"OpenAI API error: {api_error}")
                raise Exception(f"Failed to generate question via OpenAI: {api_error}")

        except Exception as e:
            self.logger.error(f"Failed to generate question: {e}")
            raise Exception(f"Failed to generate question: {e}")

    def _create_prompt(self, subject, topic, class_level, difficulty):
        return f"""
        Generate a NCERT-based question for class {class_level} {subject} {'on ' + topic if topic else ''} at {difficulty} difficulty level.
        The question should be directly from or based on NCERT textbooks.
        The response should be in JSON format with the following structure:
        {{
            "question": "The question text",
            "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
            "correct_answer": "The correct option letter (A, B, C, or D)",
            "explanation": "Detailed explanation of the answer with NCERT reference"
        }}
        """