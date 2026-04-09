from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.services.agents import (
    ContentAuthor, ContentReviewer,
    Formatter,
    QuizMaster, QuizReviewer,
    QuestionSuggester, QuestionReviewer
)
from app.services.json_structurer import JSONStructurer
from app.models.course import Level, Quiz

router = APIRouter()

class LazyLoadLevelRequest(BaseModel):
    level_id: str
    level_title: str
    level_description: str
    target_skill: str
    course_context: Dict[str, Any] = {}

@router.post("/level/lazy-load", response_model=Level)
async def lazy_load_level(request: LazyLoadLevelRequest):
    import json
    try:
        course_context_json = json.dumps(request.course_context) if request.course_context else ""
        level = Level(id=request.level_id, title=request.level_title, description=request.level_description, order=0)

        # 1. Content Generation (Raw Text)
        draft_content = await ContentAuthor.write_content(level.title, level.description, request.target_skill, course_context_json)
        refined_content = await ContentReviewer.refine_content(draft_content, level.title, course_context_json)

        # 2. UI Formatting (Raw Text)
        level.content = await Formatter.format_content(refined_content)

        # 3. Curiosity Questions (Raw -> JSON)
        draft_q_text = await QuestionSuggester.suggest_questions(level.content, course_context_json)
        refined_q_text = await QuestionReviewer.refine_questions(draft_q_text, level.content, course_context_json)
        level.suggested_questions = await JSONStructurer.extract_suggested_questions(refined_q_text)

        # Note: If generating Quiz, it would be:
        # draft_quiz_text = await QuizMaster.generate_quiz(...)
        # refined_quiz_text = await QuizReviewer.refine_quiz(...)
        # quiz = await JSONStructurer.extract_quiz(refined_quiz_text, level.id)

        return level
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
