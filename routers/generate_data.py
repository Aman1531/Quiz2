from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from faker import Faker
import random
from typing import List

# Import models and schemas
from models import Department, Employee, Project, Salary, ProjectEmployee
from schemas import (
    DepartmentName,
    ProjectStatus,
    PaymentMethod,
    DepartmentCreate,
    EmployeeCreate,
    ProjectCreate,
    SalaryCreate
)
from dependencies import get_db

router = APIRouter(prefix="/generate", tags=["Data Generation"])
fake = Faker()

# Constants for realistic data generation
JOB_TITLES = [
    "Software Engineer", "HR Manager", "Marketing Specialist",
    "Financial Analyst", "Sales Executive", "Product Manager"
]

def generate_phone():
    return f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"

@router.post("/mock_data")
async def generate_mock_data(
    departments: int = 3,
    employees_per_dept: int = 5,
    projects_per_dept: int = 2,
    salaries_per_employee: int = 3,
    db: Session = Depends(get_db)
):
    try:
        # Clear existing data in proper order
        db.query(ProjectEmployee).delete()
        db.query(Salary).delete()
        db.query(Project).delete()
        db.query(Employee).delete()
        db.query(Department).delete()
        db.commit()

        # ===== 1. Generate Departments =====
        dept_objects = []
        used_dept_names = set()  # Track used department names
        
        # Get all enum values and shuffle them
        all_dept_names = list(DepartmentName)
        random.shuffle(all_dept_names)
        
        for i in range(min(departments, len(all_dept_names))):  # Ensure we don't exceed available names
            dept_name = all_dept_names[i]
            dept_data = DepartmentCreate(
                name=dept_name,
                location=f"{fake.city()}, {fake.state_abbr()}",
                budget=round(random.uniform(100000, 500000), 2),
                head_of_department=fake.name(),
                established_date=fake.date_between(start_date="-5y", end_date="today"),
                employee_count=employees_per_dept
            )
            dept = Department(**dept_data.model_dump())
            db.add(dept)
            dept_objects.append(dept)
            used_dept_names.add(dept_name)
        
        # If more departments requested than enum values, use modified names
        for i in range(len(all_dept_names), departments):
            base_name = random.choice(all_dept_names)
            dept_name = f"{base_name} {random.randint(1, 100)}"
            dept_data = DepartmentCreate(
                name=dept_name,
                location=f"{fake.city()}, {fake.state_abbr()}",
                budget=round(random.uniform(100000, 500000), 2),
                head_of_department=fake.name(),
                established_date=fake.date_between(start_date="-5y", end_date="today"),
                employee_count=employees_per_dept
            )
            dept = Department(**dept_data.model_dump())
            db.add(dept)
            dept_objects.append(dept)
        
        db.commit()

        # ===== Rest of your generation code remains the same =====
        # ... (employee, project, salary generation) ...
   # ===== 2. Generate Employees =====
        employee_objects = []
        for dept in dept_objects:
            for _ in range(employees_per_dept):
                emp_data = EmployeeCreate(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.unique.email(),
                    phone=generate_phone(),
                    hire_date=fake.date_between(
                        start_date=dept.established_date,
                        end_date="today"
                    ),
                    job_title=random.choice(JOB_TITLES),
                    department_id=dept.id
                )
                employee = Employee(**emp_data.model_dump())
                db.add(employee)
                employee_objects.append(employee)
        db.commit()

        # ===== 3. Generate Projects =====
        project_objects = []
        for dept in dept_objects:
            for _ in range(projects_per_dept):
                start_date = fake.date_between(start_date="-1y", end_date="+6m")
                project_data = ProjectCreate(
                    name=f"Project {fake.color_name().title()}",
                    description=fake.sentence(nb_words=10),
                    start_date=start_date,
                    end_date=fake.date_between(
                        start_date=start_date + timedelta(days=30),
                        end_date=start_date + timedelta(days=180)
                    ),
                    budget=round(random.uniform(20000, 150000), 2),
                    status=random.choice(list(ProjectStatus)),
                    department_id=dept.id
                )
                project = Project(**project_data.model_dump())
                db.add(project)
                project_objects.append(project)
        db.commit()

        # ===== 4. Generate Project Assignments =====
        for project in project_objects:
            # Assign 2-5 random employees to each project
            assignees = random.sample(
                [e for e in employee_objects if e.department_id == project.department_id],
                k=random.randint(2, min(5, employees_per_dept))
            )
            
            for emp in assignees:
                assignment = ProjectEmployee(
                    employee_id=emp.id,
                    project_id=project.id,
                    role=random.choice(["Lead", "Member", "Contributor"]),
                    join_date=fake.date_between(
                        start_date=project.start_date,
                        end_date=project.start_date + timedelta(days=30))
                )
                db.add(assignment)
        db.commit()

        # ===== 5. Generate Salaries =====
        for emp in employee_objects:
            base_salary = random.uniform(45000, 120000)
            for _ in range(salaries_per_employee):
                salary_data = SalaryCreate(
                    employee_id=emp.id,
                    amount=round(base_salary * random.uniform(0.9, 1.1), 2),  # ±10% variation
                    payment_date=fake.date_between(
                        start_date=emp.hire_date,
                        end_date="today"),
                    tax_deduction=round(base_salary * 0.2 * random.uniform(0.8, 1.2), 2),
                    bonus=round(base_salary * 0.1 * random.random(), 2),
                    payment_method=random.choice(list(PaymentMethod))
                )
                db.add(Salary(**salary_data.model_dump()))
        db.commit()

        return {
            "message": "Mock data generated successfully",
            "stats": {
                "departments": len(dept_objects),
                "employees": len(employee_objects),
                "projects": len(project_objects),
                "salaries": len(employee_objects) * salaries_per_employee
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Data generation failed: {str(e)}"
        )
