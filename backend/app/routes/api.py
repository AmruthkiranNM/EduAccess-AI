from flask import Blueprint, request, jsonify
from app.utils.validators import validate_generate_request
from app.services.ai_service import generate_lesson_content
from app.utils.logger import logger

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/generate', methods=['POST'])
def generate():
    """Endpoint to generate lesson plan and quiz."""
    data = request.json
    
    is_valid, error_msg = validate_generate_request(data)
    if not is_valid:
        logger.warning(f"Validation error on /generate: {error_msg}")
        return jsonify({"success": False, "error": error_msg}), 400
        
    topic = data.get('topic')
    grade = data.get('grade')
    language = data.get('language')
    
    try:
        logger.info(f"Processing generation request for topic='{topic}'")
        # Call the GenAI service (currently mocked)
        result_markdown = generate_lesson_content(topic, grade, language)
        logger.info(f"Successfully generated content for topic='{topic}'")
        return jsonify({
            "success": True,
            "data": {
                "content": result_markdown
            }
        })
    except ValueError as ve:
        # Handling missing API Key or configuration issues
        logger.error(f"Configuration error: {ve}")
        return jsonify({"success": False, "error": str(ve)}), 500
    except Exception as e:
        # Handling API call failures
        logger.error(f"Error during content generation: {e}", exc_info=True)
        return jsonify({"success": False, "error": "An internal server error occurred while generating content."}), 500
