# Dictionary to store pre-defined questions for class 12
QUESTION_BANK_12 = {
    'physics': {
        'Electrostatics': [
            {
                'question': '''A parallel plate capacitor has plates of area A separated by distance d. A dielectric slab of thickness d/2 and dielectric constant K is inserted between the plates. What is the new capacitance in terms of the original capacitance C₀?''',
                'options': [
                    'A) 2KC₀/(K+1)',
                    'B) (K+1)C₀/2',
                    'C) KC₀',
                    'D) 2KC₀'
                ],
                'correct_answer': 'A',
                'explanation': '''Let's solve this step by step:

1. Original capacitance C₀ = ε₀A/d
2. With dielectric partially inserted:
   - The capacitor can be treated as two capacitors in series
   - One with dielectric (thickness d/2, capacitance C₁)
   - One without dielectric (thickness d/2, capacitance C₂)
3. For the part with dielectric:
   C₁ = 2Kε₀A/d = 2KC₀
4. For the part without dielectric:
   C₂ = 2ε₀A/d = 2C₀
5. Total capacitance (series combination):
   1/C = 1/C₁ + 1/C₂
   1/C = 1/(2KC₀) + 1/(2C₀)
   C = 2KC₀/(K+1)'''
            }
        ],
        'Quantum Physics': [
            {
                'question': '''Consider a photon and an electron, both with wavelength λ. Which of the following statements is correct about their momenta?''',
                'options': [
                    'A) Photon has more momentum',
                    'B) Electron has more momentum',
                    'C) Both have equal momentum',
                    'D) Cannot be compared without knowing their energies'
                ],
                'correct_answer': 'B',
                'explanation': '''Let's analyze this:

1. For a photon:
   - p = h/λ where h is Planck's constant

2. For an electron:
   - Using de Broglie's relation: λ = h/p
   - Therefore, p = h/λ
   - But electron also has rest mass energy
   - So total energy E = √((pc)² + (mc²)²)
   - For the same wavelength, electron has additional mass term
   - Thus, electron momentum > photon momentum'''
            }
        ]
    },
    'chemistry': {
        'Electrochemistry': [
            {
                'question': '''An electrochemical cell is constructed with the following half-cells:
Zn|Zn²⁺(1.0 M) || Ag⁺(1.0 M)|Ag

Given:
E°(Zn²⁺/Zn) = -0.76 V
E°(Ag⁺/Ag) = +0.80 V

Calculate:
1. The cell potential under standard conditions
2. The cell reaction
3. The direction of electron flow''',
                'options': [
                    'A) 1.56 V, Zn + 2Ag⁺ → Zn²⁺ + 2Ag, Zn to Ag',
                    'B) 0.04 V, 2Ag + Zn²⁺ → 2Ag⁺ + Zn, Ag to Zn',
                    'C) 1.56 V, 2Ag + Zn²⁺ → 2Ag⁺ + Zn, Ag to Zn',
                    'D) 0.04 V, Zn + 2Ag⁺ → Zn²⁺ + 2Ag, Zn to Ag'
                ],
                'correct_answer': 'A',
                'explanation': '''Let's solve this step by step:

1. Cell potential calculation:
   E°cell = E°cathode - E°anode
   E°cell = E°(Ag⁺/Ag) - E°(Zn²⁺/Zn)
   E°cell = 0.80 V - (-0.76 V) = 1.56 V

2. Cell reaction:
   - Oxidation (anode): Zn → Zn²⁺ + 2e⁻
   - Reduction (cathode): 2Ag⁺ + 2e⁻ → 2Ag
   - Overall: Zn + 2Ag⁺ → Zn²⁺ + 2Ag

3. Electron flow:
   - Electrons flow from anode (Zn) to cathode (Ag)
   - Higher potential means more tendency to be reduced
   - Therefore, electrons flow from Zn to Ag'''
            }
        ]
    }
}

def get_stored_question_12(subject: str, topic: str | None = None) -> dict | None:
    """
    Retrieve a pre-stored question from the class 12 question bank
    """
    subject = subject.lower() if subject else ""
    if not subject or subject not in QUESTION_BANK_12:
        return None

    if topic:
        topic_questions = QUESTION_BANK_12[subject].get(topic, [])
    else:
        # If no topic specified, get questions from all topics
        topic_questions = []
        for questions in QUESTION_BANK_12[subject].values():
            topic_questions.extend(questions)

    return topic_questions[0] if topic_questions else None