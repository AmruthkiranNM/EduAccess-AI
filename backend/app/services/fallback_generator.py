import logging

logger = logging.getLogger(__name__)

def apply_fallbacks(lesson_json, topic, grade):
    """
    Ensures that every required section of the lesson JSON exists.
    If the AI truncated or omitted sections, this provides rich fallback data.
    """
    if not isinstance(lesson_json, dict):
        lesson_json = {}

    # Overview
    if 'overview' not in lesson_json:
        lesson_json['overview'] = {
            "lesson_objective": f"Understand the core concepts of {topic}.",
            "learning_outcome": f"Students will be able to explain {topic} effectively.",
            "required_materials": ["Notebook", "Pen", "Whiteboard"],
            "estimated_teaching_time": "60 minutes",
            "difficulty": "Intermediate",
            "teaching_style": "Interactive",
            "skills_developed": ["Critical Thinking", "Comprehension"],
            "curriculum_alignment": "Standard",
            "blooms_taxonomy": "Understand, Apply",
            "21st_century_skills": ["Communication", "Problem Solving"],
            "key_vocabulary": [topic, "Analysis", "Concept"],
            "student_prerequisites": ["Basic understanding of related subjects"],
            "teacher_prep_checklist": ["Review the topic", "Prepare board notes"],
            "classroom_prep": "Arrange desks for group discussion",
            "student_prep": "Bring writing materials"
        }

    # Lesson Plan
    if 'lesson_plan' not in lesson_json or not isinstance(lesson_json['lesson_plan'], list):
        lesson_json['lesson_plan'] = [{
            "subtopic_title": f"Introduction to {topic}",
            "estimated_time": "15 mins",
            "simple_explanation": f"This is an introduction to {topic}.",
            "detailed_explanation": f"{topic} is an important concept for {grade} students to master.",
            "real_life_example": f"Applying {topic} in everyday situations.",
            "fun_fact": f"{topic} has fascinating historical origins.",
            "teacher_tip": "Keep students engaged by asking questions.",
            "common_mistake": "Confusing terms.",
            "important_keywords": [topic],
            "student_question": "Why is this important?",
            "suggested_answer": "It builds a foundation for future learning.",
            "mini_recap": "We covered the basics today.",
            "quick_check_question": "What is the main idea?"
        }]

    # Timeline
    if 'timeline' not in lesson_json or not isinstance(lesson_json['timeline'], list):
        lesson_json['timeline'] = [{
            "time_range": "0-60 mins",
            "title": f"Main Lesson on {topic}",
            "teacher_script": "Let's explore this topic together.",
            "expected_student_activity": "Listening and taking notes."
        }]

    # Activities
    if 'activities' not in lesson_json or not isinstance(lesson_json['activities'], list):
        lesson_json['activities'] = [{
            "activity_name": "Group Discussion",
            "objective": f"Discuss {topic}",
            "materials": ["Paper", "Pen"],
            "preparation_time": "5 mins",
            "execution_time": "15 mins",
            "instructions": ["Form small groups", "Discuss the main points", "Present to class"],
            "teacher_script": "Work together and share your thoughts.",
            "student_instructions": "Listen to your peers.",
            "learning_outcome": "Improved collaboration.",
            "assessment": "Teacher observation.",
            "difficulty": "Easy",
            "group_size": "3-4 students",
            "variations": "Can be done individually."
        }]

    # Quiz
    if 'quiz' not in lesson_json or not isinstance(lesson_json['quiz'], list):
        lesson_json['quiz'] = [{
            "question_type": "Multiple Choice",
            "question": f"What is the most important aspect of {topic}?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "A is the best answer based on the lesson.",
            "difficulty": "Medium",
            "topic_covered": topic,
            "learning_objective": "Test comprehension",
            "marks": 1
        }]

    # Homework (8 required types)
    if 'homework' not in lesson_json or not isinstance(lesson_json['homework'], dict):
        lesson_json['homework'] = {}
        
    hw_types = ["easy", "medium", "advanced", "creative", "project", "research", "revision", "exam"]
    for hw in hw_types:
        if hw not in lesson_json['homework']:
            lesson_json['homework'][hw] = {
                "title": f"{hw.capitalize()} Task: {topic}",
                "objective": f"Reinforce learning about {topic}.",
                "estimated_time": "20 mins",
                "difficulty_badge": hw.capitalize(),
                "instructions": ["Review notes.", f"Complete the exercise on {topic}."],
                "submission_format": "Written response",
                "rubric": "Clarity and accuracy."
            }

    # Teacher Notes (30+ required types)
    if 'teacher_notes' not in lesson_json or not isinstance(lesson_json['teacher_notes'], dict):
        lesson_json['teacher_notes'] = {}
        
    tn = lesson_json['teacher_notes']
    
    # Core Teaching
    tn.setdefault('lesson_strategy', f"Use inquiry-based learning for {topic}.")
    tn.setdefault('detailed_lesson_flow', ["Introduction", "Direct Instruction", "Guided Practice", "Independent Practice", "Closure"])
    tn.setdefault('teacher_introduction_script', f"Welcome class! Today we are exploring the fascinating world of {topic}.")
    tn.setdefault('step_by_step_teaching_guide', ["Step 1: Assess prior knowledge", "Step 2: Introduce concept", "Step 3: Group activity", "Step 4: Review"])
    
    # Concepts & Discussion
    tn.setdefault('important_concepts', [f"The core mechanism of {topic}."])
    tn.setdefault('key_discussion_points', [f"How does {topic} affect our daily lives?"])
    tn.setdefault('examples_to_explain_difficult_concepts', [f"Think of {topic} like a factory assembly line."])
    tn.setdefault('real_world_connections', [f"{topic} applies to daily problem solving."])
    
    # Misconceptions & FAQ
    tn.setdefault('common_misconceptions', [{"misconception": f"Students think {topic} is simple.", "correction": "It involves complex steps."}])
    tn.setdefault('frequently_asked_questions', [{"question": f"Why learn {topic}?", "answer": "It is foundational for future learning."}])
    tn.setdefault('suggested_teacher_answers', ["Great question! Let's explore that..."])
    tn.setdefault('common_mistakes', ["Confusing the main terms."])
    tn.setdefault('how_to_correct_student_misunderstandings', ["Use visual aids and real-world analogies."])
    
    # Differentiation
    if 'differentiated_learning' not in tn or not isinstance(tn['differentiated_learning'], dict):
        tn['differentiated_learning'] = {}
    tn['differentiated_learning'].setdefault('support_for_slow_learners', ["Provide visual aids", "Repeat key terms", "Use simple language"])
    tn['differentiated_learning'].setdefault('extension_activities_for_fast_learners', ["Research related advanced topics", "Peer mentoring"])
    
    # Management & Activities
    tn.setdefault('classroom_management_tips', ["Keep transitions short.", "Use a quiet signal."])
    tn.setdefault('group_discussion_ideas', ["Divide into pairs to discuss the main concept."])
    tn.setdefault('think_pair_share_activities', ["Think about the question, pair with a neighbor, and share with the class."])
    
    # Assessment
    if 'assessment_strategy' not in tn or not isinstance(tn['assessment_strategy'], dict):
        tn['assessment_strategy'] = {}
    tn['assessment_strategy'].setdefault('observation_checklist', ["Is the student engaged?", "Can they define the concept?"])
    tn['assessment_strategy'].setdefault('formative_assessment_ideas', ["Exit tickets", "Thumbs up/down"])
    tn['assessment_strategy'].setdefault('summative_assessment_ideas', ["End of unit quiz", "Short essay"])
    
    # Bloom's Taxonomy
    if 'blooms_taxonomy_mapping' not in tn or not isinstance(tn['blooms_taxonomy_mapping'], dict):
        tn['blooms_taxonomy_mapping'] = {}
    tn['blooms_taxonomy_mapping'].setdefault('remember', f"Define {topic}.")
    tn['blooms_taxonomy_mapping'].setdefault('understand', f"Explain the process of {topic}.")
    tn['blooms_taxonomy_mapping'].setdefault('apply', f"Apply {topic} to a real-world scenario.")
    tn['blooms_taxonomy_mapping'].setdefault('analyze', f"Compare {topic} with other concepts.")
    tn['blooms_taxonomy_mapping'].setdefault('evaluate', f"Assess the importance of {topic}.")
    tn['blooms_taxonomy_mapping'].setdefault('create', f"Design a model demonstrating {topic}.")
    
    # Questions & Reflection
    tn.setdefault('questioning_strategy', ["Use open-ended questions.", "Wait 3 seconds for answers."])
    tn.setdefault('critical_thinking_questions', [f"What would happen if {topic} did not exist?"])
    tn.setdefault('reflection_questions', ["Did the students grasp the main concept?"])
    tn.setdefault('teacher_reflection_after_class', ["What worked well?", "What should be changed for next time?"])
    
    # Connections & Resources
    tn.setdefault('homework_discussion_tips', ["Review the hardest homework question first."])
    tn.setdefault('parent_involvement_suggestions', ["Send home a discussion prompt for parents."])
    tn.setdefault('cross_curricular_connections', ["Connect this topic to math or history."])
    tn.setdefault('teaching_resources', ["Online encyclopedias", "Library books"])
    tn.setdefault('digital_learning_suggestions', ["Use an interactive simulation applet."])

    # Student Resources (11 required types)
    if 'student_resources' not in lesson_json or not isinstance(lesson_json['student_resources'], dict):
        lesson_json['student_resources'] = {}
        
    sr = lesson_json['student_resources']
    sr.setdefault('quick_revision', [f"Remember the 3 main points of {topic}."])
    sr.setdefault('key_concepts', [f"Core principle of {topic}"])
    sr.setdefault('definitions', [{"term": topic, "definition": f"A key concept in {grade}."}])
    sr.setdefault('glossary', [{"term": "Concept", "definition": "An abstract idea."}])
    sr.setdefault('vocabulary', [topic, "Analysis", "Concept"])
    sr.setdefault('flashcards', [{"question": f"What is {topic}?", "answer": f"A topic for {grade}."}])
    sr.setdefault('memory_tricks', [f"Use acronyms to remember {topic} rules."])
    sr.setdefault('practice_questions', [f"Explain {topic} in your own words."])
    sr.setdefault('exam_tips', ["Read the question carefully."])
    sr.setdefault('additional_reading', [f"Check the textbook chapter on {topic}."])
    sr.setdefault('interesting_facts', [f"{topic} was discovered many years ago."])

    return lesson_json
