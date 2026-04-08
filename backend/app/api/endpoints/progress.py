from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
import json

from app.db.session import get_db
from app.models.db_models import DBCourseState, DBUserProgress

router = APIRouter()

class SaveCourseRequest(BaseModel):
    user_id: str
    target_skill: str
    course_data: dict # The JSON output from syllabus generation

@router.post("/save_course")
def save_course(request: SaveCourseRequest, db: Session = Depends(get_db)):
    # Check if a course for this user and skill already exists to avoid duplication
    db_course = db.query(DBCourseState).filter(
        DBCourseState.user_id == request.user_id,
        DBCourseState.target_skill == request.target_skill
    ).first()

    if db_course:
        # Update existing record
        db_course.course_data = json.dumps(request.course_data)
    else:
        # Create new record
        db_course = DBCourseState(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            target_skill=request.target_skill,
            course_data=json.dumps(request.course_data)
        )
        db.add(db_course)

    db.commit()
    db.refresh(db_course)
    return {"status": "success", "course_id": db_course.id}

@router.get("/get_course/{user_id}")
def get_course(user_id: str, db: Session = Depends(get_db)):
    # Assuming one active course per user for MVP
    db_course = db.query(DBCourseState).filter(DBCourseState.user_id == user_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return {
        "id": db_course.id,
        "user_id": db_course.user_id,
        "target_skill": db_course.target_skill,
        "course_data": json.loads(db_course.course_data)
    }
