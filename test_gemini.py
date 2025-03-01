import os
import google.generativeai as genai
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_gemini():
    try:
        # Configure the API
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            logger.error("Google API key not found")
            return

        genai.configure(api_key=api_key)
        logger.info("Configured Gemini API")

        # List available models
        logger.info("Available models:")
        for m in genai.list_models():
            logger.info(f"- {m.name}")

        # Initialize model with the correct model name
        model = genai.GenerativeModel('gemini-pro')
        logger.info("Initialized model")

        # Test with simple prompt
        prompt = "Create a flashcard about Python programming with this format:\nFront: What is Python?\nBack: The answer"

        # Make API call
        response = await asyncio.to_thread(model.generate_content, prompt)
        logger.debug(f"Response type: {type(response)}")
        logger.debug(f"Response attributes: {dir(response)}")
        logger.debug(f"Raw response: {response.text}")

        print("\nTest Results:")
        print(f"Response text:\n{response.text}")

    except Exception as e:
        logger.error(f"Error in test: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_gemini())