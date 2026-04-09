import uuid
import json
from typing import List
from app.services.llm_client import generate_json, generate_text
from app.models.course import Course, Chapter, Level, Quiz, QuizQuestion, Prerequisite

class PrerequisiteAssessor:
    """Agent 0: Assesses what fundamental skills are needed before learning the target skill"""
    @staticmethod
    async def get_prerequisites(target_skill: str) -> List[Prerequisite]:
        system_prompt = """
        You are 'The Assessor' (Agent 0). Your job is to identify the fundamental prerequisite skills someone MUST know before they can master the target skill.
        Break it down into 3-6 distinct prerequisites.
        Output MUST be a JSON object with a 'prerequisites' array.
        Each prerequisite dict should have 'title' (str) and 'description' (str) explaining why it is needed.
        """
        user_prompt = f"Target Skill: {target_skill}"

        result_json = await generate_json(system_prompt, user_prompt)

        prereqs = []
        for p_data in result_json.get("prerequisites", []):
            prereqs.append(Prerequisite(
                id=str(uuid.uuid4()),
                title=p_data["title"],
                description=p_data["description"]
            ))
        return prereqs

class PrerequisiteReviewer:
    """Agent 0.1: Reviews and refines the prerequisites"""
    @staticmethod
    async def refine_prerequisites(draft_prereqs: List[Prerequisite], target_skill: str) -> List[Prerequisite]:
        system_prompt = """
        You are 'The Assessor Reviewer' (Agent 0.1). Review the draft prerequisites for the target skill.
        Are they truly foundational? Are any crucial basics missing? Are any redundant?
        Improve them to be the perfect starting checklist.
        Output MUST be a JSON object with a 'prerequisites' array containing 'title' and 'description'.
        """
        draft_json = json.dumps([{"title": p.title, "description": p.description} for p in draft_prereqs], indent=2)
        user_prompt = f"Target Skill: {target_skill}\nDraft Prerequisites:\n{draft_json}\n\nProvide the refined JSON."

        result_json = await generate_json(system_prompt, user_prompt)

        prereqs = []
        for p_data in result_json.get("prerequisites", []):
            prereqs.append(Prerequisite(
                id=str(uuid.uuid4()),
                title=p_data["title"],
                description=p_data["description"]
            ))
        return prereqs

class SyllabusArchitect:
    """Agent 1: Generates the high-level chapters based on user prompt and prerequisites"""
    @staticmethod
    async def generate_syllabus(target_skill: str, user_context: str, known_prereqs: List[str], unknown_prereqs: List[str]) -> Course:
        system_prompt = """
        You are 'The Syllabus Architect' (Agent 1). Create a MECE syllabus for learning a specific skill up to an ADVANCED level.
        CRITICAL: Skip known prerequisites. MUST include chapters to teach unknown prerequisites early on.
        Output MUST be a JSON object with 'title' (str), 'target_skill' (str), and 'chapters' (list of dicts with 'title' and 'description').
        """
        user_prompt = f"Target Skill: {target_skill}\nUser Context: {user_context}\n"
        user_prompt += f"Known Prereqs: {', '.join(known_prereqs) if known_prereqs else 'None'}\n"
        user_prompt += f"Unknown Prereqs to teach: {', '.join(unknown_prereqs) if unknown_prereqs else 'None'}\n"

        result_json = await generate_json(system_prompt, user_prompt)

        chapters = []
        for i, ch_data in enumerate(result_json.get("chapters", [])):
            chapters.append(Chapter(
                id=str(uuid.uuid4()),
                title=ch_data["title"],
                description=ch_data["description"],
                order=i + 1
            ))

        return Course(
            id=str(uuid.uuid4()),
            title=result_json.get("title", f"Mastering {target_skill}"),
            target_skill=target_skill,
            chapters=chapters
        )

class SyllabusReviewer:
    """Agent 1.1: Critiques and refines the draft syllabus (formerly Agent 6)"""
    @staticmethod
    async def refine_syllabus(draft_course: Course, user_context: str, unknown_prereqs: List[str]) -> Course:
        system_prompt = """
        You are 'The Syllabus Reviewer' (Agent 1.1). Review the draft syllabus.
        Is it perfectly MECE? Are unknown prerequisites adequately covered at the start? Does it reach an advanced level?
        Output MUST be a JSON object with 'title' (str), 'target_skill' (str), and 'chapters' (list of dicts with 'title' and 'description').
        """
        draft_json = json.dumps({"title": draft_course.title, "target_skill": draft_course.target_skill, "chapters": [{"title": c.title, "description": c.description} for c in draft_course.chapters]}, indent=2)
        user_prompt = f"User Context: {user_context}\nUnknown Prereqs: {', '.join(unknown_prereqs)}\nDraft:\n{draft_json}"

        result_json = await generate_json(system_prompt, user_prompt)

        chapters = []
        for i, ch_data in enumerate(result_json.get("chapters", [])):
            chapters.append(Chapter(
                id=str(uuid.uuid4()),
                title=ch_data["title"],
                description=ch_data["description"],
                order=i + 1
            ))
        return Course(id=draft_course.id, title=result_json.get("title", draft_course.title), target_skill=draft_course.target_skill, chapters=chapters)

class ChapterDesigner:
    """Agent 2: Breaks down a chapter into specific Levels"""
    @staticmethod
    async def design_chapter(chapter_title: str, chapter_desc: str, target_skill: str) -> List[Level]:
        system_prompt = """
        You are 'The Chapter Designer' (Agent 2). Break down the chapter into MECE 'Levels' (sub-topics) progressing from fundamental to specific.
        Output MUST be a JSON object with a 'levels' array containing 'title' and 'description'.
        """
        user_prompt = f"Skill: {target_skill}\nChapter: {chapter_title}\nDescription: {chapter_desc}"

        result_json = await generate_json(system_prompt, user_prompt)

        levels = []
        for i, lvl_data in enumerate(result_json.get("levels", [])):
            levels.append(Level(id=str(uuid.uuid4()), title=lvl_data["title"], description=lvl_data["description"], order=i + 1))
        return levels

class ChapterReviewer:
    """Agent 2.1: Reviews the levels in a chapter"""
    @staticmethod
    async def refine_chapter(draft_levels: List[Level], chapter_title: str, chapter_desc: str) -> List[Level]:
        system_prompt = """
        You are 'The Chapter Reviewer' (Agent 2.1). Review the sub-topic levels for this chapter.
        Are they truly MECE? Is the progression logical without overlaps? Add, remove, or refine levels as needed.
        Output MUST be a JSON object with a 'levels' array containing 'title' and 'description'.
        """
        draft_json = json.dumps([{"title": l.title, "description": l.description} for l in draft_levels], indent=2)
        user_prompt = f"Chapter: {chapter_title} - {chapter_desc}\nDraft Levels:\n{draft_json}"

        result_json = await generate_json(system_prompt, user_prompt)
        levels = []
        for i, lvl_data in enumerate(result_json.get("levels", [])):
            levels.append(Level(id=str(uuid.uuid4()), title=lvl_data["title"], description=lvl_data["description"], order=i + 1))
        return levels

class ContentAuthor:
    """Agent 3: Writes the comprehensive content for a Level"""
    @staticmethod
    async def write_content(level: Level, target_skill: str) -> str:
        system_prompt = """
        You are 'The Content Author' (Agent 3). Write comprehensive, deep, and engaging textbook content for this Level.
        Use deep reasoning to explain complex topics. DO NOT worry about formatting UI elements yet.
        """
        user_prompt = f"Skill: {target_skill}\nLevel Title: {level.title}\nLevel Description: {level.description}"
        return await generate_text(system_prompt, user_prompt)

class ContentReviewer:
    """Agent 3.1: Reviews and refines textbook content"""
    @staticmethod
    async def refine_content(draft_content: str, level_title: str) -> str:
        system_prompt = """
        You are 'The Content Reviewer' (Agent 3.1). Read the draft textbook content.
        Your job is to identify and fix hallucinations, improve analogies, ensure pedagogical clarity, and deepen the explanation if it's too shallow.
        Output ONLY the improved raw markdown text. No pleasantries.
        """
        user_prompt = f"Level Title: {level_title}\nDraft Content:\n\n{draft_content}"
        return await generate_text(system_prompt, user_prompt)

class Formatter:
    """Agent 4: Formats the content into UI-ready markdown (No reviewer needed)"""
    @staticmethod
    async def format_content(raw_content: str) -> str:
        system_prompt = """
        You are 'The Formatter' (Agent 4). Format the text beautifully for a UI 'Vertical Journey'.
        Add ':::caution' or ':::info' blocks. Break up long paragraphs. Output raw markdown.
        """
        return await generate_text(system_prompt, f"Raw Content:\n\n{raw_content}", model="deepseek-chat")

class QuizMaster:
    """Agent 5: Generates validation questions"""
    @staticmethod
    async def generate_quiz(level_content: str, level_id: str) -> Quiz:
        system_prompt = """
        You are 'The Quiz Master' (Agent 5). Generate 2-3 high-quality multiple-choice questions based on the content.
        Output MUST be a JSON object with a 'questions' array ('question', 'options', 'correct_answer', 'explanation').
        """
        result_json = await generate_json(system_prompt, f"Content:\n{level_content}")
        questions = [QuizQuestion(**q) for q in result_json.get("questions", [])]
        return Quiz(level_id=level_id, questions=questions)

class QuizReviewer:
    """Agent 5.1: Reviews the validation questions"""
    @staticmethod
    async def refine_quiz(draft_quiz: Quiz, level_content: str) -> Quiz:
        system_prompt = """
        You are 'The Quiz Reviewer' (Agent 5.1). Review the draft quiz questions against the content.
        Ensure the correct answer is factually accurate, options are unambiguous, and explanations are clear.
        Output MUST be a JSON object with a 'questions' array ('question', 'options', 'correct_answer', 'explanation').
        """
        draft_json = json.dumps([q.model_dump() for q in draft_quiz.questions], indent=2)
        user_prompt = f"Content:\n{level_content}\n\nDraft Quiz:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)
        questions = [QuizQuestion(**q) for q in result_json.get("questions", [])]
        return Quiz(level_id=draft_quiz.level_id, questions=questions)

class QuestionSuggester:
    """Agent 7: Analyzes level content and suggests follow-up questions"""
    @staticmethod
    async def suggest_questions(level_content: str) -> List[str]:
        system_prompt = """
        You are 'The Curiosity Agent' (Agent 7). Identify complex technical terms in the text and generate 3-5 engaging follow-up questions (e.g., "Apa itu tensor?").
        Output MUST be a JSON object with a 'questions' array of strings.
        """
        result_json = await generate_json(system_prompt, f"Textbook Content:\n\n{level_content}")
        return result_json.get("questions", [])

class QuestionReviewer:
    """Agent 7.1: Reviews suggested follow-up questions"""
    @staticmethod
    async def refine_questions(draft_questions: List[str], level_content: str) -> List[str]:
        system_prompt = """
        You are 'The Curiosity Reviewer' (Agent 7.1). Review the draft follow-up questions based on the text.
        Make them more natural, highly contextual, and deeply inquisitive.
        Output MUST be a JSON object with a 'questions' array of strings.
        """
        draft_json = json.dumps({"questions": draft_questions})
        user_prompt = f"Content:\n{level_content}\n\nDraft Questions:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)
        return result_json.get("questions", [])
