import uuid
from typing import List
from app.services.llm_client import generate_json, generate_text
from app.models.course import Course, Chapter, Level, Quiz, QuizQuestion

class SyllabusArchitect:
    """Agent 1: Generates the high-level chapters based on user prompt"""
    @staticmethod
    async def generate_syllabus(target_skill: str, user_context: str) -> Course:
        system_prompt = """
        You are 'The Syllabus Architect'. Your job is to deeply think about and create a MECE (Mutually Exclusive, Collectively Exhaustive) syllabus for learning a specific skill.
        Focus entirely on the quality, logical progression, and exhaustiveness of the curriculum.
        Output MUST be a JSON object with 'title' (str), 'target_skill' (str), and 'chapters' (list of dicts).
        Each chapter dict should have 'title' (str) and 'description' (str).
        Do NOT worry about markdown formatting. Just output the pure data structure.
        Ensure you follow the user's specific context (e.g. if they know OOP, skip basic OOP).
        """
        user_prompt = f"Target Skill: {target_skill}\nContext: {user_context}"

        # Uses deepseek-reasoner by default
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
        You are 'The Chapter Designer'. Your job is to deeply analyze a high-level chapter and break it down into logical, step-by-step 'Levels' (sub-topics).
        The levels should be MECE, progressing smoothly from fundamental to specific for this chapter without overlapping concepts.
        Output MUST be a JSON object with a 'levels' array.
        Each level dict should have 'title' (str) and 'description' (str).
        """
        user_prompt = f"Skill: {target_skill}\nChapter: {chapter_title}\nDescription: {chapter_desc}"

        # Uses deepseek-reasoner by default
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
        You are 'The Content Author'. Write an extremely comprehensive, deep, and engaging textbook content for a specific Level.
        Use deep reasoning to explain complex topics. Use analogies, clear explanations, and code examples if it's a technical skill.
        DO NOT worry about formatting UI elements, beautiful markdown, or strict structural tags yet.
        Focus 100% on the highest quality pedagogy and content depth. The Formatter will handle presentation later.
        """
        user_prompt = f"Skill: {target_skill}\nLevel Title: {level.title}\nLevel Description: {level.description}"

        # Uses deepseek-reasoner by default
        content = await generate_text(system_prompt, user_prompt)
        return content

class Formatter:
    """Agent 4: Formats the content into UI-ready markdown"""
    @staticmethod
    async def format_content(raw_content: str) -> str:
        system_prompt = """
        You are 'The Formatter'. Your job is to take raw, high-quality textbook text and format it beautifully for a UI 'Vertical Journey'.
        - Use clean Markdown.
        - Add ':::caution' or ':::info' blocks for important notes.
        - Ensure code blocks have proper syntax highlighting tags.
        - Break up very long paragraphs into readable micro-chunks.
        Do not change the underlying meaning or pedadogy of the content, just optimize the presentation and readability.
        """
        user_prompt = f"Raw Content:\n\n{raw_content}"

        # Explicitly use deepseek-chat for fast and simple formatting without reasoning overhead
        formatted_content = await generate_text(system_prompt, user_prompt, model="deepseek-chat")
        return formatted_content

class QuizMaster:
    """Agent 5: Generates validation questions"""
    @staticmethod
    async def generate_quiz(level_content: str, level_id: str) -> Quiz:
        system_prompt = """
        You are 'The Quiz Master'. Use deep reasoning to generate 2-3 high-quality multiple-choice questions that test the user's true understanding of the provided content.
        Avoid obvious questions. Test concepts, not just rote memorization.
        Output MUST be a JSON object with a 'questions' array.
        Each question object MUST have 'question' (str), 'options' (list of str), 'correct_answer' (str), and 'explanation' (str).
        """
        user_prompt = f"Content:\n{level_content}"

        # Uses deepseek-reasoner by default
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
