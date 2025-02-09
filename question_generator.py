import os
import json
import logging
import random
from typing import Optional, Dict, Any
import google.generativeai as genai
from question_bank import get_stored_question

class QuestionGenerator:
    def __init__(self):
        self.logger = logging.getLogger('discord_bot')
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate_question(
        self,
        subject: str,
        topic: Optional[str] = None,
        class_level: int = 11,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a question using Gemini API or fallback to stored questions
        """
        try:
            # First try to generate using Gemini
            question = await self._generate_with_gemini(subject, topic, class_level)
            if question:
                self.logger.info("Successfully generated question using Gemini")
                return question

        except Exception as e:
            self.logger.error(f"Gemini question generation failed: {str(e)}")

        # Fallback to stored questions
        self.logger.info(f"Falling back to stored questions for {subject} {topic if topic else ''}")
        stored_question = get_stored_question(subject, topic)

        if not stored_question:
            self.logger.error(f"No stored questions found for {subject} {topic if topic else ''}")
            # Create a generic question as last resort
            return {
                "question": f"What is the most fundamental concept in {subject} {topic if topic else ''}?",
                "options": [
                    "A) Option 1",
                    "B) Option 2",
                    "C) Option 3",
                    "D) Option 4"
                ],
                "correct_answer": "A",
                "explanation": "Please contact your teacher for a detailed explanation."
            }

        return stored_question

    async def _generate_with_gemini(
        self,
        subject: str,
        topic: Optional[str],
        class_level: int
    ) -> Optional[Dict[str, Any]]:
        """Generate a question using Gemini API"""
        try:
            prompt = self._create_prompt(subject, topic, class_level)
            self.logger.debug(f"Sending prompt to Gemini: {prompt}")

            # Generate response using Gemini
            response = await self._get_gemini_response(prompt)

            if not response:
                return None

            # Log the raw response for debugging
            self.logger.debug(f"Raw Gemini response: {response}")

            # Try to extract JSON from the response
            try:
                # Look for JSON-like structure in the response
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1

                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    question_data = json.loads(json_str)

                    # Validate required fields
                    required_fields = ['question', 'options', 'correct_answer']
                    if all(field in question_data for field in required_fields):
                        self.logger.info("Successfully parsed Gemini response")
                        return question_data

                self.logger.error("Generated question missing required fields")
                return None

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
                return None

        except Exception as e:
            self.logger.error(f"Error in Gemini question generation: {str(e)}")
            return None

    def _create_prompt(self, subject: str, topic: Optional[str], class_level: int) -> str:
        """Create the prompt for Gemini"""
        base_prompt = (
            "You are a question generator for NCERT curriculum. "
            f"Generate a multiple-choice question for class {class_level} {subject}"
            f"{' on ' + topic if topic else ''}. "
            "\nIMPORTANT: You must respond with ONLY a JSON object in the following format:\n"
            "{\n"
            '  "question": "The question text",\n'
            '  "options": ["A) option1", "B) option2", "C) option3", "D) option4"],\n'
            '  "correct_answer": "A",\n'
            '  "explanation": "Detailed explanation of the answer"\n'
            "}\n\n"
            "Requirements:\n"
            "1. Response must be ONLY the JSON object, no other text\n"
            "2. Question must be age-appropriate for the class level\n"
            "3. Question must be clear and unambiguous\n"
            "4. Must have exactly one correct answer\n"
            "5. Must include a detailed explanation\n"
            "6. All JSON fields are required"
        )
        return base_prompt

    async def _get_gemini_response(self, prompt: str) -> Optional[str]:
        """Get response from Gemini API"""
        try:
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            return None