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
            'physics': [
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
                'Thermodynamics',
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
        self._used_questions_cache = {}  # Store generated questions to prevent duplicates

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
        """Get a stored question from the appropriate question bank"""
        if class_level == 11:
            return get_stored_question_11(subject, topic)
        elif class_level == 12:
            return get_stored_question_12(subject, topic)
        return None

    def _get_cache_key(self, subject: str, topic: str | None, class_level: int) -> str:
        """Generate a cache key for tracking used questions"""
        return f"{subject}:{topic or 'all'}:{class_level}"

    def _is_question_used(self, question: dict, cache_key: str) -> bool:
        """Check if a question has been used recently"""
        if cache_key not in self._used_questions_cache:
            self._used_questions_cache[cache_key] = set()

        # Use a substring of the question text as the identifier
        question_id = f"{question['question'][:100]}"
        return question_id in self._used_questions_cache[cache_key]

    def _mark_question_used(self, question: dict, cache_key: str):
        """Mark a question as used"""
        if cache_key not in self._used_questions_cache:
            self._used_questions_cache[cache_key] = set()

        question_id = f"{question['question'][:100]}"
        self._used_questions_cache[cache_key].add(question_id)

    async def generate_question(self, subject, topic=None, class_level=11, difficulty='medium'):
        """Generate a new question using OpenAI"""
        try:
            subject = subject.lower()
            cache_key = self._get_cache_key(subject, topic, class_level)

            if not os.getenv('OPENAI_API_KEY'):
                self.logger.error("OpenAI API key is not set")
                raise Exception("OpenAI API key is not configured")

            # Generate a new question using OpenAI
            prompt = self._create_prompt(subject, topic, class_level, difficulty)
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an educational question generator for class {class_level} students focusing on NCERT curriculum."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )

                result = json.loads(response.choices[0].message.content)

                # Only return and cache the question if it's unique
                if not self._is_question_used(result, cache_key):
                    self._mark_question_used(result, cache_key)
                    return result

                # If we got a duplicate, try one more time
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are an educational question generator for class {class_level} students. Generate a completely different question from previous ones."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )

                result = json.loads(response.choices[0].message.content)
                self._mark_question_used(result, cache_key)
                return result

            except Exception as api_error:
                self.logger.error(f"OpenAI API error: {api_error}")
                raise Exception(f"Failed to generate question via OpenAI: {api_error}")

        except Exception as e:
            self.logger.error(f"Failed to generate question: {e}")
            raise Exception(f"Failed to generate question: {e}")

    def _create_prompt(self, subject, topic, class_level, difficulty):
        topic_text = f" on {topic}" if topic else ""
        return f"""
        Generate a NCERT-based question for class {class_level} {subject}{topic_text} at {difficulty} difficulty level.
        The question should be directly from or based on NCERT textbooks.
        If the topic is specified, ensure the question is specifically about that topic.
        The response should be in JSON format with the following structure:
        {{
            "question": "The question text",
            "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
            "correct_answer": "The correct option letter (A, B, C, or D)",
            "explanation": "Detailed explanation of the answer with NCERT reference"
        }}
        """