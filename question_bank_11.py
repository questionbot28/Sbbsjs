# Dictionary to store pre-defined questions for class 11
QUESTION_BANK_11 = {
    'physics': {
        'Mechanics': [
            {
                'question': '''A stone is thrown vertically upward with an initial velocity of 19.6 m/s from the top of a building of height 25m. Calculate:
1. The maximum height reached by the stone above the ground
2. The time taken by the stone to reach the ground
3. The velocity with which it hits the ground

(Take g = 9.8 m/s²)''',
                'options': [
                    'A) 45m, 3.5s, 29.4 m/s',
                    'B) 44.6m, 3.27s, 32.1 m/s',
                    'C) 44.6m, 4s, 39.2 m/s',
                    'D) 45m, 3.27s, 29.4 m/s'
                ],
                'correct_answer': 'B',
                'explanation': '''Let's solve this step by step:

1. Maximum height calculation:
   - Initial velocity (u) = 19.6 m/s
   - Using v² = u² + 2gh where v = 0 at max height
   - 0 = (19.6)² + 2(-9.8)h₁
   - h₁ = 19.6 meters above the building
   - Total height = 25 + 19.6 = 44.6m

2. Time to reach ground:
   - Using h = ut + (1/2)gt²
   - -25 = 19.6t - 4.9t²
   - Solving quadratic equation: t = 3.27s

3. Final velocity:
   - Using v = u + gt
   - v = 19.6 + (-9.8)(3.27)
   - v = 32.1 m/s'''
            }
        ],
        'Waves': [
            {
                'question': '''A simple harmonic oscillator consists of a mass m attached to a spring with spring constant k. If the mass is displaced from its equilibrium position and released, what is the formula for its period of oscillation?''',
                'options': [
                    'A) T = 2π√(m/k)',
                    'B) T = 2π√(k/m)',
                    'C) T = π√(m/k)',
                    'D) T = π√(k/m)'
                ],
                'correct_answer': 'A',
                'explanation': '''The period (T) of a simple harmonic oscillator is given by:
T = 2π√(m/k)

This formula shows that:
1. The period is directly proportional to the square root of the mass
2. The period is inversely proportional to the square root of the spring constant
3. The period is independent of the amplitude of oscillation'''
            }
        ]
    },
    'chemistry': {
        'Chemical Bonding': [
            {
                'question': '''Which of the following statements about hydrogen bonding is INCORRECT?''',
                'options': [
                    'A) It is stronger than covalent bonds',
                    'B) It occurs between H and electronegative atoms',
                    'C) It affects the boiling point of compounds',
                    'D) It is important in DNA structure'
                ],
                'correct_answer': 'A',
                'explanation': '''Hydrogen bonding is a type of intermolecular force that:
1. Is weaker than covalent bonds (making option A incorrect)
2. Forms between a hydrogen atom bonded to a highly electronegative atom (like N, O, or F) and another electronegative atom
3. Influences physical properties like boiling point
4. Plays a crucial role in biological structures like DNA'''
            }
        ]
    },
    'business_studies': {
        'Business Environment': [
            {
                'question': '''Which of the following is NOT a component of the business environment?

Consider the various aspects that affect business operations and identify the one that does NOT belong to either the micro or macro environment of business.''',
                'options': [
                    'A) Economic conditions',
                    'B) Personal hobbies',
                    'C) Government policies',
                    'D) Market competition'
                ],
                'correct_answer': 'B',
                'explanation': '''The business environment consists of:
1. Micro environment: Factors in immediate business environment (suppliers, customers, competitors)
2. Macro environment: Broader factors (economic, social, political, legal)

Personal hobbies are not part of either environment as they don't directly impact business operations.
Other options are valid components:
- Economic conditions affect business decisions
- Government policies create the regulatory framework
- Market competition influences business strategy'''
            }
        ],
        'Management Principles': [
            {
                'question': '''In the context of Henry Fayol's 14 principles of management, what does the principle of 'Scalar Chain' refer to?''',
                'options': [
                    'A) Division of work among employees',
                    'B) Line of authority from top to bottom',
                    'C) Unity of command in organization',
                    'D) Monetary compensation to workers'
                ],
                'correct_answer': 'B',
                'explanation': '''Scalar Chain principle by Henry Fayol refers to:
1. The line of authority and communication from top to bottom
2. A clear hierarchy where each employee knows their supervisor
3. Creates a clear reporting structure in the organization

This principle ensures:
- Clear communication channels
- Proper flow of information
- Defined responsibility and authority levels
- Organizational discipline and order'''
            }
        ]
    },
    'accountancy': {
        'Basic Accounting': [
            {
                'question': '''Which of the following is the correct accounting equation?''',
                'options': [
                    'A) Assets = Liabilities + Capital',
                    'B) Assets + Liabilities = Capital',
                    'C) Assets = Liabilities - Capital',
                    'D) Assets + Capital = Liabilities'
                ],
                'correct_answer': 'A',
                'explanation': '''The fundamental accounting equation is:
Assets = Liabilities + Capital (Owner's Equity)

This equation is based on the dual aspect concept where:
1. Every debit has a corresponding credit
2. Total assets must equal total claims (liabilities + owner's equity)
3. This equation holds true at all times

For example:
- If you start a business with $10,000 cash: Assets ($10,000) = Capital ($10,000)
- If you buy inventory worth $6,000 on credit: Assets ($10,000) = Liabilities ($6,000) + Capital ($4,000)'''
            }
        ]
    },
    'economics': {
        'Microeconomics': [
            {
                'question': '''What happens to the demand curve when there is an increase in the price of a complementary good?''',
                'options': [
                    'A) Shifts right',
                    'B) Shifts left',
                    'C) Moves along the curve',
                    'D) Remains unchanged'
                ],
                'correct_answer': 'B',
                'explanation': '''When the price of a complementary good increases:
1. Complementary goods are used together (e.g., cars and petrol)
2. When price of one increases, demand for both decreases
3. This causes the demand curve to shift left

Example:
- If petrol prices increase:
  * People drive less
  * Demand for cars decreases
  * Entire demand curve shifts left
  * This is different from movement along the curve, which happens due to price changes of the good itself'''
            }
        ]
    },
    'english': {
        'Literature': [
            {
                'question': '''Read the following extract and answer the question:

"All the world's a stage,
And all the men and women merely players;
They have their exits and their entrances,
And one man in his time plays many parts..."

Which literary device is predominantly used in these lines from Shakespeare's "As You Like It"?''',
                'options': [
                    'A) Personification',
                    'B) Extended Metaphor',
                    'C) Hyperbole',
                    'D) Alliteration'
                ],
                'correct_answer': 'B',
                'explanation': '''The correct answer is Extended Metaphor:

1. Shakespeare uses an extended metaphor comparing:
   - The world to a stage
   - People to actors ("players")
   - Life events to entrances and exits
   - Different phases of life to different parts in a play

2. This metaphor:
   - Continues throughout the passage
   - Creates a sustained comparison
   - Develops multiple parallel aspects
   - Is a signature device in Shakespearean works'''
            }
        ],
        'Grammar': [
            {
                'question': '''Identify the type of clause in the underlined portion of the sentence:

"The book that I borrowed from the library yesterday is very interesting."''',
                'options': [
                    'A) Independent Clause',
                    'B) Noun Clause',
                    'C) Adjective Clause',
                    'D) Adverb Clause'
                ],
                'correct_answer': 'C',
                'explanation': '''Let's analyze this step by step:

1. The underlined portion "that I borrowed from the library yesterday" is an Adjective Clause because:
   - It modifies the noun "book"
   - It begins with the relative pronoun "that"
   - It gives more information about the noun
   - It cannot stand alone as a complete sentence

2. Key characteristics of an Adjective Clause:
   - Describes a noun or pronoun
   - Usually begins with relative pronouns (who, whom, whose, which, that)
   - Functions as an adjective in the sentence'''
            }
        ],
        'Writing Skills': [
            {
                'question': '''Which of the following is NOT a characteristic of a well-written formal letter?''',
                'options': [
                    'A) Clear and concise language',
                    'B) Proper salutation and closing',
                    'C) Use of casual abbreviations and emoticons',
                    'D) Correct format and layout'
                ],
                'correct_answer': 'C',
                'explanation': '''A formal letter should maintain professionalism:

1. Formal letters should have:
   - Professional tone and language
   - Proper structure and formatting
   - Clear and direct communication

2. Casual elements like abbreviations and emoticons are inappropriate because:
   - They reduce professionalism
   - Can be misinterpreted
   - Don't conform to business writing standards
   - May not be understood by all readers'''
            }
        ]
    }
}

def get_stored_question_11(subject: str, topic: str | None = None) -> dict | None:
    """
    Retrieve a pre-stored question from the class 11 question bank
    """
    subject = subject.lower() if subject else ""
    if not subject or subject not in QUESTION_BANK_11:
        return None

    if topic:
        topic_questions = QUESTION_BANK_11[subject].get(topic, [])
    else:
        # If no topic specified, get questions from all topics
        topic_questions = []
        for questions in QUESTION_BANK_11[subject].values():
            topic_questions.extend(questions)

    return topic_questions[0] if topic_questions else None