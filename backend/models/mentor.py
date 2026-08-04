from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Mentor(Base):
    """Mentor model for database - stores additional mentor-specific information"""
    __tablename__ = "mentors"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to User (authentication)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Personal Information
    name = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    
    # Professional Information
    qualification = Column(String(255), nullable=False)  # e.g., "M.Tech", "PhD", "B.E."
    specialization = Column(String(255), nullable=False)  # e.g., "Data Science", "Web Development"
    experience_years = Column(Integer, nullable=False, default=0)  # Years of teaching/industry experience
    bio = Column(Text, nullable=True)  # Short bio/introduction
    
    # Profile
    profile_image_url = Column(String(512), nullable=True)
    linkedin_url = Column(String(512), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="joined"
    )
    
    def __repr__(self):
        return f"<Mentor(id={self.id}, name={self.name}, specialization={self.specialization})>"
