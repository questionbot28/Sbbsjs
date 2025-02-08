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