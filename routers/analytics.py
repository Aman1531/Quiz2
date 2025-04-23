from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func, and_, case
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Dict, List, Any
from models import Department, Employee, Project, Salary
from dependencies import get_db
import matplotlib.pyplot as plt
import base64
from io import BytesIO

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Helper function to generate base64 encoded chart images
def create_chart_image(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

@router.get("/visual-summary", response_model=Dict[str, Any])
def get_visual_analytics_summary(db: Session = Depends(get_db)):
    """
    Returns analytical summary with embedded visualizations including:
    - Department distribution (pie chart)
    - Salary statistics (bar chart)
    - Project status (donut chart)
    - Budget allocation (horizontal bar chart)
    - Recent hires trend (line chart)
    """
    try:
        # 1. Employee count by department
        dept_counts = db.query(
            Department.name,
            func.count(Employee.id).label("count")
        ).join(Employee).group_by(Department.name).all()
        
        # 2. Salary statistics
        salary_stats = db.query(
            func.avg(Salary.amount).label("avg"),
            func.min(Salary.amount).label("min"),
            func.max(Salary.amount).label("max"),
            func.stddev(Salary.amount).label("stddev")
        ).first()
        
        # 3. Project status
        project_status = db.query(
            Project.status,
            func.count(Project.id).label("count")
        ).group_by(Project.status).all()
        
        # 4. Recent hires (last 90 days)
        hire_trend = db.query(
            func.date(Employee.hire_date).label("date"),
            func.count(Employee.id).label("count")
        ).filter(
            Employee.hire_date >= date.today() - timedelta(days=90)
        ).group_by(func.date(Employee.hire_date)).order_by("date").all()
        
        # 5. Budget allocation
        budget_allocation = db.query(
            Department.name,
            Department.budget
        ).order_by(Department.budget.desc()).all()
        
        # Generate visualizations
        def generate_pie_chart(labels, sizes, title):
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            ax.set_title(title)
            return create_chart_image(fig)
        
        def generate_bar_chart(labels, values, title, ylabel):
            fig, ax = plt.subplots()
            bars = ax.bar(labels, values)
            ax.bar_label(bars)
            ax.set_ylabel(ylabel)
            ax.set_title(title)
            return create_chart_image(fig)
        
        def generate_line_chart(dates, values, title):
            fig, ax = plt.subplots()
            ax.plot(dates, values, marker="o")
            ax.set_title(title)
            fig.autofmt_xdate()
            return create_chart_image(fig)
        
        # Create all charts
        dept_chart = generate_pie_chart(
            [d.name for d in dept_counts],
            [d.count for d in dept_counts],
            "Employee Distribution by Department"
        )
        
        salary_chart = generate_bar_chart(
            ["Average", "Minimum", "Maximum", "Std Dev"],
            [float(salary_stats.avg), float(salary_stats.min), 
             float(salary_stats.max), float(salary_stats.stddev or 0)],
            "Salary Statistics",
            "USD"
        )
        
        project_chart = generate_pie_chart(
            [p.status for p in project_status],
            [p.count for p in project_status],
            "Project Status Distribution"
        )
        
        budget_chart = generate_bar_chart(
            [b.name for b in budget_allocation],
            [b.budget for b in budget_allocation],
            "Department Budget Allocation",
            "USD",
            horizontal=True
        )
        
        hire_trend_chart = generate_line_chart(
            [h.date.strftime("%Y-%m-%d") for h in hire_trend],
            [h.count for h in hire_trend],
            "Hiring Trend (Last 90 Days)"
        )
        
        return {
            "summary_data": {
                "department_distribution": dict(dept_counts),
                "salary_statistics": {
                    "average": round(float(salary_stats.avg), 2),
                    "minimum": round(float(salary_stats.min), 2),
                    "maximum": round(float(salary_stats.max), 2),
                    "standard_deviation": round(float(salary_stats.stddev or 0), 2)
                },
                "project_status": dict(project_status),
                "recent_hires_trend": [
                    {"date": h.date.strftime("%Y-%m-%d"), "count": h.count} 
                    for h in hire_trend
                ],
                "budget_allocation": [
                    {"department": b.name, "budget": b.budget} 
                    for b in budget_allocation
                ]
            },
            "visualizations": {
                "department_distribution": f"data:image/png;base64,{dept_chart}",
                "salary_statistics": f"data:image/png;base64,{salary_chart}",
                "project_status": f"data:image/png;base64,{project_chart}",
                "budget_allocation": f"data:image/png;base64,{budget_chart}",
                "hire_trend": f"data:image/png;base64,{hire_trend_chart}"
            },
            "chart_configs": {
                "department_distribution": {
                    "type": "pie",
                    "data_labels": [d.name for d in dept_counts],
                    "data_values": [d.count for d in dept_counts]
                },
                "salary_statistics": {
                    "type": "bar",
                    "categories": ["Average", "Minimum", "Maximum", "Std Dev"],
                    "series": [
                        {
                            "name": "Salary",
                            "data": [
                                round(float(salary_stats.avg), 2),
                                round(float(salary_stats.min), 2),
                                round(float(salary_stats.max), 2),
                                round(float(salary_stats.stddev or 0), 2)
                            ]
                        }
                    ]
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analytics generation failed: {str(e)}"
        )
