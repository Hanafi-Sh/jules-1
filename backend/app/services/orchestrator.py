import asyncio
import json
import uuid
import logging
from typing import Dict, Any, List

from app.models.course import Course, Chapter, Level, Quiz
from app.services.agents import (
    PrerequisiteAssessor, PrerequisiteReviewer,
    SyllabusArchitect, SyllabusReviewer,
    ChapterDesigner, ChapterReviewer,
    ContentAuthor, ContentReviewer,
    Formatter,
    QuizMaster, QuizReviewer,
    QuestionSuggester, QuestionReviewer
)

logger = logging.getLogger(__name__)

# Semaphore to prevent hitting API rate limits during massive parallel processing
MAX_CONCURRENT_API_CALLS = 5
api_semaphore = asyncio.Semaphore(MAX_CONCURRENT_API_CALLS)

async def process_level(level: Level, target_skill: str, course_context_json: str, update_progress_cb) -> None:
    """Processes a single Level end-to-end (Author -> Formatter -> Quiz -> Questions)."""
    try:
        # Agent 3 & 3.1
        async with api_semaphore:
            update_progress_cb(f"Menulis materi untuk level: {level.title}...")
            draft_content = await ContentAuthor.write_content(level, target_skill, course_context_json)
            refined_content = await ContentReviewer.refine_content(draft_content, level.title, course_context_json)

        # Agent 4
        async with api_semaphore:
            update_progress_cb(f"Memformat materi untuk level: {level.title}...")
            formatted_content = await Formatter.format_content(refined_content)
            level.content = formatted_content

        # We can run Quiz and Questions in parallel because they both just depend on formatted_content
        async def process_quiz():
            async with api_semaphore:
                draft_quiz = await QuizMaster.generate_quiz(formatted_content, level.id, course_context_json)
                return await QuizReviewer.refine_quiz(draft_quiz, formatted_content, course_context_json)

        async def process_questions():
            async with api_semaphore:
                draft_questions = await QuestionSuggester.suggest_questions(formatted_content, course_context_json)
                return await QuestionReviewer.refine_questions(draft_questions, formatted_content, course_context_json)

        update_progress_cb(f"Membuat Kuis & Pertanyaan untuk level: {level.title}...")
        quiz, questions = await asyncio.gather(process_quiz(), process_questions())

        # Although we don't return the quiz directly attached to the level model in our current schema,
        # in a real DB we would save it here. For the orchestrator, we attach questions to the level.
        level.suggested_questions = questions

        update_progress_cb(f"Selesai memproses level: {level.title}")
    except Exception as e:
        logger.error(f"Error processing level {level.title}: {str(e)}")
        raise e

async def process_chapter(chapter: Chapter, target_skill: str, course_context_json: str, update_progress_cb) -> None:
    """Processes a single Chapter: breaks into Levels, then processes all Levels in parallel."""
    try:
        async with api_semaphore:
            update_progress_cb(f"Mendesain level untuk BAB: {chapter.title}...")
            draft_levels = await ChapterDesigner.design_chapter(chapter.title, chapter.description, target_skill, course_context_json)
            final_levels = await ChapterReviewer.refine_chapter(draft_levels, chapter.title, chapter.description, course_context_json)
            chapter.levels = final_levels

        # Process all levels in this chapter concurrently
        level_tasks = [
            process_level(lvl, target_skill, course_context_json, update_progress_cb)
            for lvl in chapter.levels
        ]
        await asyncio.gather(*level_tasks)
    except Exception as e:
        logger.error(f"Error processing chapter {chapter.title}: {str(e)}")
        raise e

async def generate_full_course_async(
    target_skill: str,
    user_context: str,
    known_prereqs: List[str],
    update_progress_cb
) -> Course:
    """Orchestrates the entire 8-Agent pipeline to generate a full course in parallel."""
    try:
        # Phase 1: Prerequisites
        update_progress_cb("Sedang melakukan asesmen prasyarat (Prerequisite Assessor)...")
        draft_prereqs = await PrerequisiteAssessor.get_prerequisites(target_skill)
        final_prereqs = await PrerequisiteReviewer.refine_prerequisites(draft_prereqs, target_skill)

        unknown_prereqs = [p.title for p in final_prereqs if p.title not in known_prereqs]

        # Phase 2: Syllabus
        update_progress_cb("Sedang merancang silabus utama (Syllabus Architect)...")
        draft_course = await SyllabusArchitect.generate_syllabus(target_skill, user_context, known_prereqs, unknown_prereqs)
        final_course = await SyllabusReviewer.refine_syllabus(draft_course, user_context, unknown_prereqs)

        course_context_json = json.dumps({
            "title": final_course.title,
            "target_skill": final_course.target_skill,
            "chapters": [{"title": c.title, "description": c.description} for c in final_course.chapters]
        })

        # Phase 3: Parallel Chapter Generation
        # Each chapter will independently break down into levels, and each level will write its content
        update_progress_cb(f"Mulai memproses {len(final_course.chapters)} BAB secara paralel...")

        chapter_tasks = [
            process_chapter(ch, target_skill, course_context_json, update_progress_cb)
            for ch in final_course.chapters
        ]
        await asyncio.gather(*chapter_tasks)

        update_progress_cb("Generasi Full Course Selesai!")
        return final_course

    except Exception as e:
        logger.error(f"Failed to generate full course: {str(e)}")
        update_progress_cb(f"Error: {str(e)}")
        raise e
