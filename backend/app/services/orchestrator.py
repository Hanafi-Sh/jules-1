import asyncio
import json
import logging
from typing import List

from app.models.course import Course
from app.services.agents import (
    TriageAnalyst, TriageReviewer,
    SyllabusArchitect, SyllabusReviewer,
    PhaseDesigner, PhaseReviewer,
    ChapterDesigner, ChapterReviewer
)

logger = logging.getLogger(__name__)
api_semaphore = asyncio.Semaphore(3)

async def generate_structural_tree_async(target_skill: str, user_context: str, update_progress_cb) -> Course:
    """Generates the massive hierarchical JSON structure (Course -> Phase -> Chapter -> Level) WITHOUT content."""
    try:
        # Step 1: Triage (Agent 0 & 0.1)
        update_progress_cb("Menganalisis kompleksitas dan prasyarat topik...")
        draft_score, draft_prereqs = await TriageAnalyst.analyze_topic(target_skill)
        score, final_prereqs = await TriageReviewer.refine_analysis(draft_score, draft_prereqs, target_skill)

        # We assume for this MVP that the user does not know any prereqs and we must teach them all
        unknown_prereqs = [p.title for p in final_prereqs]

        # Step 2: Syllabus/Macro Pillars (Agent 1 & 1.1)
        update_progress_cb(f"Merancang Pilar Utama (Kompleksitas: {score}/10)...")
        draft_title, draft_phases = await SyllabusArchitect.generate_phases(target_skill, user_context, score, unknown_prereqs)
        final_title, final_phases = await SyllabusReviewer.refine_phases(draft_title, draft_phases, target_skill, unknown_prereqs)

        # Create the Course shell
        course = Course(
            id="temp", title=final_title, target_skill=target_skill,
            complexity_score=score, prerequisites=final_prereqs, phases=final_phases
        )

        # Helper string for caching
        course_context_json = course.model_dump_json(exclude={"phases": {"__all__": {"chapters"}}})

        # Step 3: Phase -> Chapter Breakdown (Agent 2 & 2.1)
        update_progress_cb("Memecah Pilar menjadi Bab Spesifik...")
        async def process_phase(phase):
            async with api_semaphore:
                draft_ch = await PhaseDesigner.design_chapters(phase.title, phase.description, target_skill, course_context_json)
                phase.chapters = await PhaseReviewer.refine_chapters(draft_ch, phase.title, course_context_json)

        await asyncio.gather(*[process_phase(p) for p in course.phases])

        # Update cache string
        course_context_json = course.model_dump_json(exclude={"phases": {"__all__": {"chapters": {"__all__": {"levels"}}}}})

        # Step 4: Chapter -> Level Breakdown (Agent 3 & 3.1)
        update_progress_cb("Mendesain Level (Micro) untuk setiap Bab...")
        async def process_chapter(chapter):
            async with api_semaphore:
                draft_lvl = await ChapterDesigner.design_levels(chapter.title, chapter.description, target_skill, course_context_json)
                chapter.levels = await ChapterReviewer.refine_levels(draft_lvl, chapter.title, course_context_json)

        chapter_tasks = []
        for phase in course.phases:
            for chapter in phase.chapters:
                chapter_tasks.append(process_chapter(chapter))

        await asyncio.gather(*chapter_tasks)

        update_progress_cb("Struktur Kurikulum Selesai Dibuat!")
        return course

    except Exception as e:
        logger.error(f"Failed structure generation: {str(e)}")
        update_progress_cb(f"Error: {str(e)}")
        raise e
