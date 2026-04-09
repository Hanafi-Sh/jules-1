from pydantic import BaseModel, Field
from typing import List, Optional

class Prerequisite(BaseModel):
    id: str = Field(..., description="Unique identifier for the prerequisite")
    title: str = Field(..., description="Title of the prerequisite skill")
    description: str = Field(..., description="Why this is needed before learning the target skill")

class Level(BaseModel):
    id: str = Field(..., description="Unique identifier for the level")
    title: str = Field(..., description="Title of the level")
    description: str = Field(..., description="Brief description of what will be learned")
    order: int = Field(..., description="Order of the level in the chapter")
    content: Optional[str] = Field(None, description="The formatted markdown content for this level. None if not yet generated.")
    suggested_questions: Optional[List[str]] = Field(default_factory=list, description="AI suggested follow-up questions")

class Chapter(BaseModel):
    id: str = Field(..., description="Unique identifier for the chapter")
    title: str = Field(..., description="Title of the chapter")
    description: str = Field(..., description="Brief description of the chapter")
    order: int = Field(..., description="Order of the chapter in the phase")
    levels: List[Level] = Field(default_factory=list, description="List of levels in this chapter")

class Phase(BaseModel):
    id: str = Field(..., description="Unique identifier for the Phase (Macro Pillar)")
    title: str = Field(..., description="Title of the phase")
    description: str = Field(..., description="High level description of this learning phase")
    order: int = Field(..., description="Order of the phase in the course")
    chapters: List[Chapter] = Field(default_factory=list, description="List of specific chapters in this phase")

class Course(BaseModel):
    id: str = Field(..., description="Unique identifier for the course")
    title: str = Field(..., description="Title of the course based on user input")
    target_skill: str = Field(..., description="The main skill the user wants to master")
    complexity_score: int = Field(1, description="1-10 score indicating how deep/complex the topic is")
    prerequisites: List[Prerequisite] = Field(default_factory=list, description="List of required foundational skills")
    phases: List[Phase] = Field(default_factory=list, description="List of Macro Pillars in this course")

class QuizQuestion(BaseModel):
    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="List of multiple choice options")
    correct_answer: str = Field(..., description="The correct answer from the options")
    explanation: str = Field(..., description="Explanation of why the answer is correct")

class Quiz(BaseModel):
    level_id: str = Field(..., description="The level this quiz belongs to")
    questions: List[QuizQuestion] = Field(..., description="List of questions for this quiz")
