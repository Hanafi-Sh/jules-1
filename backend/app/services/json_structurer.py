import json
import uuid
from typing import List, Tuple, Dict, Any
from app.services.llm_client import generate_json
from app.models.course import Prerequisite, Phase, Chapter, Level, QuizQuestion, Quiz

class JSONStructurer:
    """
    Dedicated agent to strictly convert raw unstructured text into structured JSON.
    Uses 'deepseek-chat' to save time and reasoning tokens. Does not alter pedagogy.
    """

    @staticmethod
    async def extract_triage(raw_text: str) -> Tuple[int, List[Prerequisite]]:
        system_prompt = "You are a strict data parser. Read the raw text which contains a complexity score and a list of prerequisites. Extract them perfectly into JSON format with 'complexity_score' (int) and 'prerequisites' (array of 'title' and 'description'). Do not change any meaning."
        result = await generate_json(system_prompt, f"Raw Text:\n{raw_text}", model="deepseek-chat")
        score = result.get("complexity_score", 5)
        prereqs = [Prerequisite(id=str(uuid.uuid4()), **p) for p in result.get("prerequisites", [])]
        return score, prereqs

    @staticmethod
    async def extract_phases(raw_text: str) -> Tuple[str, List[Phase]]:
        system_prompt = "You are a strict data parser. Read the raw text describing a syllabus outline. Extract the overarching Course Title and the Macro Pillars (Phases). Output MUST be a JSON object with 'title' (Course Title) and 'phases' (array of 'title' and 'description'). Do not alter the descriptions."
        result = await generate_json(system_prompt, f"Raw Text:\n{raw_text}", model="deepseek-chat")
        title = result.get("title", "Course")
        phases = [Phase(id=str(uuid.uuid4()), title=p["title"], description=p["description"], order=i+1) for i, p in enumerate(result.get("phases", []))]
        return title, phases

    @staticmethod
    async def extract_chapters(raw_text: str) -> List[Chapter]:
        system_prompt = "You are a strict data parser. Read the raw text describing the breakdown of a Phase into Chapters. Extract the chapters perfectly. Output MUST be a JSON object with a 'chapters' array containing 'title' and 'description'."
        result = await generate_json(system_prompt, f"Raw Text:\n{raw_text}", model="deepseek-chat")
        return [Chapter(id=str(uuid.uuid4()), title=c["title"], description=c["description"], order=i+1) for i, c in enumerate(result.get("chapters", []))]

    @staticmethod
    async def extract_levels(raw_text: str) -> List[Level]:
        system_prompt = "You are a strict data parser. Read the raw text describing the breakdown of a Chapter into Levels (sub-topics). Extract the levels perfectly. Output MUST be a JSON object with a 'levels' array containing 'title' and 'description'."
        result = await generate_json(system_prompt, f"Raw Text:\n{raw_text}", model="deepseek-chat")
        return [Level(id=str(uuid.uuid4()), title=l["title"], description=l["description"], order=i+1) for i, l in enumerate(result.get("levels", []))]

    @staticmethod
    async def extract_quiz(raw_text: str, level_id: str) -> Quiz:
        system_prompt = "You are a strict data parser. Read the raw text which contains multiple choice questions. Extract them into JSON. Output MUST be a JSON object with a 'questions' array containing 'question', 'options' (array of strings), 'correct_answer' (string), and 'explanation' (string)."
        result = await generate_json(system_prompt, f"Raw Text:\n{raw_text}", model="deepseek-chat")
        questions = [QuizQuestion(**q) for q in result.get("questions", [])]
        return Quiz(level_id=level_id, questions=questions)

    @staticmethod
    async def extract_suggested_questions(raw_text: str) -> List[str]:
        system_prompt = "You are a strict data parser. Read the raw text which lists suggested follow-up questions. Extract them into a JSON array. Output MUST be a JSON object with a 'questions' array of strings."
        result = await generate_json(system_prompt, f"Raw Text:\n{raw_text}", model="deepseek-chat")
        return result.get("questions", [])
