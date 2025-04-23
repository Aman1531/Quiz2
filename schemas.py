from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date
from enum import Enum

# Enums for constrained choices
class DepartmentName(str, Enum):
    HR = "HR"
    ENGINEERING = "Engineering"
    MARKETING = "Marketing"
    FINANCE = "Finance"
    SALES = "Sales"

class ProjectStatus(str, Enum):
    PLANNING = "Planning"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"

class PaymentMethod(str, Enum):
    BANK_TRANSFER = "Bank Transfer"
    CHECK = "Check"
    DIRECT_DEPOSIT = "Direct Deposit"

# Department Schemas
class DepartmentBase(BaseModel):
    name: DepartmentName
    location: str = Field(..., example="New York")
    budget: float = Field(..., gt=0, example=250000.00)
    head_of_department: str = Field(..., example="John Smith")
    established_date: date = Field(..., example="2020-01-15")
    employee_count: int = Field(0, ge=0, example=25)

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    class Config:
        from_attributes = True

# Employee Schemas
class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50, example="Jane")
    last_name: str = Field(..., min_length=2, max_length=50, example="Doe")
    email: EmailStr = Field(..., example="jane.doe@example.com")
    phone: str = Field(..., pattern=r"^\+?[\d\s-]{10,15}$", example="+1-555-123-4567")
    hire_date: date = Field(..., example="2022-05-10")
    job_title: str = Field(..., example="Software Engineer")
    department_id: Optional[int] = Field(None, example=1)

    @validator("hire_date")
    def validate_hire_date(cls, v):
        if v > date.today():
            raise ValueError("Hire date cannot be in the future")
        return v

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    class Config:
        from_attributes = True

# Project Schemas
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=100, example="Website Redesign")
    description: Optional[str] = Field(None, max_length=500, 
                                     example="Redesign company website with modern UI")
    start_date: date = Field(..., example="2023-01-01")
    end_date: Optional[date] = Field(None, example="2023-06-30")
    budget: float = Field(..., gt=0, example=50000.00)
    status: ProjectStatus = Field(ProjectStatus.PLANNING, example="Planning")
    department_id: int = Field(..., example=1)

    @validator("end_date")
    def validate_end_date(cls, v, values):
        if v and "start_date" in values and v < values["start_date"]:
            raise ValueError("End date must be after start date")
        return v

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    class Config:
        from_attributes = True

# Salary Schemas
class SalaryBase(BaseModel):
    employee_id: int = Field(..., example=1)
    amount: float = Field(..., gt=0, example=75000.00)
    payment_date: date = Field(..., example="2023-03-15")
    tax_deduction: float = Field(0, ge=0, example=15000.00)
    bonus: float = Field(0, ge=0, example=5000.00)
    payment_method: PaymentMethod = Field(..., example="Bank Transfer")

class SalaryCreate(SalaryBase):
    pass

class SalaryResponse(SalaryBase):
    id: int
    class Config:
        from_attributes = True

# Relationship Schemas (For nested responses)
class EmployeeWithDepartment(EmployeeResponse):
    department: Optional[DepartmentResponse] = None

class DepartmentWithEmployees(DepartmentResponse):
    employees: List[EmployeeResponse] = []

class ProjectWithRelations(ProjectResponse):
    department: DepartmentResponse
    employees: List[EmployeeResponse] = []

class EmployeeWithRelations(EmployeeResponse):
    department: Optional[DepartmentResponse] = None
    projects: List[ProjectResponse] = []
    salaries: List[SalaryResponse] = []
