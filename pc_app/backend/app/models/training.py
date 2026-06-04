from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class TrainingSession(Base):
    __tablename__ = "training_sessions"
    
    id = Column(String, primary_key=True, index=True)
    session_name = Column(String, nullable=False)
    status = Column(String, default="IDLE") # IDLE, RECORDING, COMPLETED
    created_at = Column(DateTime, default=datetime.utcnow)
    
    samples = relationship("TrainingSample", back_populates="session")

class TrainingSample(Base):
    __tablename__ = "training_samples"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("training_sessions.id"))
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("TrainingSession", back_populates="samples")