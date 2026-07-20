import json
import re
from groq import Groq, APIError, APIConnectionError, RateLimitError
from app.config import Config
from app.utils.logger import logger

def _extract_json(text: str) -> str:
    """
    Robustly extract JSON from a model response that may be wrapped
    in markdown code fences (```json ... ```) or returned as raw JSON.
    """
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()


def generate_lesson_content(topic: str, grade: str, language: str) -> dict:
    """
    Generate lesson content using the Groq API.
    Uses prompt engineering to request JSON output and parses the result robustly.
    Falls back to a smaller model if the primary one fails.
    """
    logger.info(f"Generating AI content for topic='{topic}', grade='{grade}', language='{language}'")
    
    api_key = Config.GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment variables.")
        
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        raise Exception("Failed to initialize AI client. Check configuration.")
    
    prompt = f"""You are an expert educator. Create a comprehensive lesson plan for the following:
Topic: {topic}
Grade Level: {grade}
Language: {language}

You MUST respond entirely in {language}.
You MUST respond with ONLY a valid JSON object — no markdown, no extra text, no code fences.

The JSON object must have exactly these keys:
- "title": (string) Lesson title
- "objectives": (array of strings) 3-4 clear learning objectives
- "explanation": (string) A clear explanation of the core concepts (2-3 paragraphs)
- "activity": (string) A highly engaging classroom activity description
- "summary": (string) A brief summary of the lesson
- "mcqs": (array of objects) Exactly 5 multiple-choice questions. Each object must have:
    - "question": (string) The question text
    - "options": (array of 4 strings) e.g. ["A) Option one", "B) Option two", "C) Option three", "D) Option four"]
    - "answer": (string) The correct option letter and text, e.g. "A) Option one"

Respond with the JSON object only. Do not wrap it in code fences.
"""

    models_to_try = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
    
    last_error = None
    raw_text = None

    for model_name in models_to_try:
        try:
            logger.info(f"Attempting to use Groq model: {model_name}")
            response = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=model_name,
                temperature=0.7,
                # Optionally specify response format if supported by the model,
                # but relying on prompt engineering for safety across fallbacks.
            )
            raw_text = response.choices[0].message.content
            logger.info("Successfully received response from Groq API.")
            break
            
        except RateLimitError as e:
            logger.warning(f"Rate limit exceeded for model {model_name}: {e}")
            last_error = "Rate limit exceeded. Please try again later."
        except APIConnectionError as e:
            logger.warning(f"Connection error when calling model {model_name}: {e}")
            last_error = "Network error connecting to AI provider."
        except APIError as e:
            logger.warning(f"API error for model {model_name}: {e}")
            last_error = f"AI API error: {e.message}"
        except Exception as e:
            logger.warning(f"Unexpected error with model {model_name}: {e}")
            last_error = "An unexpected error occurred during generation."

    if not raw_text:
        logger.error("All Groq model attempts failed.")
        raise Exception(last_error or "Failed to generate content due to an unknown API error.")
        
    try:
        cleaned = _extract_json(raw_text)
        if not cleaned:
             raise ValueError("Empty response after JSON extraction.")
             
        content_json = json.loads(cleaned)
        return content_json
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from AI response: {e}")
        logger.error(f"Raw response: {raw_text[:500]}")
        raise Exception("The AI returned an unexpected format. Please try again.")
    except Exception as e:
        logger.error(f"Error extracting JSON: {e}", exc_info=True)
        raise Exception(f"Failed to parse content: {str(e)}")
