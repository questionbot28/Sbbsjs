import os
import google.generativeai as genai
import json
import logging
import random
from question_bank_11 import get_stored_question_11
from question_bank_12 import get_stored_question_12

class QuestionGenerator:
    def __init__(self):
        self.logger = logging.getLogger('discord_bot')
        self._initialize_gemini_client()
        self.subjects = {
            'physics': [
                'Mechanics',
                'Thermodynamics',
                'Units and Measurements',
                'Motion in a Straight Line',
                'Motion in a Plane',
                'Laws of Motion',
                'Work, Energy and Power',
                'System of Particles and Rotational Motion',
                'Gravitation',
                'Mechanical Properties of Solids',
                'Mechanical Properties of Fluids',
                'Thermal Properties of Matter',
                'Kinetic Theory',
                'Oscillations',
                'Waves',
                'Electrostatics',
                'Current Electricity',
                'Magnetic Effects of Current',
                'Magnetism and Matter',
                'Electromagnetic Induction',
                'Alternating Current',
                'Electromagnetic Waves',
                'Ray Optics',
                'Wave Optics',
                'Dual Nature of Matter and Radiation',
                'Atoms',
                'Nuclei',
                'Semiconductor Electronics',
                'Communication Systems'
            ],
            'chemistry': [
                'Some Basic Concepts of Chemistry',
                'Structure of Atom',
                'Classification of Elements',
                'Chemical Bonding and Molecular Structure',
                'States of Matter',
                'Thermodynamics',
                'Equilibrium',
                'Redox Reactions',
                'Hydrogen',
                's-Block Elements',
                'p-Block Elements',
                'd and f Block Elements',
                'Coordination Compounds',
                'Environmental Chemistry',
                'Organic Chemistry: Basic Principles',
                'Hydrocarbons',
                'Haloalkanes and Haloarenes',
                'Alcohols, Phenols and Ethers',
                'Aldehydes, Ketones and Carboxylic Acids',
                'Amines',
                'Biomolecules',
                'Polymers',
                'Chemistry in Everyday Life',
                'Surface Chemistry',
                'Solutions',
                'Electrochemistry',
                'Chemical Kinetics'
            ],
            'mathematics': [
                'Sets',
                'Relations and Functions',
                'Trigonometric Functions',
                'Complex Numbers',
                'Linear Inequalities',
                'Permutations and Combinations',
                'Binomial Theorem',
                'Sequences and Series',
                'Straight Lines',
                'Conic Sections',
                'Introduction to 3D Geometry',
                'Limits and Derivatives',
                'Mathematical Reasoning',
                'Statistics',
                'Probability',
                'Matrices',
                'Determinants',
                'Continuity and Differentiability',
                'Applications of Derivatives',
                'Integrals',
                'Applications of Integrals',
                'Differential Equations',
                'Vector Algebra',
                'Three Dimensional Geometry',
                'Linear Programming'
            ],
            'biology': [
                'Diversity in Living World',
                'Structural Organization in Plants and Animals',
                'Cell Structure and Function',
                'Plant Physiology',
                'Human Physiology',
                'Reproduction',
                'Genetics and Evolution',
                'Biology and Human Welfare',
                'Biotechnology and its Applications',
                'Ecology and Environment',
                'Living World',
                'Biological Classification',
                'Plant Kingdom',
                'Animal Kingdom',
                'Morphology of Flowering Plants',
                'Anatomy of Flowering Plants',
                'Cell: The Unit of Life',
                'Biomolecules',
                'Cell Cycle and Cell Division',
                'Transport in Plants',
                'Mineral Nutrition',
                'Photosynthesis',
                'Respiration in Plants',
                'Plant Growth and Development',
                'Digestion and Absorption',
                'Breathing and Exchange of Gases',
                'Body Fluids and Circulation',
                'Excretory Products',
                'Locomotion and Movement',
                'Neural Control and Coordination',
                'Chemical Coordination and Integration'
            ],
            'business_studies': [
                'Nature and Purpose of Business',
                'Forms of Business Organisation',
                'Private, Public and Global Enterprises',
                'Business Services',
                'Emerging Modes of Business',
                'Social Responsibility of Business',
                'Formation of a Company',
                'Sources of Business Finance',
                'Small Business',
                'Internal Trade',
                'International Business',
                'Nature and Significance of Management',
                'Principles of Management',
                'Business Environment',
                'Planning',
                'Organising',
                'Staffing',
                'Directing',
                'Controlling',
                'Financial Management',
                'Financial Markets',
                'Marketing Management',
                'Consumer Protection',
                'Entrepreneurship Development'
            ],
            'accountancy': [
                'Introduction to Accounting',
                'Theory Base of Accounting',
                'Recording of Transactions-I',
                'Recording of Transactions-II',
                'Bank Reconciliation Statement',
                'Trial Balance and Rectification of Errors',
                'Depreciation, Provisions and Reserves',
                'Bills of Exchange',
                'Financial Statements',
                'Financial Statements - Not for Profit Organizations',
                'Accounts from Incomplete Records',
                'Applications of Computers in Accounting',
                'Accounting for Partnership Firms',
                'Reconstitution of Partnership',
                'Accounting for Share Capital',
                'Issue and Redemption of Debentures',
                'Financial Statement Analysis',
                'Accounting Ratios',
                'Cash Flow Statement',
                'Project Work'
            ],
            'economics': [
                'Introduction to Economics',
                'Consumer Equilibrium and Demand',
                'Producer Behaviour and Supply',
                'Forms of Market and Price Determination',
                'National Income and Related Aggregates',
                'Money and Banking',
                'Determination of Income and Employment',
                'Government Budget and the Economy',
                'Balance of Payments',
                'Indian Economic Development',
                'Development Experience (1947-90)',
                'Economic Reforms since 1991',
                'Current Challenges facing Indian Economy',
                'Development Experience of India',
                'Microeconomics: Introduction',
                'Central Problems of an Economy',
                'Consumer\'s Equilibrium',
                'Theory of Demand',
                'Theory of Supply',
                'Price Elasticity',
                'Production Function',
                'Cost and Revenue',
                'Market Structure',
                'National Income Accounting',
                'Money and Credit',
                'Income Determination',
                'Government Budget',
                'Foreign Exchange',
                'International Trade'
            ],
            'english': {
                11: [
                    'Hornbill - The Portrait of a Lady',
                    'Hornbill - We\'re Not Afraid to Die',
                    'Hornbill - Discovering Tut',
                    'Hornbill - Landscape of the Soul',
                    'Hornbill - The Ailing Planet',
                    'Hornbill - The Browning Version',
                    'Hornbill - The Adventure',
                    'Hornbill - Silk Road',
                    'Hornbill - Father to Son (Poem)',
                    'Snapshots - The Summer of the Beautiful White Horse',
                    'Snapshots - The Address',
                    'Snapshots - Ranga\'s Marriage',
                    'Snapshots - Albert Einstein at School',
                    'Snapshots - Mother\'s Day',
                    'Snapshots - Birth',
                    'Snapshots - The Tale of Melon City',
                    'Writing Skills - Notice Writing',
                    'Writing Skills - Report Writing',
                    'Writing Skills - Article Writing',
                    'Writing Skills - Letter Writing',
                    'Grammar and Language Skills'
                ],
                12: [
                    'Flamingo - The Last Lesson',
                    'Flamingo - Lost Spring',
                    'Flamingo - Deep Water',
                    'Flamingo - The Rattrap',
                    'Flamingo - Indigo',
                    'Flamingo - Poets and Pancakes',
                    'Flamingo - The Interview',
                    'Flamingo - Going Places',
                    'Flamingo - My Mother at Sixty-six (Poem)',
                    'Flamingo - An Elementary School Classroom in a Slum (Poem)',
                    'Flamingo - Keeping Quiet (Poem)',
                    'Flamingo - A Thing of Beauty (Poem)',
                    'Flamingo - A Roadside Stand (Poem)',
                    'Flamingo - Aunt Jennifer\'s Tigers (Poem)',
                    'Vistas - The Third Level',
                    'Vistas - The Tiger King',
                    'Vistas - Journey to the End of the Earth',
                    'Vistas - The Enemy',
                    'Vistas - Should Wizard Hit Mommy',
                    'Vistas - On the Face of It',
                    'Vistas - Evans Tries an O-Level',
                    'Vistas - Memories of Childhood',
                    'Writing Skills - Notice Writing',
                    'Writing Skills - Report Writing',
                    'Writing Skills - Article Writing',
                    'Writing Skills - Letter Writing',
                    'Grammar and Language Skills'
                ]
            }
        }
        self._used_questions_cache = {
            'physics': set(),
            'chemistry': set(),
            'mathematics': set(),
            'biology': set(),
            'business_studies': set(),
            'accountancy': set(),
            'economics': set(),
            'english': set()
        }
        self._cache_limit = 1000
        self._last_questions = {}  # Track last question per user-subject combination

    def _initialize_gemini_client(self):
        """Initialize the Gemini API client"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                self.logger.error("Google API key is not set")
                raise ValueError("Google API key is not configured")

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')

            # Test the API key with a simple completion
            response = self.model.generate_content("Test")
            if not response:
                raise ValueError("Failed to initialize Gemini API")

            self.logger.info("Gemini client initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing Gemini client: {str(e)}")
            raise ValueError(f"Gemini API Error: {str(e)}")

    async def generate_question(self, subject, topic=None, class_level=11, difficulty='medium', user_id=None):
        """Enhanced question generation with better error handling and uniqueness checks"""
        try:
            # Generate cache key that includes user_id to track per-user questions
            cache_key = self._get_cache_key(subject, topic, class_level, user_id)

            # First try to get a stored question as fallback
            if class_level == 11:
                stored_question = self.get_stored_question_11(subject, topic)
            else:
                stored_question = self.get_stored_question_12(subject, topic)

            if stored_question and not self._is_question_used(stored_question, cache_key):
                self.logger.info(f"Using stored question for {subject} {topic if topic else ''}")
                self._mark_question_used(stored_question, cache_key)
                return stored_question

            # If no stored question or it was used, try Gemini
            subject = subject.lower()

            prompt = self._create_enhanced_prompt(subject, topic, class_level, difficulty)

            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    response = self.model.generate_content(prompt)

                    if not response or not response.text:
                        continue

                    try:
                        result = json.loads(response.text)
                    except json.JSONDecodeError:
                        self.logger.warning(f"Invalid JSON response from Gemini, attempt {attempt + 1}")
                        continue

                    # Validate question format
                    if not all(key in result for key in ['question', 'options', 'correct_answer', 'explanation']):
                        self.logger.warning(f"Invalid question format received, attempt {attempt + 1}")
                        continue

                    # Only return if question is unique
                    if not self._is_question_used(result, cache_key):
                        self._mark_question_used(result, cache_key)
                        return result

                except Exception as api_error:
                    self.logger.error(f"API error on attempt {attempt + 1}: {api_error}")
                    if attempt == max_attempts - 1:
                        raise ValueError(f"Gemini API Error: {str(api_error)}")

            # If we couldn't get a unique question, clear cache and try one more time
            self._clear_cache_for_user(user_id, subject)
            return await self.generate_question(subject, topic, class_level, difficulty, user_id)

        except Exception as e:
            self.logger.error(f"Failed to generate question: {e}")
            return None

    def _get_cache_key(self, subject: str, topic: str | None, class_level: int, user_id: str | None) -> str:
        """Generate a more specific cache key for tracking used questions per user"""
        user_part = f"user_{user_id}" if user_id else "global"
        return f"{user_part}:{subject}:{topic or 'all'}:{class_level}"

    def _clear_cache_for_user(self, user_id: str | None, subject: str):
        """Clear the question cache for a specific user and subject"""
        if user_id:
            cache_key_prefix = f"user_{user_id}:{subject}"
            self._used_questions_cache[subject] = {
                q for q in self._used_questions_cache[subject]
                if not q.startswith(cache_key_prefix)
            }

    def _is_question_used(self, question: dict, cache_key: str) -> bool:
        """Enhanced check for used questions with subject-specific caching"""
        subject = cache_key.split(':')[1]  # Now subject is the second part after user_id

        if subject not in self._used_questions_cache:
            self._used_questions_cache[subject] = set()

        # Create a unique identifier for the question using both question text and options
        question_id = f"{cache_key}:{question['question'][:100]}_{'-'.join(question['options'])[:100]}"

        # Also check if this was the last question for this user-subject combination
        last_question_key = f"{cache_key}:last"
        if last_question_key in self._last_questions and self._last_questions[last_question_key] == question_id:
            return True

        return question_id in self._used_questions_cache[subject]

    def _mark_question_used(self, question: dict, cache_key: str):
        """Mark a question as used in the subject-specific cache"""
        subject = cache_key.split(':')[1]

        if subject not in self._used_questions_cache:
            self._used_questions_cache[subject] = set()

        # Create a unique identifier for the question
        question_id = f"{cache_key}:{question['question'][:100]}_{'-'.join(question['options'])[:100]}"

        # Update last question for this user-subject combination
        last_question_key = f"{cache_key}:last"
        self._last_questions[last_question_key] = question_id

        # Implement cache size limit
        if len(self._used_questions_cache[subject]) >= self._cache_limit:
            # Remove oldest entries (20% of cache) when limit is reached
            remove_count = int(self._cache_limit * 0.2)
            self._used_questions_cache[subject] = set(list(self._used_questions_cache[subject])[remove_count:])

        self._used_questions_cache[subject].add(question_id)

    def _create_enhanced_prompt(self, subject, topic, class_level, difficulty):
        """Create an enhanced prompt for more varied questions"""
        topic_text = f" on {topic}" if topic else ""
        difficulty_prompts = {
            'easy': 'focus on fundamental concepts and basic understanding',
            'medium': 'include application of concepts and moderate complexity',
            'hard': 'challenge students with complex problem-solving and deeper understanding'
        }

        return f"""
        Generate a unique NCERT-based question for class {class_level} {subject}{topic_text} at {difficulty} difficulty level.
        {difficulty_prompts.get(difficulty, difficulty_prompts['medium'])}
        Requirements:
        - Question should be directly from or based on NCERT textbooks
        - Must be different from previously generated questions
        - Should include practical applications or real-world context where applicable
        - If topic is specified, question must specifically address that topic
        - Include detailed explanation with NCERT reference

        Return the response in this exact JSON format:
        {{
            "question": "The complete question text",
            "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
            "correct_answer": "The correct option letter (A, B, C, or D)",
            "explanation": "Detailed step-by-step explanation with NCERT reference"
        }}
        """

    def _get_cache_key(self, subject: str, topic: str | None, class_level: int) -> str:
        """Generate a more specific cache key for tracking used questions"""
        return f"{subject}:{topic or 'all'}:{class_level}"

    def _is_question_used(self, question: dict, cache_key: str) -> bool:
        """Enhanced check for used questions with subject-specific caching"""
        subject = cache_key.split(':')[0]

        if subject not in self._used_questions_cache:
            self._used_questions_cache[subject] = set()

        # Create a unique identifier for the question using both question text and options
        question_id = f"{question['question'][:100]}_{'-'.join(question['options'])[:100]}"
        return question_id in self._used_questions_cache[subject]

    def _mark_question_used(self, question: dict, cache_key: str):
        """Mark a question as used in the subject-specific cache"""
        subject = cache_key.split(':')[0]

        if subject not in self._used_questions_cache:
            self._used_questions_cache[subject] = set()

        # Create a unique identifier for the question
        question_id = f"{question['question'][:100]}_{'-'.join(question['options'])[:100]}"

        # Implement cache size limit
        if len(self._used_questions_cache[subject]) >= self._cache_limit:
            # Remove oldest entries (20% of cache) when limit is reached
            remove_count = int(self._cache_limit * 0.2)
            self._used_questions_cache[subject] = set(list(self._used_questions_cache[subject])[remove_count:])

        self._used_questions_cache[subject].add(question_id)

    def get_stored_question_11(self, subject: str, topic: str | None = None) -> dict | None:
        """
        Retrieve a pre-stored question from the class 11 question bank
        """
        try:
            return get_stored_question_11(subject, topic)
        except Exception as e:
            self.logger.error(f"Error getting class 11 question: {e}")
            return None

    def get_stored_question_12(self, subject: str, topic: str | None = None) -> dict | None:
        """
        Retrieve a pre-stored question from the class 12 question bank
        """
        try:
            return get_stored_question_12(subject, topic)
        except Exception as e:
            self.logger.error(f"Error getting class 12 question: {e}")
            return None

    def get_subjects(self):
        """Get all available subjects"""
        return list(self.subjects.keys())

    def get_topics(self, subject):
        """Get all available topics for a subject"""
        if subject == 'english':
            return self.subjects['english'].get(11, [])  # Only return class 11 topics by default

        subject = subject.lower()
        if subject not in self.subjects:
            return []

        topics = self.subjects.get(subject, [])
        if isinstance(topics, dict):
            return list(topics.keys())
        return topics

    def get_class_specific_topics(self, subject, class_level):
        """Get topics specific to a class level for subjects that have different topics per class"""
        subject = subject.lower()

        if subject == 'english':
            return self.subjects['english'].get(class_level, [])

        return self.get_topics(subject)

    def get_stored_question(self, subject: str, topic: str | None, class_level: int) -> dict | None:
        """Generate a new question instead of using stored ones"""
        return self.generate_question(subject, topic, class_level)