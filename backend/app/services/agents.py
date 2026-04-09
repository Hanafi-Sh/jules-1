import uuid
import json
from typing import List, Optional
from app.services.llm_client import generate_json, generate_text
from app.models.course import Course, Chapter, Level, Quiz, QuizQuestion, Prerequisite

# To maximize DeepSeek Cache Hits ($0.028/1M vs $0.28/1M), we must ensure exact prefix matching.
# We achieve this by placing the massive context (like the full course JSON) at the very beginning
# of the system prompt in the exact same format for all agents that need it.

def build_context_prefix(course_context_json: str) -> str:
    """Standardizes the prefix to ensure maximum DeepSeek cache hits across multiple agent calls."""
    if not course_context_json:
        return ""
    return f"--- MASTER CURRICULUM CONTEXT ---\n{course_context_json}\n---------------------------------\n\n"

class PrerequisiteAssessor:
    @staticmethod
    async def get_prerequisites(target_skill: str) -> List[Prerequisite]:
        system_prompt = "You are 'The Assessor' (Agent 0). Identify 3-6 fundamental prerequisite skills someone MUST know before they can master the target skill. Output MUST be a JSON object with a 'prerequisites' array containing 'title' and 'description'."
        user_prompt = f"Target Skill: {target_skill}"
        result_json = await generate_json(system_prompt, user_prompt)
        return [Prerequisite(id=str(uuid.uuid4()), **p) for p in result_json.get("prerequisites", [])]

class PrerequisiteReviewer:
    @staticmethod
    async def refine_prerequisites(draft_prereqs: List[Prerequisite], target_skill: str) -> List[Prerequisite]:
        system_prompt = "You are 'The Assessor Reviewer' (Agent 0.1). Review the draft prerequisites for the target skill. Output MUST be a JSON object with a 'prerequisites' array containing 'title' and 'description'."
        draft_json = json.dumps([{"title": p.title, "description": p.description} for p in draft_prereqs], indent=2)
        user_prompt = f"Target Skill: {target_skill}\nDraft Prerequisites:\n{draft_json}\n\nProvide the refined JSON."
        result_json = await generate_json(system_prompt, user_prompt)
        return [Prerequisite(id=str(uuid.uuid4()), **p) for p in result_json.get("prerequisites", [])]

class SyllabusArchitect:
    @staticmethod
    async def generate_syllabus(target_skill: str, user_context: str, known_prereqs: List[str], unknown_prereqs: List[str]) -> Course:
        system_prompt = "You are 'The Syllabus Architect' (Agent 1). Create a MECE syllabus. Skip known prerequisites. MUST include chapters to teach unknown prerequisites early on. Output MUST be a JSON object with 'title', 'target_skill', and 'chapters' (list of dicts with 'title' and 'description')."
        user_prompt = f"Target Skill: {target_skill}\nUser Context: {user_context}\nKnown Prereqs: {', '.join(known_prereqs)}\nUnknown Prereqs: {', '.join(unknown_prereqs)}"
        result_json = await generate_json(system_prompt, user_prompt)
        chapters = [Chapter(id=str(uuid.uuid4()), title=c["title"], description=c["description"], order=i+1) for i, c in enumerate(result_json.get("chapters", []))]
        return Course(id=str(uuid.uuid4()), title=result_json.get("title", f"Mastering {target_skill}"), target_skill=target_skill, chapters=chapters)

class SyllabusReviewer:
    @staticmethod
    async def refine_syllabus(draft_course: Course, user_context: str, unknown_prereqs: List[str]) -> Course:
        system_prompt = "You are 'The Syllabus Reviewer' (Agent 1.1). Review the draft syllabus for MECE compliance and prerequisites handling. Output MUST be a JSON object with 'title', 'target_skill', and 'chapters' ('title', 'description')."
        draft_json = json.dumps({"title": draft_course.title, "target_skill": draft_course.target_skill, "chapters": [{"title": c.title, "description": c.description} for c in draft_course.chapters]}, indent=2)
        user_prompt = f"User Context: {user_context}\nUnknown Prereqs: {', '.join(unknown_prereqs)}\nDraft:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)
        chapters = [Chapter(id=str(uuid.uuid4()), title=c["title"], description=c["description"], order=i+1) for i, c in enumerate(result_json.get("chapters", []))]
        return Course(id=draft_course.id, title=result_json.get("title", draft_course.title), target_skill=draft_course.target_skill, chapters=chapters)

class ChapterDesigner:
    @staticmethod
    async def design_chapter(chapter_title: str, chapter_desc: str, target_skill: str, course_context_json: str) -> List[Level]:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Chapter Designer' (Agent 2). Using the Master Curriculum Context above, break down the requested chapter into MECE 'Levels' (sub-topics). Output MUST be a JSON object with a 'levels' array containing 'title' and 'description'."
        user_prompt = f"Skill: {target_skill}\nDesign Levels for Chapter: {chapter_title}\nDescription: {chapter_desc}"
        result_json = await generate_json(system_prompt, user_prompt)
        return [Level(id=str(uuid.uuid4()), title=l["title"], description=l["description"], order=i+1) for i, l in enumerate(result_json.get("levels", []))]

class ChapterReviewer:
    @staticmethod
    async def refine_chapter(draft_levels: List[Level], chapter_title: str, chapter_desc: str, course_context_json: str) -> List[Level]:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Chapter Reviewer' (Agent 2.1). Review the draft levels for this chapter against the Master Curriculum. Ensure they are MECE and flow perfectly. Output MUST be a JSON object with a 'levels' array containing 'title' and 'description'."
        draft_json = json.dumps([{"title": l.title, "description": l.description} for l in draft_levels], indent=2)
        user_prompt = f"Review Chapter: {chapter_title} - {chapter_desc}\nDraft Levels:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)
        return [Level(id=str(uuid.uuid4()), title=l["title"], description=l["description"], order=i+1) for i, l in enumerate(result_json.get("levels", []))]

class ContentAuthor:
    @staticmethod
    async def write_content(level: Level, target_skill: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Content Author' (Agent 3). Look at the Master Curriculum Context to understand where this level fits. Write extremely comprehensive, deep, and engaging textbook content for the requested Level. Do NOT worry about UI formatting tags."
        user_prompt = f"Skill: {target_skill}\nWrite Content for Level: {level.title}\nLevel Description: {level.description}"
        return await generate_text(system_prompt, user_prompt)

class ContentReviewer:
    @staticmethod
    async def refine_content(draft_content: str, level_title: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Content Reviewer' (Agent 3.1). Read the draft textbook content. Fix hallucinations, improve analogies, and ensure it aligns with the Master Curriculum Context. Output ONLY the improved raw markdown text."
        user_prompt = f"Level Title: {level_title}\nDraft Content to Refine:\n\n{draft_content}"
        return await generate_text(system_prompt, user_prompt)

class Formatter:
    @staticmethod
    async def format_content(raw_content: str) -> str:
        system_prompt = """
        You are 'The Formatter' (Agent 4). Format the text beautifully for a frontend 'Vertical Journey'.
        CRITICAL: You must use custom React/Next.js friendly HTML/Markdown tags for special UI components:
        - For important notes or warnings, wrap them in: <InfoBox type="caution">...</InfoBox> or <InfoBox type="info">...</InfoBox>
        - For extra deep-dive explanations that can be collapsed, wrap them in: <Accordion title="Deep Dive: Topic Name">...</Accordion>
        - Ensure all code blocks use standard markdown ```language tags.
        Do not change the pedadogy, just wrap existing concepts in these beautiful UI tags where appropriate.
        """
        return await generate_text(system_prompt, f"Raw Content:\n\n{raw_content}", model="deepseek-chat")

class QuizMaster:
    @staticmethod
    async def generate_quiz(level_content: str, level_id: str, course_context_json: str) -> Quiz:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Quiz Master' (Agent 5). Generate 2-3 high-quality multiple-choice questions based on the content, keeping the Master Curriculum Context in mind. Output MUST be a JSON object with a 'questions' array ('question', 'options', 'correct_answer', 'explanation')."
        result_json = await generate_json(system_prompt, f"Content:\n{level_content}")
        questions = [QuizQuestion(**q) for q in result_json.get("questions", [])]
        return Quiz(level_id=level_id, questions=questions)

class QuizReviewer:
    @staticmethod
    async def refine_quiz(draft_quiz: Quiz, level_content: str, course_context_json: str) -> Quiz:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Quiz Reviewer' (Agent 5.1). Review the draft quiz questions against the content. Output MUST be a JSON object with a 'questions' array ('question', 'options', 'correct_answer', 'explanation')."
        draft_json = json.dumps([q.model_dump() for q in draft_quiz.questions], indent=2)
        user_prompt = f"Content:\n{level_content}\n\nDraft Quiz:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)
        questions = [QuizQuestion(**q) for q in result_json.get("questions", [])]
        return Quiz(level_id=draft_quiz.level_id, questions=questions)

class QuestionSuggester:
    @staticmethod
    async def suggest_questions(level_content: str, course_context_json: str) -> List[str]:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Curiosity Agent' (Agent 7). Identify complex technical terms in the text and generate 3-5 engaging follow-up questions for the user to ask the AI later. Output MUST be a JSON object with a 'questions' array of strings."
        result_json = await generate_json(system_prompt, f"Textbook Content:\n\n{level_content}")
        return result_json.get("questions", [])

class QuestionReviewer:
    @staticmethod
    async def refine_questions(draft_questions: List[str], level_content: str, course_context_json: str) -> List[str]:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Curiosity Reviewer' (Agent 7.1). Review the draft follow-up questions. Make them highly contextual based on the Master Curriculum. Output MUST be a JSON object with a 'questions' array of strings."
        draft_json = json.dumps({"questions": draft_questions})
        user_prompt = f"Content:\n{level_content}\n\nDraft Questions:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)
        return result_json.get("questions", [])
