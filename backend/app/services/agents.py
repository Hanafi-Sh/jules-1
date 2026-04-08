import uuid
from typing import List
from app.services.llm_client import generate_json, generate_text
from app.models.course import Course, Chapter, Level, Quiz, QuizQuestion

class SyllabusArchitect:
    """Agent 1: Generates the high-level chapters based on user prompt"""
    @staticmethod
    async def generate_syllabus(target_skill: str, user_context: str) -> Course:
        system_prompt = """
        You are 'The Syllabus Architect'. Your job is to create a MECE (Mutually Exclusive, Collectively Exhaustive) syllabus for learning a specific skill.
        Output MUST be a JSON object with 'title', 'target_skill', and 'chapters'.
        Each chapter should have 'title' and 'description'. Do NOT go into deep specifics, just high-level chapters.
        Ensure you follow the user's specific context (e.g. if they know OOP, skip basic OOP).
        """
        user_prompt = f"Target Skill: {target_skill}\nContext: {user_context}"

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

class ChapterDesigner:
    """Agent 2: Breaks down a chapter into specific Levels"""
    @staticmethod
    async def design_chapter(chapter_title: str, chapter_desc: str, target_skill: str) -> List[Level]:
        system_prompt = """
        You are 'The Chapter Designer'. Your job is to break down a high-level chapter into logical, step-by-step 'Levels' (sub-topics).
        Output MUST be a JSON object with a 'levels' array.
        Each level should have 'title' and 'description'.
        The levels should be MECE, progressing from fundamental to specific for this chapter.
        """
        user_prompt = f"Skill: {target_skill}\nChapter: {chapter_title}\nDescription: {chapter_desc}"

        result_json = await generate_json(system_prompt, user_prompt)

        levels = []
        for i, lvl_data in enumerate(result_json.get("levels", [])):
            levels.append(Level(
                id=str(uuid.uuid4()),
                title=lvl_data["title"],
                description=lvl_data["description"],
                order=i + 1
            ))

        return levels

class ContentAuthor:
    """Agent 3: Writes the comprehensive content for a Level"""
    @staticmethod
    async def write_content(level: Level, target_skill: str) -> str:
        system_prompt = """
        You are 'The Content Author'. Write comprehensive, deep, and engaging textbook content for a specific Level.
        Use analogies, clear explanations, and code examples if it's a technical skill.
        Do NOT worry about formatting UI elements yet, just write raw, high-quality markdown text.
        """
        user_prompt = f"Skill: {target_skill}\nLevel Title: {level.title}\nLevel Description: {level.description}"

        content = await generate_text(system_prompt, user_prompt)
        return content

class Formatter:
    """Agent 4: Formats the content into UI-ready markdown"""
    @staticmethod
    async def format_content(raw_content: str) -> str:
        system_prompt = """
        You are 'The Formatter'. Your job is to take raw markdown text and format it beautifully for a UI 'Vertical Journey'.
        - Use clean Markdown.
        - Add ':::caution' or ':::info' blocks for important notes.
        - Ensure code blocks have proper syntax highlighting tags.
        - Break up very long paragraphs.
        Do not change the meaning of the content, just the presentation.
        """
        user_prompt = f"Raw Content:\n\n{raw_content}"

        formatted_content = await generate_text(system_prompt, user_prompt)
        return formatted_content

class QuizMaster:
    """Agent 5: Generates validation questions"""
    @staticmethod
    async def generate_quiz(level_content: str, level_id: str) -> Quiz:
        system_prompt = """
        You are 'The Quiz Master'. Generate 2-3 multiple-choice questions to test the user's understanding of the provided content.
        Output MUST be a JSON object with a 'questions' array.
        Each question object MUST have 'question' (str), 'options' (list of str), 'correct_answer' (str), and 'explanation' (str).
        """
        user_prompt = f"Content:\n{level_content}"

        result_json = await generate_json(system_prompt, user_prompt)

        questions = []
        for q_data in result_json.get("questions", []):
            questions.append(QuizQuestion(
                question=q_data["question"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"]
            ))

        return Quiz(level_id=level_id, questions=questions)
