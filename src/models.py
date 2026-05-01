"""
SQLAlchemy ORM models for the Slalom Capabilities Management System.
"""

from sqlalchemy import Column, String, Integer, JSON, ForeignKey, UniqueConstraint
from src.database import Base


class Capability(Base):
    __tablename__ = "capabilities"

    name = Column(String, primary_key=True, index=True)
    description = Column(String, nullable=False)
    practice_area = Column(String, nullable=False)
    skill_levels = Column(JSON, nullable=False, default=list)
    certifications = Column(JSON, nullable=False, default=list)
    industry_verticals = Column(JSON, nullable=False, default=list)
    capacity = Column(Integer, nullable=False, default=0)


class ConsultantCapability(Base):
    __tablename__ = "consultant_capabilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    capability_name = Column(String, ForeignKey("capabilities.name", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("capability_name", "email", name="uq_consultant_capability"),
    )
