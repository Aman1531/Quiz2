from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Salary
from schemas import SalaryCreate, SalaryResponse
from dependencies import get_db

router = APIRouter(prefix="/salaries", tags=["salaries"])

@router.post("/", response_model=SalaryResponse)
def create_salary(salary: SalaryCreate, db: Session = Depends(get_db)):
    db_salary = Salary(**salary.model_dump())
    db.add(db_salary)
    db.commit()
    db.refresh(db_salary)
    return db_salary

@router.get("/", response_model=list[SalaryResponse])
def read_salaries(db: Session = Depends(get_db)):
    return db.query(Salary).all()
