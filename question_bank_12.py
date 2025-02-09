import random

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
        ]
    },
    'english': {
        'Literature': [
            {
                'question': '''Analyze the following lines from John Keats's "Ode to Autumn":

"Season of mists and mellow fruitfulness,
Close bosom-friend of the maturing sun;
Conspiring with him how to load and bless
With fruit the vines that round the thatch-eves run;"

What is the dominant poetic device used to describe autumn in these lines?''',
                'options': [
                    'A) Personification',
                    'B) Simile',
                    'C) Onomatopoeia',
                    'D) Alliteration'
                ],
                'correct_answer': 'A',
                'explanation': '''The dominant poetic device is Personification:

1. Autumn is personified as:
   - A "close bosom-friend" of the sun
   - Someone capable of "conspiring" with the sun
   - An active agent that can "load and bless"

2. This personification:
   - Gives human qualities to the season
   - Creates a vivid and relatable image
   - Helps readers connect emotionally with nature
   - Enhances the poem's romantic qualities'''
            }
        ],
        'Grammar and Language Skills': [
            {
                'question': '''Which organizational pattern would be most effective for writing an essay comparing traditional classroom learning with online education?''',
                'options': [
                    'A) Chronological order',
                    'B) Point-by-point comparison',
                    'C) Cause and effect',
                    'D) Process analysis'
                ],
                'correct_answer': 'B',
                'explanation': '''A point-by-point comparison is most effective because:

1. It allows for:
   - Direct comparison of specific aspects
   - Balanced analysis of both systems
   - Clear presentation of similarities and differences
   - Systematic evaluation of each point

2. Structure would include:
   - Introduction to both systems
   - Analysis of key aspects (teaching methods, interaction, flexibility, etc.)
   - Direct comparisons of each aspect
   - Conclusion based on the analysis'''
            }
        ],
        'Writing Skills': [
            {
                'question': '''What is the most appropriate tone to use in a formal letter of complaint to a company?''',
                'options': [
                    'A) Angry and demanding',
                    'B) Polite but firm',
                    'C) Casual and friendly',
                    'D) Sarcastic and critical'
                ],
                'correct_answer': 'B',
                'explanation': '''From NCERT Writing Skills guidelines:

1. Formal letter tone should be:
   - Professional and respectful
   - Clear and objective
   - Assertive without being aggressive
   - Solution-oriented

2. Key elements to include:
   - Specific details of the complaint
   - Clear statement of the problem
   - Expected resolution
   - Professional closing'''
            }
        ]
    },
    'accountancy': {
        'Financial Statements': [
            {
                'question': '''Based on NCERT guidelines, which of the following items should appear in the Balance Sheet of a company under 'Current Assets'?''',
                'options': [
                    'A) Goodwill',
                    'B) Trade Receivables',
                    'C) Long-term investments',
                    'D) Share Capital'
                ],
                'correct_answer': 'B',
                'explanation': '''According to NCERT Accountancy Chapter on Balance Sheet:

1. Current Assets include:
   - Trade Receivables (Debtors)
   - Inventory
   - Cash and Bank Balances
   - Short-term investments

2. Classification criteria:
   - Expected to be realized within 12 months
   - Held primarily for trading
   - Cash or cash equivalent'''
            }
        ]
    },
    'business_studies': {
        'Financial Markets': [
            {
                'question': '''What is the primary function of the Securities and Exchange Board of India (SEBI)?''',
                'options': [
                    'A) Controlling money supply',
                    'B) Regulating stock markets',
                    'C) Setting interest rates',
                    'D) Managing foreign exchange'
                ],
                'correct_answer': 'B',
                'explanation': '''SEBI's primary function is regulating stock markets:

1. Main objectives:
   - Protect investor interests
   - Promote market development
   - Regulate securities market

2. Key functions:
   - Registration and regulation of market intermediaries
   - Prevention of unfair trade practices
   - Promotion of investor education
   - Regulation of substantial acquisition of shares

3. Powers:
   - Issue guidelines and regulations
   - Conduct investigations
   - Impose penalties for violations'''
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
    },
    'economics': {
        'International Trade': [
            {
                'question': '''In the context of Balance of Payments (BOP), which of the following items is recorded in the Capital Account?''',
                'options': [
                    'A) Export of goods',
                    'B) Foreign direct investment',
                    'C) Tourism receipts',
                    'D) Interest payments'
                ],
                'correct_answer': 'B',
                'explanation': '''Balance of Payments accounts are divided into:

1. Current Account:
   - Trade in goods and services
   - Income receipts and payments
   - Current transfers

2. Capital Account:
   - Foreign direct investment (FDI)
   - Portfolio investment
   - External borrowing/lending
   - Changes in foreign exchange reserves

Therefore, Foreign Direct Investment (FDI) is recorded in the Capital Account as it represents:
- Long-term investment flows
- Change in ownership of capital assets
- Movement of financial capital across borders'''
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

    return random.choice(topic_questions) if topic_questions else None