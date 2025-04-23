from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Employee
from schemas import EmployeeCreate, EmployeeResponse , EmployeeWithRelations
from dependencies import get_db

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("/", response_model=EmployeeResponse)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.get("/", response_model=list[EmployeeResponse])
def read_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()
# In your routes (e.g., routers/employees.py)

@router.get("/{employee_id}", response_model=EmployeeWithRelations)
def get_employee_with_relations(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee  # SQLAlchemy -> Pydantic auto-conversion
