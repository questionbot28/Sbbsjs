import asyncio
import logging
from question_generator import QuestionGenerator
import json

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_question_generation():
    """Test the question generation functionality"""
    try:
        # Initialize the question generator
        generator = QuestionGenerator()
        
        # Test cases
        test_cases = [
            ("physics", "Mechanics", 11),
            ("mathematics", None, 11),
            ("chemistry", "Thermodynamics", 12),
            ("biology", None, 12)
        ]
        
        for subject, topic, class_level in test_cases:
            logger.info(f"\nTesting question generation for {subject}, topic: {topic}, class: {class_level}")
            
            try:
                # Generate question
                question = await generator.generate_question(
                    subject=subject,
                    topic=topic,
                    class_level=class_level,
                    user_id="test_user"
                )
                
                if question:
                    logger.info("Question generated successfully:")
                    logger.info(json.dumps(question, indent=2))
                    
                    # Validate response structure
                    required_fields = ['question', 'options', 'correct_answer']
                    missing_fields = [field for field in required_fields if field not in question]
                    
                    if missing_fields:
                        logger.error(f"Missing required fields: {missing_fields}")
                    else:
                        logger.info("Response structure is valid")
                else:
                    logger.error("Failed to generate question")
                    
            except Exception as e:
                logger.error(f"Error testing {subject}: {str(e)}")
                
            await asyncio.sleep(1)  # Prevent rate limiting
            
    except Exception as e:
        logger.error(f"Test suite error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_question_generation())
