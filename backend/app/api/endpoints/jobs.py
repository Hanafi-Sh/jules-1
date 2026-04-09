from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
import json
import logging

from app.db.session import get_db, SessionLocal
from app.models.db_models import DBGenerationJob, DBCourseState
from app.services.orchestrator import generate_full_course_async
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)

class JobCreateRequest(BaseModel):
    user_id: str
    target_skill: str
    user_context: str
    known_prerequisites: List[str] = []

async def background_course_generation(job_id: str, request: JobCreateRequest):
    # Must instantiate its own isolated DB session because the HTTP request one is closed!
    db = SessionLocal()

    def update_progress(msg: str):
        logger.info(f"[JOB {job_id}] {msg}")
        job = db.query(DBGenerationJob).filter(DBGenerationJob.id == job_id).first()
        if job:
            job.progress_message = msg
            db.commit()

    try:
        job = db.query(DBGenerationJob).filter(DBGenerationJob.id == job_id).first()
        job.status = "processing"
        db.commit()

        # Run the massive parallel orchestrator
        final_course = await generate_full_course_async(
            target_skill=request.target_skill,
            user_context=request.user_context,
            known_prereqs=request.known_prerequisites,
            update_progress_cb=update_progress
        )

        course_json = final_course.model_dump_json()

        # Update Job Status
        job.status = "completed"
        job.progress_message = "Generasi selesai."
        job.course_data = course_json
        db.commit()

        # Also save to user's main course state
        db_course = db.query(DBCourseState).filter(
            DBCourseState.user_id == request.user_id,
            DBCourseState.target_skill == request.target_skill
        ).first()

        if db_course:
            db_course.course_data = course_json
        else:
            db_course = DBCourseState(
                id=str(uuid.uuid4()),
                user_id=request.user_id,
                target_skill=request.target_skill,
                course_data=course_json
            )
            db.add(db_course)
        db.commit()

    except Exception as e:
        logger.error(f"[JOB {job_id}] Failed: {str(e)}")
        job = db.query(DBGenerationJob).filter(DBGenerationJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.progress_message = f"Error: {str(e)}"
            db.commit()
    finally:
        db.close() # Clean up the isolated session

@router.post("/start")
def start_generation_job(request: JobCreateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    new_job = DBGenerationJob(
        id=job_id,
        user_id=request.user_id,
        status="pending",
        progress_message="Menyiapkan generasi course..."
    )
    db.add(new_job)
    db.commit()

    # Do NOT pass the HTTP session (db) to the background task!
    background_tasks.add_task(background_course_generation, job_id, request)
    return {"job_id": job_id, "status": "pending"}

@router.get("/status/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(DBGenerationJob).filter(DBGenerationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id": job.id,
        "status": job.status,
        "progress_message": job.progress_message
    }

    if job.status == "completed" and job.course_data:
        response["course_data"] = json.loads(job.course_data)

    return response
