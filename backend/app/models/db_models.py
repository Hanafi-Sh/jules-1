from sqlalchemy import Column, String, Integer, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

class DBUserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(String, primary_key=True, index=True) # Could be a generated uuid
    user_id = Column(String, index=True)
    target_skill = Column(String)
    current_level_id = Column(String, nullable=True)

class DBCourseState(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    target_skill = Column(String)
    course_data = Column(Text) # JSON string representation of the full course structure

class DBGenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    status = Column(String) # pending, processing, completed, failed
    progress_message = Column(String)
    course_data = Column(Text, nullable=True) # Will hold the final json when done
