"""
Slalom Capabilities Management System API

A FastAPI application that enables Slalom consultants to register their
capabilities and manage consulting expertise across the organization.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from src.database import engine, get_db, Base
from src import models

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Slalom Capabilities Management API",
              description="API for managing consulting capabilities and consultant expertise")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Seed data used to populate an empty database on first run
SEED_CAPABILITIES = [
    {
        "name": "Cloud Architecture",
        "description": "Design and implement scalable cloud solutions using AWS, Azure, and GCP",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["AWS Solutions Architect", "Azure Architect Expert"],
        "industry_verticals": ["Healthcare", "Financial Services", "Retail"],
        "capacity": 40,
        "consultants": ["alice.smith@slalom.com", "bob.johnson@slalom.com"],
    },
    {
        "name": "Data Analytics",
        "description": "Advanced data analysis, visualization, and machine learning solutions",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Tableau Desktop Specialist", "Power BI Expert", "Google Analytics"],
        "industry_verticals": ["Retail", "Healthcare", "Manufacturing"],
        "capacity": 35,
        "consultants": ["emma.davis@slalom.com", "sophia.wilson@slalom.com"],
    },
    {
        "name": "DevOps Engineering",
        "description": "CI/CD pipeline design, infrastructure automation, and containerization",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Docker Certified Associate", "Kubernetes Admin", "Jenkins Certified"],
        "industry_verticals": ["Technology", "Financial Services"],
        "capacity": 30,
        "consultants": ["john.brown@slalom.com", "olivia.taylor@slalom.com"],
    },
    {
        "name": "Digital Strategy",
        "description": "Digital transformation planning and strategic technology roadmaps",
        "practice_area": "Strategy",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Digital Transformation Certificate", "Agile Certified Practitioner"],
        "industry_verticals": ["Healthcare", "Financial Services", "Government"],
        "capacity": 25,
        "consultants": ["liam.anderson@slalom.com", "noah.martinez@slalom.com"],
    },
    {
        "name": "Change Management",
        "description": "Organizational change leadership and adoption strategies",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Prosci Certified", "Lean Six Sigma Black Belt"],
        "industry_verticals": ["Healthcare", "Manufacturing", "Government"],
        "capacity": 20,
        "consultants": ["ava.garcia@slalom.com", "mia.rodriguez@slalom.com"],
    },
    {
        "name": "UX/UI Design",
        "description": "User experience design and digital product innovation",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Adobe Certified Expert", "Google UX Design Certificate"],
        "industry_verticals": ["Retail", "Healthcare", "Technology"],
        "capacity": 30,
        "consultants": ["amelia.lee@slalom.com", "harper.white@slalom.com"],
    },
    {
        "name": "Cybersecurity",
        "description": "Information security strategy, risk assessment, and compliance",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["CISSP", "CISM", "CompTIA Security+"],
        "industry_verticals": ["Financial Services", "Healthcare", "Government"],
        "capacity": 25,
        "consultants": ["ella.clark@slalom.com", "scarlett.lewis@slalom.com"],
    },
    {
        "name": "Business Intelligence",
        "description": "Enterprise reporting, data warehousing, and business analytics",
        "practice_area": "Technology",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Microsoft BI Certification", "Qlik Sense Certified"],
        "industry_verticals": ["Retail", "Manufacturing", "Financial Services"],
        "capacity": 35,
        "consultants": ["james.walker@slalom.com", "benjamin.hall@slalom.com"],
    },
    {
        "name": "Agile Coaching",
        "description": "Agile transformation and team coaching for scaled delivery",
        "practice_area": "Operations",
        "skill_levels": ["Emerging", "Proficient", "Advanced", "Expert"],
        "certifications": ["Certified Scrum Master", "SAFe Agilist", "ICAgile Certified"],
        "industry_verticals": ["Technology", "Financial Services", "Healthcare"],
        "capacity": 20,
        "consultants": ["charlotte.young@slalom.com", "henry.king@slalom.com"],
    },
]


def seed_database(db: Session) -> None:
    """Populate the database with initial capabilities if it is empty."""
    if db.query(models.Capability).count() > 0:
        return
    for entry in SEED_CAPABILITIES:
        capability = models.Capability(
            name=entry["name"],
            description=entry["description"],
            practice_area=entry["practice_area"],
            skill_levels=entry["skill_levels"],
            certifications=entry["certifications"],
            industry_verticals=entry["industry_verticals"],
            capacity=entry["capacity"],
        )
        db.add(capability)
        for email in entry["consultants"]:
            db.add(models.ConsultantCapability(capability_name=entry["name"], email=email))
    db.commit()


@app.on_event("startup")
def startup_event():
    from src.database import SessionLocal
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/capabilities")
def get_capabilities(db: Session = Depends(get_db)):
    capabilities = db.query(models.Capability).all()
    result = {}
    for cap in capabilities:
        consultants = (
            db.query(models.ConsultantCapability)
            .filter(models.ConsultantCapability.capability_name == cap.name)
            .all()
        )
        result[cap.name] = {
            "description": cap.description,
            "practice_area": cap.practice_area,
            "skill_levels": cap.skill_levels,
            "certifications": cap.certifications,
            "industry_verticals": cap.industry_verticals,
            "capacity": cap.capacity,
            "consultants": [c.email for c in consultants],
        }
    return result


@app.post("/capabilities/{capability_name}/register")
def register_for_capability(capability_name: str, email: str, db: Session = Depends(get_db)):
    """Register a consultant for a capability"""
    capability = db.query(models.Capability).filter(models.Capability.name == capability_name).first()
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    existing = (
        db.query(models.ConsultantCapability)
        .filter(
            models.ConsultantCapability.capability_name == capability_name,
            models.ConsultantCapability.email == email,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Consultant is already registered for this capability")

    db.add(models.ConsultantCapability(capability_name=capability_name, email=email))
    db.commit()
    return {"message": f"Registered {email} for {capability_name}"}


@app.delete("/capabilities/{capability_name}/unregister")
def unregister_from_capability(capability_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a consultant from a capability"""
    capability = db.query(models.Capability).filter(models.Capability.name == capability_name).first()
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    record = (
        db.query(models.ConsultantCapability)
        .filter(
            models.ConsultantCapability.capability_name == capability_name,
            models.ConsultantCapability.email == email,
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=400, detail="Consultant is not registered for this capability")

    db.delete(record)
    db.commit()
    return {"message": f"Unregistered {email} from {capability_name}"}
