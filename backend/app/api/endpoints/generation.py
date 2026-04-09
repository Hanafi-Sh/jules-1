from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

from app.services.agents import (
    PrerequisiteAssessor, PrerequisiteReviewer,
    SyllabusArchitect, SyllabusReviewer,
    ChapterDesigner, ChapterReviewer,
    ContentAuthor, ContentReviewer,
    Formatter,
    QuizMaster, QuizReviewer,
    QuestionSuggester, QuestionReviewer
)
from app.models.course import Course, Chapter, Level, Quiz, Prerequisite

router = APIRouter()

class PrerequisiteRequest(BaseModel):
    target_skill: str

class CourseRequest(BaseModel):
    target_skill: str
    user_context: str
    known_prerequisites: List[str] = []
    unknown_prerequisites: List[str] = []

class ChapterDesignRequest(BaseModel):
    chapter_title: str
    chapter_description: str
    target_skill: str

class LevelContentRequest(BaseModel):
    level_title: str
    level_description: str
    target_skill: str

@router.post("/prerequisites", response_model=List[Prerequisite])
async def assess_prerequisites(request: PrerequisiteRequest):
    try:
        # Agent 0
        draft_prereqs = await PrerequisiteAssessor.get_prerequisites(request.target_skill)
        # Agent 0.1
        final_prereqs = await PrerequisiteReviewer.refine_prerequisites(draft_prereqs, request.target_skill)
        return final_prereqs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/syllabus", response_model=Course)
async def generate_syllabus(request: CourseRequest):
    try:
        # Agent 1
        draft_course = await SyllabusArchitect.generate_syllabus(
            target_skill=request.target_skill,
            user_context=request.user_context,
            known_prereqs=request.known_prerequisites,
            unknown_prereqs=request.unknown_prerequisites
        )
        # Agent 1.1 (formerly Agent 6)
        final_course = await SyllabusReviewer.refine_syllabus(
            draft_course=draft_course,
            user_context=request.user_context,
            unknown_prereqs=request.unknown_prerequisites
        )
        return final_course
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chapter/{chapter_id}/design", response_model=List[Level])
async def design_chapter(chapter_id: str, request: ChapterDesignRequest):
    try:
        # Agent 2
        draft_levels = await ChapterDesigner.design_chapter(
            chapter_title=request.chapter_title,
            chapter_desc=request.chapter_description,
            target_skill=request.target_skill
        )
        # Agent 2.1
        final_levels = await ChapterReviewer.refine_chapter(
            draft_levels=draft_levels,
            chapter_title=request.chapter_title,
            chapter_desc=request.chapter_description
        )
        return final_levels
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/level/{level_id}/content", response_model=Level)
async def generate_level_content(level_id: str, request: LevelContentRequest):
    try:
        level = Level(id=level_id, title=request.level_title, description=request.level_description, order=0)

        # Agent 3
        draft_content = await ContentAuthor.write_content(level, request.target_skill)
        # Agent 3.1
        refined_content = await ContentReviewer.refine_content(draft_content, level.title)

        # Agent 4
        formatted_content = await Formatter.format_content(refined_content)
        level.content = formatted_content

        # Agent 7
        draft_questions = await QuestionSuggester.suggest_questions(formatted_content)
        # Agent 7.1
        final_questions = await QuestionReviewer.refine_questions(draft_questions, formatted_content)
        level.suggested_questions = final_questions

        return level
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QuizRequest(BaseModel):
    level_content: str

@router.post("/level/{level_id}/quiz", response_model=Quiz)
async def generate_quiz(level_id: str, request: QuizRequest):
    try:
        # Agent 5
        draft_quiz = await QuizMaster.generate_quiz(
            level_content=request.level_content,
            level_id=level_id
        )
        # Agent 5.1
        final_quiz = await QuizReviewer.refine_quiz(draft_quiz, request.level_content)
        return final_quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
