from typing import List
from app.services.llm_client import generate_text

def build_context_prefix(course_context_json: str) -> str:
    if not course_context_json:
        return ""
    return f"--- MASTER CURRICULUM CONTEXT ---\n{course_context_json}\n---------------------------------\n\n"

class TriageAnalyst:
    """Agent 0: Evaluates complexity and prerequisites (Dependency Mapping)"""
    @staticmethod
    async def analyze_topic(target_skill: str) -> str:
        system_prompt = """
        You are the 'Triage Analyst' (Agent 0). Analyze the requested target skill.
        First, state the complexity score from 1 to 10.
        Second, write a clear list of the absolute fundamental prerequisite concepts required to master it, including titles and descriptions for each.
        Write purely in plain text, do NOT output JSON formatting.
        """
        user_prompt = f"Target Skill: {target_skill}"
        return await generate_text(system_prompt, user_prompt)

class TriageReviewer:
    """Agent 0.1: Reviews the Triage Analysis"""
    @staticmethod
    async def refine_analysis(draft_text: str, target_skill: str) -> str:
        system_prompt = """
        You are the 'Triage Reviewer' (Agent 0.1). Review the complexity score and prerequisites drafted for the target skill.
        Ensure no crucial foundational dependencies are missed. Adjust the score if unrealistic.
        Output ONLY the refined text (Score and list of prerequisites). Do NOT output JSON.
        """
        user_prompt = f"Target Skill: {target_skill}\nDraft Analysis:\n{draft_text}"
        return await generate_text(system_prompt, user_prompt)

class SyllabusArchitect:
    """Agent 1: Generates the Macro Pillars (Phases)"""
    @staticmethod
    async def generate_phases(target_skill: str, user_context: str, complexity_score: int, unknown_prereqs: List[str]) -> str:
        system_prompt = """
        You are 'The Syllabus Architect' (Agent 1). Create the Macro Pillars (Phases) for learning a specific skill up to an ADVANCED level.
        Do NOT write specific chapters yet. Focus on high-level macro phases.
        CRITICAL: Ensure the phases cover the unknown prerequisites early on.
        The number of phases should scale with the complexity score.
        Write purely in plain text, do NOT output JSON formatting. Just list the Course Title and the Phases with descriptions.
        """
        user_prompt = f"Target Skill: {target_skill}\nComplexity Score: {complexity_score}/10\nUser Context: {user_context}\nUnknown Prereqs to teach: {', '.join(unknown_prereqs) if unknown_prereqs else 'None'}"
        return await generate_text(system_prompt, user_prompt)

class SyllabusReviewer:
    """Agent 1.1: Critiques the Macro Phases"""
    @staticmethod
    async def refine_phases(draft_text: str, target_skill: str, unknown_prereqs: List[str]) -> str:
        system_prompt = """
        You are 'The Syllabus Reviewer' (Agent 1.1). Review the draft Macro Phases.
        Are they perfectly MECE? Do they form a logical Directed Acyclic Graph (DAG) progression? Are unknown prerequisites adequately covered at the start?
        Output ONLY the refined text list of phases. Do NOT output JSON.
        """
        user_prompt = f"Target Skill: {target_skill}\nUnknown Prereqs: {', '.join(unknown_prereqs)}\nDraft Phases:\n{draft_text}"
        return await generate_text(system_prompt, user_prompt)

class PhaseDesigner:
    """Agent 2: Breaks down a Phase into Chapters"""
    @staticmethod
    async def design_chapters(phase_title: str, phase_desc: str, target_skill: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + """
        You are 'The Phase Designer' (Agent 2). Break down the requested Macro Phase into highly specific MECE 'Chapters'.
        Write purely in plain text. Just list the Chapters and their descriptions. Do NOT output JSON formatting.
        """
        user_prompt = f"Skill: {target_skill}\nDesign Chapters for Phase: {phase_title}\nDescription: {phase_desc}"
        return await generate_text(system_prompt, user_prompt)

class PhaseReviewer:
    """Agent 2.1: Reviews the Chapters within a Phase"""
    @staticmethod
    async def refine_chapters(draft_text: str, phase_title: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Phase Reviewer' (Agent 2.1). Review the draft chapters for this phase. Ensure they are MECE. Output ONLY the refined text list of chapters. Do NOT output JSON."
        user_prompt = f"Review Chapters for Phase: {phase_title}\nDraft Chapters:\n{draft_text}"
        return await generate_text(system_prompt, user_prompt)

class ChapterDesigner:
    """Agent 3: Breaks down a chapter into specific Levels"""
    @staticmethod
    async def design_levels(chapter_title: str, chapter_desc: str, target_skill: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Chapter Designer' (Agent 3). Break down the requested chapter into MECE 'Levels' (sub-topics). Output purely plain text list of levels and descriptions. Do NOT format as JSON."
        user_prompt = f"Skill: {target_skill}\nDesign Levels for Chapter: {chapter_title}\nDescription: {chapter_desc}"
        return await generate_text(system_prompt, user_prompt)

class ChapterReviewer:
    """Agent 3.1: Reviews the levels in a chapter"""
    @staticmethod
    async def refine_levels(draft_text: str, chapter_title: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Chapter Reviewer' (Agent 3.1). Review the draft levels for this chapter against the Master Curriculum. Ensure they are MECE. Output ONLY the refined text list of levels. Do NOT output JSON."
        user_prompt = f"Review Levels for Chapter: {chapter_title}\nDraft Levels:\n{draft_text}"
        return await generate_text(system_prompt, user_prompt)

class ContentAuthor:
    """Agent 4: Writes the comprehensive content for a Level"""
    @staticmethod
    async def write_content(level_title: str, level_desc: str, target_skill: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Content Author' (Agent 4). Write extremely comprehensive, deep, and engaging textbook content for the requested Level. Do NOT worry about UI formatting tags."
        user_prompt = f"Skill: {target_skill}\nWrite Content for Level: {level_title}\nLevel Description: {level_desc}"
        return await generate_text(system_prompt, user_prompt)

class ContentReviewer:
    """Agent 4.1: Reviews and refines textbook content"""
    @staticmethod
    async def refine_content(draft_content: str, level_title: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Content Reviewer' (Agent 4.1). Read the draft textbook content. Fix hallucinations, improve analogies, and ensure pedagogical perfection. Output ONLY the improved raw text."
        user_prompt = f"Level Title: {level_title}\nDraft Content to Refine:\n\n{draft_content}"
        return await generate_text(system_prompt, user_prompt)

class Formatter:
    """Agent 5: Formats the content into UI-ready markdown"""
    @staticmethod
    async def format_content(raw_content: str) -> str:
        system_prompt = """
        You are 'The Formatter' (Agent 5). Format the text beautifully for a frontend 'Vertical Journey'.
        CRITICAL: Use custom React/Next.js friendly HTML/Markdown tags:
        - <InfoBox type="caution">...</InfoBox> or <InfoBox type="info">...</InfoBox>
        - <Accordion title="Deep Dive: Topic Name">...</Accordion>
        Ensure code blocks use standard markdown ```language tags.
        """
        return await generate_text(system_prompt, f"Raw Content:\n\n{raw_content}", model="deepseek-chat")

class QuizMaster:
    """Agent 6: Generates validation questions"""
    @staticmethod
    async def generate_quiz(level_content: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Quiz Master' (Agent 6). Generate 2-3 high-quality multiple-choice questions based on the content. Write in plain text, do NOT output JSON."
        return await generate_text(system_prompt, f"Content:\n{level_content}")

class QuizReviewer:
    """Agent 6.1: Reviews the validation questions"""
    @staticmethod
    async def refine_quiz(draft_text: str, level_content: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Quiz Reviewer' (Agent 6.1). Review the draft quiz questions against the content for factual accuracy. Output ONLY the refined text. Do NOT format as JSON."
        user_prompt = f"Content:\n{level_content}\n\nDraft Quiz:\n{draft_text}"
        return await generate_text(system_prompt, user_prompt)

class QuestionSuggester:
    """Agent 7: Analyzes level content and suggests follow-up questions"""
    @staticmethod
    async def suggest_questions(level_content: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Curiosity Agent' (Agent 7). Identify complex technical terms and write 3-5 engaging follow-up questions. Write in plain text, do NOT output JSON."
        return await generate_text(system_prompt, f"Textbook Content:\n\n{level_content}")

class QuestionReviewer:
    """Agent 7.1: Reviews suggested follow-up questions"""
    @staticmethod
    async def refine_questions(draft_text: str, level_content: str, course_context_json: str) -> str:
        prefix = build_context_prefix(course_context_json)
        system_prompt = prefix + "You are 'The Curiosity Reviewer' (Agent 7.1). Make the draft follow-up questions more natural and inquisitive. Output ONLY the refined plain text questions. Do NOT format as JSON."
        user_prompt = f"Content:\n{level_content}\n\nDraft Questions:\n{draft_text}"
        return await generate_text(system_prompt, user_prompt)
