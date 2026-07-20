import json
import google.generativeai as genai
from app.config import Config
from app.utils.logger import logger

def generate_lesson_content(topic: str, grade: str, language: str) -> str:
    """
    Generate lesson content using Google Generative AI.
    Constructs a structured prompt, requests JSON output, and formats it to Markdown.
    """
    logger.info(f"Generating AI content for topic='{topic}', grade='{grade}', language='{language}'")
    
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
        
    genai.configure(api_key=api_key)
    
    # Use gemini-1.5-flash which is good for fast generation and supports JSON output well
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
    
    prompt = f"""
    You are an expert educator. Create a comprehensive lesson plan for the following:
    Topic: {topic}
    Grade Level: {grade}
    Language: {language}
    
    You MUST respond entirely in {language}.
    
    Generate the response as a JSON object with the following exact keys:
    - "title": (string) Lesson title
    - "objectives": (list of strings) 3-4 learning objectives
    - "explanation": (string) A clear explanation of the core concepts
    - "activity": (string) A highly engaging classroom activity
    - "summary": (string) A brief summary of the lesson
    - "mcqs": (list of objects) Exactly 5 multiple-choice questions. Each object must have:
        - "question": (string) The question text
        - "options": (list of strings) Exactly 4 options (e.g. ["A) ...", "B) ...", "C) ...", "D) ..."])
        - "answer": (string) The correct option
    """
    
    try:
        response = model.generate_content(prompt)
        content_json = json.loads(response.text)
        return content_json
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from AI response: {e}")
        logger.error(f"Raw response: {response.text}")
        raise Exception("The AI generated an invalid response format. Please try again.")
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}", exc_info=True)
        raise Exception(f"Failed to generate content: {str(e)}")

