from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import uuid

from app.services.agents import (
    SyllabusArchitect,
    CurriculumSupervisor,
    ChapterDesigner,
    ContentAuthor,
    Formatter,
    QuizMaster
)
from app.models.course import Course, Chapter, Level, Quiz

router = APIRouter()

class CourseRequest(BaseModel):
    target_skill: str
    user_context: str

class ChapterDesignRequest(BaseModel):
    chapter_title: str
    chapter_description: str
    target_skill: str

class LevelContentRequest(BaseModel):
    level_title: str
    level_description: str
    target_skill: str

@router.post("/syllabus", response_model=Course)
async def generate_syllabus(request: CourseRequest):
    """Generates the high-level course and chapters based on the user's request, then reviews it via Supervisor."""
    try:
        # Agent 1: Draft the syllabus
        draft_course = await SyllabusArchitect.generate_syllabus(
            target_skill=request.target_skill,
            user_context=request.user_context
        )

        # Agent 6: Critique and Refine the syllabus
        final_course = await CurriculumSupervisor.refine_syllabus(
            draft_course=draft_course,
            user_context=request.user_context
        )

        return final_course
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chapter/{chapter_id}/design", response_model=List[Level])
async def design_chapter(chapter_id: str, request: ChapterDesignRequest):
    """Breaks down a specific chapter into levels."""
    try:
        levels = await ChapterDesigner.design_chapter(
            chapter_title=request.chapter_title,
            chapter_desc=request.chapter_description,
            target_skill=request.target_skill
        )
        # Inherit chapter id reference if needed
        return levels
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/level/{level_id}/content", response_model=Level)
async def generate_level_content(level_id: str, request: LevelContentRequest):
    """Generates and formats the content for a specific level."""
    try:
        # Create a mock level object to pass to the ContentAuthor
        level = Level(
            id=level_id,
            title=request.level_title,
            description=request.level_description,
            order=0  # order doesn't matter here
        )

        # Agent 3: Generate Raw Content
        raw_content = await ContentAuthor.write_content(level, request.target_skill)

        # Agent 4: Format Content
        formatted_content = await Formatter.format_content(raw_content)

        level.content = formatted_content
        return level
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QuizRequest(BaseModel):
    level_content: str

@router.post("/level/{level_id}/quiz", response_model=Quiz)
async def generate_quiz(level_id: str, request: QuizRequest):
    """Generates validation quiz for a level's content."""
    try:
        quiz = await QuizMaster.generate_quiz(
            level_content=request.level_content,
            level_id=level_id
        )
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
