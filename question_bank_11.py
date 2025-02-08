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
            },
            {
                'question': '''According to NCERT, which of the following is NOT a characteristic of a 'Journal'?''',
                'options': [
                    'A) Chronological record of transactions',
                    'B) Original book of entry',
                    'C) Recording final trial balance',
                    'D) Complete information about transactions'
                ],
                'correct_answer': 'C',
                'explanation': '''From NCERT Accountancy Chapter 1:
1. Characteristics of Journal:
   - Chronological record
   - Original/primary book of entry
   - Complete information of transactions
2. Trial Balance:
   - Prepared after posting to ledger
   - Not part of journalizing
   - Separate statement altogether'''
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
        'Grammar and Language Skills': [
            {
                'question': '''Identify the type of clause in the following sentence:
"The book that I borrowed from the library belongs to my friend."''',
                'options': [
                    'A) Noun Clause',
                    'B) Adverbial Clause',
                    'C) Relative Clause',
                    'D) Main Clause'
                ],
                'correct_answer': 'C',
                'explanation': '''From NCERT English Grammar:
1. A Relative Clause (also called Adjective Clause):
   - Modifies a noun or pronoun
   - Begins with relative pronouns (who, whom, whose, which, that)
   - "that I borrowed from the library" modifies "book"
   - Functions as an adjective in the sentence
   - Cannot stand alone as a complete sentence'''
            },
            {
                'question': '''Choose the correct form of the verb in the following sentence:
"Neither of the students _____ completed the assignment."''',
                'options': [
                    'A) have',
                    'B) has',
                    'C) having',
                    'D) had been'
                ],
                'correct_answer': 'B',
                'explanation': '''Based on NCERT Subject-Verb Agreement rules:
1. When 'neither of' is used:
   - It refers to two things
   - Takes a singular verb
   - Therefore, 'has' is correct
2. Remember: 'Neither' is singular
   - Always followed by singular verb
   - Even when followed by plural noun'''
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
            },
            {
                'question': '''Which of the following is NOT an essential component of a formal letter?''',
                'options': [
                    'A) Sender\'s address',
                    'B) Personal anecdotes',
                    'C) Subject line',
                    'D) Date'
                ],
                'correct_answer': 'B',
                'explanation': '''From NCERT Writing Skills section:
1. Essential components of a formal letter:
   - Sender's address
   - Date
   - Receiver's address
   - Subject line
   - Salutation
   - Body
   - Complimentary close
2. Personal anecdotes:
   - Not appropriate for formal letters
   - Should be avoided
   - Makes the letter informal'''
            }
        ],
        'Hornbill - Prose': [
            {
                'question': '''Read the following extract from "The Portrait of a Lady" and answer the question:

"She hobbled around the house in spotless white with one hand resting on her waist to balance her stoop and the other telling the beads of her rosary. Her silver locks were scattered untidily over her pale, puckered face, and her lips constantly moved in inaudible prayer."

What does this description reveal about the grandmother's character?''',
                'options': [
                    'A) Her vanity and self-consciousness',
                    'B) Her religious nature and physical frailty',
                    'C) Her disorganized and careless nature',
                    'D) Her modern and progressive outlook'
                ],
                'correct_answer': 'B',
                'explanation': '''The passage reveals the grandmother's character through:
1. Physical description:
   - "hobbled" suggests age and physical limitation
   - "stoop" indicates her aged posture
   - "silver locks" describes her grey hair

2. Spiritual nature:
   - "telling the beads of her rosary"
   - "lips constantly moved in inaudible prayer"
   - "spotless white" suggesting purity and devotion

3. Overall image:
   - Shows her as a traditional, religious, elderly woman
   - Despite physical frailty, maintains spiritual dedication
   - Presents a dignified yet humble character'''
            },
            {
                'question': '''From the chapter "We're Not Afraid to Die... if We Can All Be Together", what was the narrator's first action when the wave hit the boat?''',
                'options': [
                    'A) He called for help on the radio',
                    'B) He checked on his children',
                    'C) He went to start the engine',
                    'D) He assessed the damage to the boat'
                ],
                'correct_answer': 'B',
                'explanation': '''The correct sequence of events was:
1. After the wave hit:
   - Narrator's first concern was his children's safety
   - He immediately went to check on Jon and Sue
   - This shows his priorities as a father

2. Why this was significant:
   - Demonstrates the theme of family unity
   - Shows how crisis reveals priorities
   - Reinforces the chapter's title theme'''
            },
            {
                'question': '''In "Discovering Tut", what was Howard Carter's initial reaction upon finding the tomb?''',
                'options': [
                    'A) He immediately began excavating the tomb.',
                    'B) He felt a sense of overwhelming joy and excitement.',
                    'C) He cautiously peered into the tomb and noticed some small details.',
                    'D) He called for his team and celebrated the discovery.'
                ],
                'correct_answer': 'C',
                'explanation': 'The text describes Carter\'s initial reaction as cautious observation, highlighting his meticulous approach to the discovery.'
            }
        ],
        'Hornbill - Poetry': [
            {
                'question': '''In the poem "A Photograph" by Shirley Toulson, what does the phrase "laboured ease" suggest about the girls' poses?''',
                'options': [
                    'A) They were completely natural',
                    'B) They were trying to look casual but were actually conscious',
                    'C) They were uncomfortable being photographed',
                    'D) They were experienced models'
                ],
                'correct_answer': 'B',
                'explanation': '''The phrase "laboured ease" is an oxymoron that suggests:
1. The girls were:
   - Trying to appear natural and at ease
   - Actually quite conscious of being photographed
   - Making an effort to look casual

2. This detail is significant because:
   - It captures a universal human moment
   - Shows the artifice involved in photography
   - Adds to the nostalgic tone of the poem'''
            },
            {
                'question': '''What is the central theme of the poem "Voice of the Rain" by Walt Whitman?''',
                'options': [
                    'A) The destructive power of nature',
                    'B) The cyclical nature of life and death',
                    'C) The beauty of a summer storm',
                    'D) The insignificance of human life'
                ],
                'correct_answer': 'B',
                'explanation': 'The poem uses the imagery of rain to represent the continuous cycle of life, death, and rebirth.'
            }
        ],
        'Snapshots': [
            {
                'question': '''In "The Summer of the Beautiful White Horse" by William Saroyan, why does Aram find it hard to believe that his cousin Mourad has stolen a horse?''',
                'options': [
                    'A) Because Mourad was too young to steal',
                    'B) Because stealing was against their tribe\'s reputation for honesty',
                    'C) Because Mourad didn\'t know how to ride horses',
                    'D) Because the horse belonged to a family friend'
                ],
                'correct_answer': 'B',
                'explanation': '''The answer reflects the story\'s central conflict:
1. Tribal identity:
   - The Garoghlanian tribe was famous for honesty
   - They were poor but never stole
   - Their reputation was their pride

2. Personal conflict:
   - Aram struggles between tribal values and temptation
   - The beautiful horse represents desire vs. integrity
   - Shows the complexity of moral choices'''
            },
            {
                'question': '''What is the central theme of the short story "The Address"?''',
                'options': [
                    'A) The lasting impact of war and displacement',
                    'B) The importance of family bonds',
                    'C) The struggle for social justice',
                    'D) The search for personal identity'
                ],
                'correct_answer': 'A',
                'explanation': 'The story explores the lingering effects of war and the complex emotions it leaves behind, focusing on how experiences and memories shape the present.'
            },
            {
                'question': '''In "Ranga's Marriage," what role does the character of Shastri play in the story?''',
                'options': [
                    'A) He is a wealthy landowner who helps Ranga find a bride.',
                    'B) He is a close friend of Ranga who advises him on marriage.',
                    'C) He is a wise and respected elder who arranges Ranga\'s marriage.',
                    'D) He is a rival of Ranga who tries to prevent his marriage.'
                ],
                'correct_answer': 'C',
                'explanation': 'Shastri acts as the mediator and facilitator, leveraging his influence and wisdom to orchestrate the marriage successfully.'
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