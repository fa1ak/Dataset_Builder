"""
Database models and configuration for the Dataset Processor
"""
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid
import json

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/dataset_processor")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProcessingJob(Base):
    """Model for tracking document processing jobs"""
    __tablename__ = "processing_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Processing results
    word_count = Column(Integer, default=0)
    element_count = Column(Integer, default=0)
    total_elements_found = Column(Integer, default=0)
    processed_count = Column(Integer, default=0)
    skipped_count = Column(Integer, default=0)
    
    # User information
    user_id = Column(String(100), nullable=True)  # For future user management
    session_id = Column(String(100), nullable=True)
    
    # Processing metadata
    processing_time_seconds = Column(Float, nullable=True)
    export_paths = Column(JSON, nullable=True)  # Paths to exported files
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "word_count": self.word_count,
            "element_count": self.element_count,
            "total_elements_found": self.total_elements_found,
            "processed_count": self.processed_count,
            "skipped_count": self.skipped_count,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "processing_time_seconds": self.processing_time_seconds,
            "export_paths": self.export_paths
        }

class ProcessedElement(Base):
    """Model for storing individual processed elements"""
    __tablename__ = "processed_elements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False)
    element_type = Column(String(100), nullable=False)
    text_content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    coordinates = Column(JSON, nullable=True)
    element_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "job_id": str(self.job_id),
            "element_type": self.element_type,
            "text_content": self.text_content,
            "metadata": self.metadata,
            "coordinates": self.coordinates,
            "element_index": self.element_index,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class UserSession(Base):
    """Model for tracking user sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(String(100), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "is_active": self.is_active,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address
        }

# Database utility functions
def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_job_by_id(db: Session, job_id: str) -> Optional[ProcessingJob]:
    """Get processing job by ID"""
    return db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()

def get_jobs_by_session(db: Session, session_id: str) -> List[ProcessingJob]:
    """Get all jobs for a session"""
    return db.query(ProcessingJob).filter(ProcessingJob.session_id == session_id).all()

def create_job(db: Session, filename: str, file_path: str, file_size: int, 
              file_type: str, session_id: str = None) -> ProcessingJob:
    """Create a new processing job"""
    job = ProcessingJob(
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
        session_id=session_id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def update_job_status(db: Session, job_id: str, status: str, 
                     error_message: str = None, processing_time: float = None):
    """Update job status"""
    job = get_job_by_id(db, job_id)
    if job:
        job.status = status
        if error_message:
            job.error_message = error_message
        if processing_time:
            job.processing_time_seconds = processing_time
        if status == "completed":
            job.completed_at = datetime.utcnow()
        db.commit()

def save_processed_elements(db: Session, job_id: str, elements: List[Dict[str, Any]]):
    """Save processed elements to database"""
    for element_data in elements:
        element = ProcessedElement(
            job_id=job_id,
            element_type=element_data.get('type', 'unknown'),
            text_content=element_data.get('text', ''),
            metadata=element_data.get('metadata', {}),
            coordinates=element_data.get('coordinates'),
            element_index=element_data.get('element_index', 0)
        )
        db.add(element)
    db.commit()

def get_processed_elements(db: Session, job_id: str) -> List[ProcessedElement]:
    """Get processed elements for a job"""
    return db.query(ProcessedElement).filter(ProcessedElement.job_id == job_id).all()

def cleanup_old_sessions(db: Session, days_old: int = 30):
    """Clean up old sessions and their data"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    # Get old sessions
    old_sessions = db.query(UserSession).filter(
        UserSession.last_activity < cutoff_date
    ).all()
    
    for session in old_sessions:
        # Delete associated jobs and elements
        jobs = get_jobs_by_session(db, session.id)
        for job in jobs:
            db.query(ProcessedElement).filter(ProcessedElement.job_id == job.id).delete()
            db.delete(job)
        db.delete(session)
    
    db.commit()
