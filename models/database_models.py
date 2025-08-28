from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship     

Base = declarative_base()


class SpyCat(Base):
    __tablename__ = "spy_cats"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Added length for MySQL
    years_of_experience = Column(Integer, nullable=False)
    breed = Column(String(100), nullable=False)  # Added length for MySQL
    salary = Column(Float, nullable=False)
    
    # Relationship with missions
    missions = relationship("Mission", back_populates="cat")

class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(Integer, ForeignKey("spy_cats.id"), nullable=True)
    complete = Column(Boolean, default=False)
    
    # Relationships
    cat = relationship("SpyCat", back_populates="missions")
    targets = relationship("Target", back_populates="mission", cascade="all, delete-orphan")

class Target(Base):
    __tablename__ = "targets"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    name = Column(String(255), nullable=False)  # Added length for MySQL
    country = Column(String(100), nullable=False)  # Added length for MySQL
    notes = Column(Text, default="")  # Text doesn't need length
    complete = Column(Boolean, default=False)
    
    # Relationship
    mission = relationship("Mission", back_populates="targets")