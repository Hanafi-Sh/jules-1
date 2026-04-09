import uuid
import json
from typing import List, Optional, Tuple
from app.services.llm_client import generate_json, generate_text
from app.models.course import Course, Phase, Chapter, Level, Quiz, QuizQuestion, Prerequisite

def build_context_prefix(course_context_json: str) -> str:
    if not course_context_json:
        return ""
    return f"--- MASTER CURRICULUM CONTEXT ---\n{course_context_json}\n---------------------------------\n\n"

class TriageAnalyst:
    """Agent 0: Evaluates complexity and prerequisites (Dependency Mapping)"""
    @staticmethod
    async def analyze_topic(target_skill: str) -> Tuple[int, List[Prerequisite]]:
        system_prompt = """
        You are the 'Triage Analyst' (Agent 0). Your job is to analyze the requested target skill.
        First, assign a complexity score from 1 to 10 (1 = e.g., boiling an egg, 10 = e.g., building an LLM from scratch).
        Second, identify the absolute fundamental prerequisite concepts required to master it.
        Output MUST be a JSON object with 'complexity_score' (int) and a 'prerequisites' array (each with 'title' and 'description').
        """
        user_prompt = f"Target Skill: {target_skill}"
        result_json = await generate_json(system_prompt, user_prompt)

        score = result_json.get("complexity_score", 5)
        prereqs = [Prerequisite(id=str(uuid.uuid4()), **p) for p in result_json.get("prerequisites", [])]
        return score, prereqs

class TriageReviewer:
    """Agent 0.1: Reviews the Triage Analysis"""
    @staticmethod
    async def refine_analysis(draft_score: int, draft_prereqs: List[Prerequisite], target_skill: str) -> Tuple[int, List[Prerequisite]]:
        system_prompt = """
        You are the 'Triage Reviewer' (Agent 0.1). Review the complexity score and prerequisites for the target skill.
        Ensure no crucial foundational dependencies are missed. Adjust the complexity score if it's unrealistic.
        Output MUST be a JSON object with 'complexity_score' (int) and 'prerequisites' array ('title', 'description').
        """
        draft_json = json.dumps({"complexity_score": draft_score, "prerequisites": [{"title": p.title, "description": p.description} for p in draft_prereqs]}, indent=2)
        user_prompt = f"Target Skill: {target_skill}\nDraft Analysis:\n{draft_json}\n\nProvide the refined JSON."
        result_json = await generate_json(system_prompt, user_prompt)

        score = result_json.get("complexity_score", draft_score)
        prereqs = [Prerequisite(id=str(uuid.uuid4()), **p) for p in result_json.get("prerequisites", [])]
        return score, prereqs

class SyllabusArchitect:
    """Agent 1: Generates the Macro Pillars (Phases) based on complexity and prerequisites"""
    @staticmethod
    async def generate_phases(target_skill: str, user_context: str, complexity_score: int, unknown_prereqs: List[str]) -> List[Phase]:
        system_prompt = """
        You are 'The Syllabus Architect' (Agent 1). Create the Macro Pillars (Phases) for learning a specific skill up to an ADVANCED level.
        Do NOT write specific chapters yet. Focus on high-level macro phases (e.g., 'Phase 1: Mathematical Foundations', 'Phase 2: Predictive Algorithms').
        CRITICAL: Ensure the phases cover the unknown prerequisites early on.
        The number of phases should scale with the complexity score.
        Output MUST be a JSON object with 'title' (Course Title), 'target_skill', and 'phases' (list of dicts with 'title' and 'description').
        """
        user_prompt = f"Target Skill: {target_skill}\nComplexity Score: {complexity_score}/10\nUser Context: {user_context}\nUnknown Prereqs to teach: {', '.join(unknown_prereqs) if unknown_prereqs else 'None'}"
        result_json = await generate_json(system_prompt, user_prompt)

        phases = [Phase(id=str(uuid.uuid4()), title=p["title"], description=p["description"], order=i+1) for i, p in enumerate(result_json.get("phases", []))]
        return result_json.get("title", f"Mastering {target_skill}"), phases

class SyllabusReviewer:
    """Agent 1.1: Critiques the Macro Phases"""
    @staticmethod
    async def refine_phases(draft_title: str, draft_phases: List[Phase], target_skill: str, unknown_prereqs: List[str]) -> Tuple[str, List[Phase]]:
        system_prompt = """
        You are 'The Syllabus Reviewer' (Agent 1.1). Review the draft Macro Phases.
        Are they perfectly MECE? Do they form a logical Directed Acyclic Graph (DAG) progression? Are unknown prerequisites adequately covered at the start?
        Output MUST be a JSON object with 'title' and 'phases' ('title', 'description').
        """
        draft_json = json.dumps({"title": draft_title, "phases": [{"title": p.title, "description": p.description} for p in draft_phases]}, indent=2)
        user_prompt = f"Target Skill: {target_skill}\nUnknown Prereqs: {', '.join(unknown_prereqs)}\nDraft Phases:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)

        phases = [Phase(id=str(uuid.uuid4()), title=p["title"], description=p["description"], order=i+1) for i, p in enumerate(result_json.get("phases", []))]
        return result_json.get("title", draft_title), phases

class PhaseDesigner:
    """Agent 2: Breaks down a Phase into Chapters (Micro-level)"""
    @staticmethod
    async def design_chapters(phase_title: str, phase_desc: str, target_skill: str, course_context_json: str) -> List[Chapter]:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Phase Designer' (Agent 2). Break down the requested Macro Phase into highly specific MECE 'Chapters'. Output MUST be a JSON object with a 'chapters' array containing 'title' and 'description'."
        user_prompt = f"Skill: {target_skill}\nDesign Chapters for Phase: {phase_title}\nDescription: {phase_desc}"
        result_json = await generate_json(system_prompt, user_prompt)
        return [Chapter(id=str(uuid.uuid4()), title=c["title"], description=c["description"], order=i+1) for i, c in enumerate(result_json.get("chapters", []))]

class PhaseReviewer:
    """Agent 2.1: Reviews the Chapters within a Phase"""
    @staticmethod
    async def refine_chapters(draft_chapters: List[Chapter], phase_title: str, course_context_json: str) -> List[Chapter]:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Phase Reviewer' (Agent 2.1). Review the draft chapters for this phase against the Master Curriculum. Ensure they are MECE. Output MUST be a JSON object with a 'chapters' array containing 'title' and 'description'."
        draft_json = json.dumps([{"title": c.title, "description": c.description} for c in draft_chapters], indent=2)
        user_prompt = f"Review Chapters for Phase: {phase_title}\nDraft Chapters:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)
        return [Chapter(id=str(uuid.uuid4()), title=c["title"], description=c["description"], order=i+1) for i, c in enumerate(result_json.get("chapters", []))]

class ChapterDesigner:
    """Agent 3: Breaks down a chapter into specific Levels"""
    @staticmethod
    async def design_levels(chapter_title: str, chapter_desc: str, target_skill: str, course_context_json: str) -> List[Level]:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Chapter Designer' (Agent 3). Break down the requested chapter into MECE 'Levels' (sub-topics) progressing from fundamental to specific. Output MUST be a JSON object with a 'levels' array containing 'title' and 'description'."
        user_prompt = f"Skill: {target_skill}\nDesign Levels for Chapter: {chapter_title}\nDescription: {chapter_desc}"
        result_json = await generate_json(system_prompt, user_prompt)
        return [Level(id=str(uuid.uuid4()), title=l["title"], description=l["description"], order=i+1) for i, l in enumerate(result_json.get("levels", []))]

class ChapterReviewer:
    """Agent 3.1: Reviews the levels in a chapter"""
    @staticmethod
    async def refine_levels(draft_levels: List[Level], chapter_title: str, course_context_json: str) -> List[Level]:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Chapter Reviewer' (Agent 3.1). Review the draft levels for this chapter against the Master Curriculum. Ensure they are MECE and flow perfectly. Output MUST be a JSON object with a 'levels' array containing 'title' and 'description'."
        draft_json = json.dumps([{"title": l.title, "description": l.description} for l in draft_levels], indent=2)
        user_prompt = f"Review Levels for Chapter: {chapter_title}\nDraft Levels:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)
        return [Level(id=str(uuid.uuid4()), title=l["title"], description=l["description"], order=i+1) for i, l in enumerate(result_json.get("levels", []))]

class ContentAuthor:
    """Agent 4: Writes the comprehensive content for a Level"""
    @staticmethod
    async def write_content(level: Level, target_skill: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Content Author' (Agent 4). Look at the Master Curriculum Context to understand where this level fits. Write extremely comprehensive, deep, and engaging textbook content for the requested Level. Do NOT worry about UI formatting tags."
        user_prompt = f"Skill: {target_skill}\nWrite Content for Level: {level.title}\nLevel Description: {level.description}"
        return await generate_text(system_prompt, user_prompt)

class ContentReviewer:
    """Agent 4.1: Reviews and refines textbook content"""
    @staticmethod
    async def refine_content(draft_content: str, level_title: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Content Reviewer' (Agent 4.1). Read the draft textbook content. Fix hallucinations, improve analogies, and ensure it aligns with the Master Curriculum Context. Output ONLY the improved raw markdown text."
        user_prompt = f"Level Title: {level_title}\nDraft Content to Refine:\n\n{draft_content}"
        return await generate_text(system_prompt, user_prompt)

class Formatter:
    """Agent 5: Formats the content into UI-ready markdown"""
    @staticmethod
    async def format_content(raw_content: str) -> str:
        system_prompt = """
        You are 'The Formatter' (Agent 5). Format the text beautifully for a frontend 'Vertical Journey'.
        CRITICAL: You must use custom React/Next.js friendly HTML/Markdown tags for special UI components:
        - For important notes or warnings, wrap them in: <InfoBox type="caution">...</InfoBox> or <InfoBox type="info">...</InfoBox>
        - For extra deep-dive explanations that can be collapsed, wrap them in: <Accordion title="Deep Dive: Topic Name">...</Accordion>
        - Ensure all code blocks use standard markdown ```language tags.
        Do not change the pedadogy, just wrap existing concepts in these beautiful UI tags where appropriate.
        """
        return await generate_text(system_prompt, f"Raw Content:\n\n{raw_content}", model="deepseek-chat")

class QuizMaster:
    """Agent 6: Generates validation questions"""
    @staticmethod
    async def generate_quiz(level_content: str, level_id: str, course_context_json: str) -> Quiz:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Quiz Master' (Agent 6). Generate 2-3 high-quality multiple-choice questions based on the content. Output MUST be a JSON object with a 'questions' array ('question', 'options', 'correct_answer', 'explanation')."
        result_json = await generate_json(system_prompt, f"Content:\n{level_content}")
        questions = [QuizQuestion(**q) for q in result_json.get("questions", [])]
        return Quiz(level_id=level_id, questions=questions)

class QuizReviewer:
    """Agent 6.1: Reviews the validation questions"""
    @staticmethod
    async def refine_quiz(draft_quiz: Quiz, level_content: str, course_context_json: str) -> Quiz:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Quiz Reviewer' (Agent 6.1). Review the draft quiz questions against the content. Output MUST be a JSON object with a 'questions' array."
        draft_json = json.dumps([q.model_dump() for q in draft_quiz.questions], indent=2)
        user_prompt = f"Content:\n{level_content}\n\nDraft Quiz:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)
        questions = [QuizQuestion(**q) for q in result_json.get("questions", [])]
        return Quiz(level_id=draft_quiz.level_id, questions=questions)

class QuestionSuggester:
    """Agent 7: Analyzes level content and suggests follow-up questions"""
    @staticmethod
    async def suggest_questions(level_content: str, course_context_json: str) -> List[str]:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Curiosity Agent' (Agent 7). Identify complex technical terms in the text and generate 3-5 engaging follow-up questions for the user to ask the AI later. Output MUST be a JSON object with a 'questions' array of strings."
        result_json = await generate_json(system_prompt, f"Textbook Content:\n\n{level_content}")
        return result_json.get("questions", [])

class QuestionReviewer:
    """Agent 7.1: Reviews suggested follow-up questions"""
    @staticmethod
    async def refine_questions(draft_questions: List[str], level_content: str, course_context_json: str) -> List[str]:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Curiosity Reviewer' (Agent 7.1). Review the draft follow-up questions. Make them highly contextual based on the Master Curriculum. Output MUST be a JSON object with a 'questions' array of strings."
        draft_json = json.dumps({"questions": draft_questions})
        user_prompt = f"Content:\n{level_content}\n\nDraft Questions:\n{draft_json}"
        result_json = await generate_json(system_prompt, user_prompt)
        return result_json.get("questions", [])
