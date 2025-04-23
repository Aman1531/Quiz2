from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Department
from schemas import DepartmentCreate, DepartmentResponse
from dependencies import get_db

router = APIRouter(prefix="/departments", tags=["departments"])

@router.post("/", response_model=DepartmentResponse)
def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    db_department = Department(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

@router.get("/", response_model=list[DepartmentResponse])
def read_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()
