# Dictionary to store pre-defined questions for classes 11 and 12
QUESTION_BANK = {
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
            },
            {
                'question': '''A physics experiment involves a complex pendulum setup:

A compound pendulum consists of a uniform rod of length L = 2m and mass M = 1kg, with an additional point mass m = 0.5kg attached at a distance l = 0.5m from the pivot point. Calculate the moment of inertia of this system about the pivot point.

Given:
- Moment of inertia of a uniform rod about its end = (ML²)/3
- Point mass moment of inertia = ml²
- Use parallel axis theorem where needed''',
                'options': [
                    'A) 1.458 kg⋅m²',
                    'B) 1.333 kg⋅m²',
                    'C) 1.125 kg⋅m²',
                    'D) 2.000 kg⋅m²'
                ],
                'correct_answer': 'A',
                'explanation': '''This complex problem can be solved step by step:

1. First, calculate the moment of inertia of the rod:
   I_rod = (ML²)/3 = (1 × 2²)/3 = 1.333 kg⋅m²

2. Calculate the moment of inertia of the point mass:
   I_point = ml² = 0.5 × 0.5² = 0.125 kg⋅m²

3. Total moment of inertia:
   I_total = I_rod + I_point = 1.333 + 0.125 = 1.458 kg⋅m²

Therefore, the total moment of inertia is 1.458 kg⋅m²'''
            }
        ],
        'Thermodynamics': [
            {
                'question': '''Consider a heat engine operating between two reservoirs:

The engine operates in a cycle between a hot reservoir at 400K and a cold reservoir at 300K. In one cycle:
1. It absorbs 800J of heat from the hot reservoir
2. It does work W
3. It rejects heat Qc to the cold reservoir

Calculate:
a) The maximum possible efficiency of this engine
b) The maximum work that can be done per cycle
c) The heat rejected to the cold reservoir in the most efficient operation''',
                'options': [
                    'A) 25%, 200J, 600J',
                    'B) 25%, 150J, 650J',
                    'C) 33%, 200J, 600J',
                    'D) 33%, 264J, 536J'
                ],
                'correct_answer': 'A',
                'explanation': '''Let's solve this step by step:

1. Maximum efficiency (Carnot efficiency):
   η = 1 - Tc/Th = 1 - 300/400 = 0.25 or 25%

2. Maximum work:
   W = η × Qh = 0.25 × 800J = 200J

3. Heat rejected (from First Law of Thermodynamics):
   Qc = Qh - W = 800J - 200J = 600J

This represents the ideal Carnot cycle, which gives the maximum possible efficiency for any heat engine operating between these temperatures.'''
            }
        ]
    }
}

def get_stored_question(subject: str, topic: str = None) -> dict:
    """
    Retrieve a pre-stored question from the question bank
    """
    subject = subject.lower()
    if subject not in QUESTION_BANK:
        return None

    if topic:
        if topic not in QUESTION_BANK[subject]:
            return None
        questions = QUESTION_BANK[subject][topic]
    else:
        # If no topic specified, get questions from all topics
        questions = []
        for topic_questions in QUESTION_BANK[subject].values():
            questions.extend(topic_questions)

    if not questions:
        return None

    # For now, return the first question. In a real implementation,
    # you might want to randomize this or implement some selection logic
    return questions[0]