def validate_generate_request(data):
    """
    Validate the input data for the generate request.
    Expected to have 'topic', 'grade', and 'language'.
    """
    if not data:
        return False, "Invalid request. JSON body required."
        
    topic = data.get('topic')
    grade = data.get('grade')
    language = data.get('language')
    
    if not topic or not grade or not language:
        return False, "Missing required fields: topic, grade, language"
        
    if not isinstance(topic, str) or not str(topic).strip():
        return False, "Topic must be a non-empty string"
        
    return True, None
