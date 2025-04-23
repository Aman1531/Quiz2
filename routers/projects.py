from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Project
from schemas import ProjectCreate, ProjectResponse
from dependencies import get_db

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=list[ProjectResponse])
def read_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()
