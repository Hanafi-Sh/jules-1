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
from app.services.json_structurer import JSONStructurer

logger = logging.getLogger(__name__)
api_semaphore = asyncio.Semaphore(3)

async def generate_structural_tree_async(target_skill: str, user_context: str, update_progress_cb) -> Course:
    """Generates the hierarchical JSON structure using the decoupled Raw Text -> JSON pattern."""
    try:
        # Step 1: Triage
        update_progress_cb("Menganalisis kompleksitas dan prasyarat topik...")
        draft_triage_text = await TriageAnalyst.analyze_topic(target_skill)
        refined_triage_text = await TriageReviewer.refine_analysis(draft_triage_text, target_skill)
        score, final_prereqs = await JSONStructurer.extract_triage(refined_triage_text)

        unknown_prereqs = [p.title for p in final_prereqs]

        # Step 2: Syllabus/Macro Pillars
        update_progress_cb(f"Merancang Pilar Utama (Kompleksitas: {score}/10)...")
        draft_phases_text = await SyllabusArchitect.generate_phases(target_skill, user_context, score, unknown_prereqs)
        refined_phases_text = await SyllabusReviewer.refine_phases(draft_phases_text, target_skill, unknown_prereqs)
        final_title, final_phases = await JSONStructurer.extract_phases(refined_phases_text)

        course = Course(
            id="temp", title=final_title, target_skill=target_skill,
            complexity_score=score, prerequisites=final_prereqs, phases=final_phases
        )
        course_context_json = course.model_dump_json(exclude={"phases": {"__all__": {"chapters"}}})

        # Step 3: Phase -> Chapter
        update_progress_cb("Memecah Pilar menjadi Bab Spesifik...")
        async def process_phase(phase):
            async with api_semaphore:
                draft_ch_text = await PhaseDesigner.design_chapters(phase.title, phase.description, target_skill, course_context_json)
                refined_ch_text = await PhaseReviewer.refine_chapters(draft_ch_text, phase.title, course_context_json)
                phase.chapters = await JSONStructurer.extract_chapters(refined_ch_text)

        await asyncio.gather(*[process_phase(p) for p in course.phases])
        course_context_json = course.model_dump_json(exclude={"phases": {"__all__": {"chapters": {"__all__": {"levels"}}}}})

        # Step 4: Chapter -> Level
        update_progress_cb("Mendesain Level (Micro) untuk setiap Bab...")
        async def process_chapter(chapter):
            async with api_semaphore:
                draft_lvl_text = await ChapterDesigner.design_levels(chapter.title, chapter.description, target_skill, course_context_json)
                refined_lvl_text = await ChapterReviewer.refine_levels(draft_lvl_text, chapter.title, course_context_json)
                chapter.levels = await JSONStructurer.extract_levels(refined_lvl_text)

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
