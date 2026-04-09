from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.services.agents import (
    ContentAuthor, ContentReviewer,
    Formatter,
    QuizMaster, QuizReviewer,
    QuestionSuggester, QuestionReviewer
)
from app.models.course import Level, Quiz

router = APIRouter()

class LazyLoadLevelRequest(BaseModel):
    level_id: str
    level_title: str
    level_description: str
    target_skill: str
    course_context: Dict[str, Any] = {} # For caching context

@router.post("/level/lazy-load", response_model=Level)
async def lazy_load_level(request: LazyLoadLevelRequest):
    """
    Just-In-Time Generation!
    Called by the frontend ONLY when the user clicks or scrolls to this specific level.
    It generates the heavy textbook content, formats it, builds the quiz, and suggests questions.
    """
    import json
    try:
        course_context_json = json.dumps(request.course_context) if request.course_context else ""
        level = Level(id=request.level_id, title=request.level_title, description=request.level_description, order=0)

        # 1. Content Generation
        draft_content = await ContentAuthor.write_content(level, request.target_skill, course_context_json)
        refined_content = await ContentReviewer.refine_content(draft_content, level.title, course_context_json)
        level.content = await Formatter.format_content(refined_content)

        # 2. Curiosity Questions
        draft_questions = await QuestionSuggester.suggest_questions(level.content, course_context_json)
        level.suggested_questions = await QuestionReviewer.refine_questions(draft_questions, level.content, course_context_json)

        # Note: In a full DB implementation, we would also generate the Quiz here and save it to the DB linked to the level_id.

        return level
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
