from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import (
    departments,
    employees,
    projects,
    salaries,
    generate_data,
    analytics
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Employee Management API",
    description="A comprehensive API for managing employee data with departments, projects, and salaries",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "departments",
            "description": "Operations with company departments"
        },
        {
            "name": "employees",
            "description": "Manage employee records"
        },
        {
            "name": "projects",
            "description": "Track company projects"
        },
        {
            "name": "salaries",
            "description": "Handle salary information"
        },
        {
            "name": "Data Generation",
            "description": "Generate mock data for testing"
        },
        {
            "name": "Analytics",
            "description": "Generate analytics"
        }
    ]
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(projects.router)
app.include_router(salaries.router)
app.include_router(generate_data.router)
app.include_router(analytics.router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the Employee Management API",
        "endpoints": {
            "departments": "/departments",
            "employees": "/employees",
            "projects": "/projects",
            "salaries": "/salaries",
            "generate_data": "/generate/mock_data",
            "analytics" : "/summary"
        }
    }
