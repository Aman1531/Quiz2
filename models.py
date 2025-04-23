from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    location = Column(String(100))
    budget = Column(Float)
    head_of_department = Column(String(50))
    established_date = Column(Date)
    employee_count = Column(Integer, default=0)
    
    # Properly define relationships
    employees = relationship("Employee", back_populates="department")
    projects = relationship("Project", back_populates="department")

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, index=True)
    phone = Column(String(20))
    hire_date = Column(Date)
    job_title = Column(String(50))
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    # Relationships
    department = relationship("Department", back_populates="employees")
    projects = relationship("ProjectEmployee", back_populates="employee")
    salaries = relationship("Salary", back_populates="employee")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(Float)
    status = Column(String(20), default="Planning")
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    # Relationships
    department = relationship("Department", back_populates="projects")
    employees = relationship("ProjectEmployee", back_populates="project")

class Salary(Base):
    __tablename__ = "salaries"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    amount = Column(Float, nullable=False)
    payment_date = Column(Date)
    tax_deduction = Column(Float)
    bonus = Column(Float, default=0)
    payment_method = Column(String(20))
    
    employee = relationship("Employee", back_populates="salaries")

class ProjectEmployee(Base):
    __tablename__ = "project_employees"
    
    employee_id = Column(Integer, ForeignKey("employees.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    role = Column(String(50))
    join_date = Column(Date)
    
    employee = relationship("Employee", back_populates="projects")
    project = relationship("Project", back_populates="employees")
