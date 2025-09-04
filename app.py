"""
Production FastAPI application with database integration
"""
import os
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

from database import (
    get_db, create_tables, ProcessingJob, ProcessedElement, UserSession,
    create_job, update_job_status, save_processed_elements, get_processed_elements,
    get_job_by_id, get_jobs_by_session, cleanup_old_sessions
)
from dataset_processor import process_single_file_from_path

# Initialize FastAPI app
app = FastAPI(
    title="Dataset Processor API",
    description="Production API for document processing with Unstructured",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/exports", StaticFiles(directory="exports"), name="exports")

@app.on_event("startup")
async def startup_event():
    """Initialize database and cleanup old data"""
    create_tables()
    # Clean up sessions older than 30 days
    db = next(get_db())
    cleanup_old_sessions(db, days_old=30)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Dataset Processor API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "process": "/process",
            "jobs": "/jobs",
            "job": "/job/{job_id}",
            "elements": "/job/{job_id}/elements",
            "export": "/job/{job_id}/export"
        }
    }

@app.post("/process")
async def process_document(
    file_path: str,
    session_id: str = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Process a document and return job information"""
    
    # Validate file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get file information
    file_info = Path(file_path)
    file_size = file_info.stat().st_size
    file_type = file_info.suffix.lower()
    
    # Create processing job
    job = create_job(
        db=db,
        filename=file_info.name,
        file_path=str(file_path),
        file_size=file_size,
        file_type=file_type,
        session_id=session_id
    )
    
    # Start background processing
    if background_tasks:
        background_tasks.add_task(process_document_background, str(job.id), file_path)
    
    return {
        "job_id": str(job.id),
        "status": "processing",
        "message": "Document processing started",
        "filename": job.filename,
        "file_size": job.file_size,
        "file_type": job.file_type
    }

async def process_document_background(job_id: str, file_path: str):
    """Background task to process document"""
    db = next(get_db())
    start_time = time.time()
    
    try:
        # Update status to processing
        update_job_status(db, job_id, "processing")
        
        # Process the document
        result = await process_single_file_from_path(file_path)
        
        if result['success']:
            # Save processed elements
            save_processed_elements(db, job_id, result['elements'])
            
            # Update job with results
            job = get_job_by_id(db, job_id)
            if job:
                job.word_count = result['word_count']
                job.element_count = result['element_count']
                job.total_elements_found = result['total_elements_found']
                job.processed_count = result['processed_count']
                job.skipped_count = result['skipped_count']
                job.export_paths = result.get('export_paths', [])
                db.commit()
            
            # Update status to completed
            processing_time = time.time() - start_time
            update_job_status(db, job_id, "completed", processing_time=processing_time)
            
        else:
            # Update status to failed
            update_job_status(db, job_id, "failed", error_message="Processing failed")
            
    except Exception as e:
        # Update status to failed with error message
        update_job_status(db, job_id, "failed", error_message=str(e))
        print(f"Error processing job {job_id}: {e}")

@app.get("/jobs")
async def get_jobs(session_id: str = None, db: Session = Depends(get_db)):
    """Get all processing jobs, optionally filtered by session"""
    if session_id:
        jobs = get_jobs_by_session(db, session_id)
    else:
        jobs = db.query(ProcessingJob).order_by(ProcessingJob.created_at.desc()).limit(100).all()
    
    return [job.to_dict() for job in jobs]

@app.get("/job/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get specific job details"""
    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job.to_dict()

@app.get("/job/{job_id}/elements")
async def get_job_elements(job_id: str, db: Session = Depends(get_db)):
    """Get processed elements for a job"""
    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    elements = get_processed_elements(db, job_id)
    return [element.to_dict() for element in elements]

@app.get("/job/{job_id}/export")
async def export_job_data(job_id: str, format: str = "json", db: Session = Depends(get_db)):
    """Export job data in various formats"""
    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    elements = get_processed_elements(db, job_id)
    
    if format == "json":
        # Export as JSON
        export_data = {
            "job": job.to_dict(),
            "elements": [element.to_dict() for element in elements]
        }
        
        export_path = f"exports/job_{job_id}_export.json"
        os.makedirs("exports", exist_ok=True)
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return FileResponse(export_path, filename=f"job_{job_id}_export.json")
    
    elif format == "csv":
        # Export as CSV
        import pandas as pd
        
        data = []
        for element in elements:
            data.append({
                "element_type": element.element_type,
                "text_content": element.text_content,
                "element_index": element.element_index,
                "created_at": element.created_at
            })
        
        df = pd.DataFrame(data)
        export_path = f"exports/job_{job_id}_export.csv"
        os.makedirs("exports", exist_ok=True)
        
        df.to_csv(export_path, index=False)
        return FileResponse(export_path, filename=f"job_{job_id}_export.csv")
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get processing statistics"""
    total_jobs = db.query(ProcessingJob).count()
    completed_jobs = db.query(ProcessingJob).filter(ProcessingJob.status == "completed").count()
    failed_jobs = db.query(ProcessingJob).filter(ProcessingJob.status == "failed").count()
    processing_jobs = db.query(ProcessingJob).filter(ProcessingJob.status == "processing").count()
    
    # Get recent activity (last 24 hours)
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    recent_jobs = db.query(ProcessingJob).filter(
        ProcessingJob.created_at >= recent_cutoff
    ).count()
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "processing_jobs": processing_jobs,
        "recent_jobs_24h": recent_jobs,
        "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
