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


def generate_lesson_content(topic: str, grade: str, language: str, subject: str = "General", duration: str = "60", teaching_style: str = "Interactive", difficulty: str = "Intermediate") -> dict:
    """
    Generate complex teaching assistant content using the Groq API.
    """
    logger.info(f"Generating AI content for topic='{topic}', subject='{subject}', grade='{grade}', duration='{duration}m'")
    
    api_key = Config.GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment variables.")
        
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        raise Exception("Failed to initialize AI client. Check configuration.")
    
    prompt = f"""You are an expert master teacher and curriculum designer. Create a highly detailed, professional lesson plan for the following:
Topic: {topic}
Subject: {subject}
Grade Level: {grade}
Language: {language}
Duration: {duration} minutes
Teaching Style: {teaching_style}
Difficulty: {difficulty}

You MUST respond entirely in {language}.
You MUST adapt the depth and number of activities strictly to the {duration}-minute time constraint.
You MUST respond with ONLY a valid JSON object — no markdown, no extra text, no code fences.

The JSON object MUST follow this EXACT structure and keys:
{{
  "metadata": {{
    "duration": "{duration} minutes",
    "difficulty": "{difficulty}",
    "grade": "{grade}",
    "language": "{language}",
    "activities_count": (integer) total number of activities,
    "reading_time": (string) estimated reading time for the teacher,
    "topic": "{topic}",
    "subject": "{subject}"
  }},
  "learning_outcomes": [
    "Explain...", "Identify...", "Solve..." (3-5 bullet points)
  ],
  "timeline": [
    {{
      "time": "0-5 min",
      "title": "Introduction",
      "description": "Brief description of what happens."
    }}
    // Add items to fill exactly {duration} minutes.
  ],
  "topic_map": (string) "A text-based tree representing the hierarchy of concepts. Use ├── and └──.",
  "sections": [
    {{
      "title": (string) Section Title (e.g. 'Introduction', 'Main Concept 1', 'Activity'),
      "estimated_time": (string) e.g. "10 min",
      "teacher_notes": (string) Tips for the teacher,
      "content": (string) The actual detailed content, explanation, or examples. Use markdown formatting inside the string (e.g. **bold**, bullet points).
    }}
    // Add as many sections as needed based on duration.
  ],
  "student_engagement": [
    {{
      "type": (string) e.g. "Think-Pair-Share", "Discussion Question", "Class Poll", "Group Activity",
      "prompt": (string) The question or activity prompt
    }}
  ],
  "quiz": [
    {{
      "question": (string) Multiple choice question,
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": (string) The correct option
    }}
    // Exactly 5 questions
  ],
  "homework": (string) Homework assignment description,
  "teacher_tips": (string) General tips for delivering this specific lesson,
  "common_misconceptions": (string) Things students usually get wrong and how to correct them
}}

Respond with the JSON object only. Do not wrap it in code fences. Do not output anything else.
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
