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
    
    prompt = f"""You are an expert master teacher, instructional designer, and curriculum developer. Create a highly detailed, professional, classroom-ready lesson plan for the following:
Topic: {topic}
Subject: {subject}
Grade Level: {grade}
Language: {language}
Duration: {duration} minutes
Teaching Style: {teaching_style}
Difficulty: {difficulty}

You MUST respond entirely in {language}.
You MUST adapt the depth and number of activities strictly to the {duration}-minute time constraint.
You MUST respond with ONLY a valid JSON object — no markdown outside of string values, no extra text, no code fences wrapping the JSON.

The JSON object MUST follow this EXACT structure and keys (do not miss any keys):
{{
  "overview": {{
    "lesson_objective": (string),
    "learning_outcome": (string),
    "required_materials": [(array of strings)],
    "estimated_teaching_time": "{duration} minutes",
    "difficulty": "{difficulty}",
    "teaching_style": "{teaching_style}",
    "skills_developed": [(array of strings)],
    "curriculum_alignment": (string),
    "blooms_taxonomy": (string),
    "21st_century_skills": [(array of strings)],
    "key_vocabulary": [(array of strings)],
    "student_prerequisites": [(array of strings)],
    "teacher_prep_checklist": [(array of strings)],
    "classroom_prep": (string),
    "student_prep": (string)
  }},
  "lesson_plan": [
    {{
      "subtopic_title": (string),
      "estimated_time": (string),
      "simple_explanation": (string),
      "detailed_explanation": (string),
      "real_life_example": (string),
      "fun_fact": (string),
      "teacher_tip": (string),
      "common_mistake": (string),
      "important_keywords": [(array of strings)],
      "student_question": (string),
      "suggested_answer": (string),
      "mini_recap": (string),
      "quick_check_question": (string)
    }}
  ],
  "visualizations": [
    // Provide 3 to 6 relevant visual resources
    {{
      "title": (string) "Title of the educational image or diagram",
      "wikimedia_search_query": (string) "Highly specific search query for Wikimedia Commons (e.g. 'human heart diagram SVG' or 'photosynthesis labeled english')",
      "what_it_shows": (string) "Description of the image content",
      "important_labels": (string) "Key labels to point out to students",
      "teacher_explanation": (string) "How the teacher should explain this diagram",
      "key_observations": (string) "What students should notice",
      "discussion_questions": (string) "Questions to engage the class about this image"
    }}
  ],
  "timeline": [
    {{
      "time_range": (string) e.g., '0-10 minutes',
      "title": (string),
      "teacher_script": (string),
      "expected_student_activity": (string)
    }}
    // IMPORTANT: Generate 4 to 8 of these objects to cover the entire lesson duration.
  ],
  "activities": [
    {{
      "activity_name": (string),
      "objective": (string),
      "materials": [(array of strings)],
      "preparation_time": (string),
      "execution_time": (string),
      "instructions": [(array of strings)],
      "teacher_script": (string),
      "student_instructions": (string),
      "learning_outcome": (string),
      "assessment": (string),
      "difficulty": (string),
      "group_size": (string),
      "variations": (string)
    }}
  ],
  "quiz": [
    {{
      "question_type": (string) 'Multiple Choice' | 'True or False' | 'Fill in the Blank' | 'Match the Following' | 'Short Answer' | 'Long Answer' | 'HOTS' | 'Case Study',
      "question": (string),
      "options": [(array of strings) Required for MCQ and Match. Leave empty for others],
      "correct_answer": (string),
      "explanation": (string),
      "difficulty": (string),
      "topic_covered": (string),
      "learning_objective": (string),
      "marks": (number)
    }}
  ],
  "homework": {{
    "easy": {{ "task": (string), "time": (string), "outcome": (string) }},
    "medium": {{ "task": (string), "time": (string), "outcome": (string) }},
    "advanced": {{ "task": (string), "time": (string), "outcome": (string) }},
    "creative": {{ "task": (string), "time": (string), "outcome": (string) }},
    "project": {{ "task": (string), "time": (string), "outcome": (string) }},
    "research": {{ "task": (string), "time": (string), "outcome": (string) }},
    "parent_activity": {{ "task": (string), "time": (string), "outcome": (string) }},
    "revision_questions": [(array of strings)],
    "exam_questions": [(array of strings)]
  }},
  "teacher_notes": {{
    "teaching_strategy": (string),
    "teaching_sequence": (string),
    "important_concepts": (string),
    "common_misconceptions": (string),
    "frequently_asked_questions": [ {{ "question": (string), "answer": (string) }} ],
    "classroom_management": (string),
    "assessment_strategy": (string),
    "differentiated_learning": (string),
    "support_slow_learners": (string),
    "extension_advanced": (string),
    "cross_curricular": (string),
    "real_world": (string),
    "exam_tips": (string),
    "revision_tips": (string)
  }},
  "student_resources": {{
    "key_points": [(array of strings)],
    "quick_revision_sheet": (string),
    "glossary": [ {{ "term": (string), "definition": (string) }} ],
    "vocabulary": [(array of strings)],
    "formula_sheet": [(array of strings) if applicable],
    "important_dates": [(array of strings) if applicable],
    "mnemonics": [(array of strings)],
    "memory_tricks": [(array of strings)],
    "common_mistakes": [(array of strings)],
    "exam_prep_guide": (string)
  }}
}}

Ensure every field is populated with high-quality, professional educational content. Generate exactly 10 multiple choice, 5 true/false, 5 fill-in-blanks, 5 match, 5 short answer, 2 long answer, 3 HOTS, and 2 case study questions for the quiz array (Total 37 questions). Generate at least 5 activities. Respond ONLY with the JSON object.
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
                max_tokens=7500,
                response_format={"type": "json_object"}
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
