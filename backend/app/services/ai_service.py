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
      "caption": (string) "A short caption for the image",
      "short_explanation": (string) "A short explanation of what this image teaches",
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
      "question_type": (string),
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
    "easy": {{ "title": (string), "objective": (string), "estimated_time": (string), "difficulty_badge": (string), "instructions": [(array of strings)], "submission_format": (string), "rubric": (string) }},
    "medium": {{ "title": (string), "objective": (string), "estimated_time": (string), "difficulty_badge": (string), "instructions": [(array of strings)], "submission_format": (string), "rubric": (string) }},
    "advanced": {{ "title": (string), "objective": (string), "estimated_time": (string), "difficulty_badge": (string), "instructions": [(array of strings)], "submission_format": (string), "rubric": (string) }},
    "creative": {{ "title": (string), "objective": (string), "estimated_time": (string), "difficulty_badge": (string), "instructions": [(array of strings)], "submission_format": (string), "rubric": (string) }},
    "project": {{ "title": (string), "objective": (string), "estimated_time": (string), "difficulty_badge": (string), "instructions": [(array of strings)], "submission_format": (string), "rubric": (string) }},
    "research": {{ "title": (string), "objective": (string), "estimated_time": (string), "difficulty_badge": (string), "instructions": [(array of strings)], "submission_format": (string), "rubric": (string) }},
    "revision": {{ "title": (string), "objective": (string), "estimated_time": (string), "difficulty_badge": (string), "instructions": [(array of strings)], "submission_format": (string), "rubric": (string) }},
    "exam": {{ "title": (string), "objective": (string), "estimated_time": (string), "difficulty_badge": (string), "instructions": [(array of strings)], "submission_format": (string), "rubric": (string) }}
  }},
  "teacher_notes": {{
    "lesson_strategy": (string),
    "detailed_lesson_flow": [(array of strings)],
    "teacher_introduction_script": (string),
    "step_by_step_teaching_guide": [(array of strings)],
    "important_concepts": [(array of strings)],
    "key_discussion_points": [(array of strings)],
    "examples_to_explain_difficult_concepts": [(array of strings)],
    "real_world_connections": [(array of strings)],
    "common_misconceptions": [ {{ "misconception": (string), "correction": (string) }} ],
    "frequently_asked_questions": [ {{ "question": (string), "answer": (string) }} ],
    "suggested_teacher_answers": [(array of strings)],
    "common_mistakes": [(array of strings)],
    "how_to_correct_student_misunderstandings": [(array of strings)],
    "differentiated_learning": {{
      "support_for_slow_learners": [(array of strings)],
      "extension_activities_for_fast_learners": [(array of strings)]
    }},
    "classroom_management_tips": [(array of strings)],
    "group_discussion_ideas": [(array of strings)],
    "think_pair_share_activities": [(array of strings)],
    "assessment_strategy": {{
      "observation_checklist": [(array of strings)],
      "formative_assessment_ideas": [(array of strings)],
      "summative_assessment_ideas": [(array of strings)]
    }},
    "blooms_taxonomy_mapping": {{
      "remember": (string),
      "understand": (string),
      "apply": (string),
      "analyze": (string),
      "evaluate": (string),
      "create": (string)
    }},
    "questioning_strategy": [(array of strings)],
    "critical_thinking_questions": [(array of strings)],
    "reflection_questions": [(array of strings)],
    "teacher_reflection_after_class": [(array of strings)],
    "homework_discussion_tips": [(array of strings)],
    "parent_involvement_suggestions": [(array of strings)],
    "cross_curricular_connections": [(array of strings)],
    "teaching_resources": [(array of strings)],
    "digital_learning_suggestions": [(array of strings)]
  }},
  "student_resources": {{
    "quick_revision": [(array of strings)],
    "key_concepts": [(array of strings)],
    "definitions": [ {{ "term": (string), "definition": (string) }} ],
    "glossary": [ {{ "term": (string), "definition": (string) }} ],
    "vocabulary": [(array of strings)],
    "flashcards": [ {{ "question": (string), "answer": (string) }} ],
    "memory_tricks": [(array of strings)],
    "practice_questions": [(array of strings)],
    "exam_tips": [(array of strings)],
    "additional_reading": [(array of strings)],
    "interesting_facts": [(array of strings)]
  }}
}}

Ensure every field is populated with high-quality, professional educational content. Generate exactly 3 multiple choice, 2 true/false, and 2 HOTS questions for the quiz array. Generate exactly 3 activities. Respond ONLY with the JSON object.
"""

    models_to_try = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama-3.2-3b-preview"
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
                max_tokens=3500,
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
    except Exception as e:
        logger.warning(f"Failed to parse JSON from AI response: {e}. Falling back to robust generation.")
        content_json = {}
        
    try:
        from app.services.fallback_generator import apply_fallbacks
        content_json = apply_fallbacks(content_json, topic, grade)
    except Exception as e:
        logger.error(f"Fallback generation failed: {e}")
        
    try:
        from app.services.image_service import fetch_educational_images
        content_json['visualizations'] = fetch_educational_images(topic)
    except Exception as e:
        logger.error(f"Image fetching failed: {e}")
        content_json['visualizations'] = []
        
    return content_json
