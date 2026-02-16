from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import os
import sys

# Import our modules
from database import get_db, init_db
from models import User, UserCV, Application
from auth import hash_password, verify_password, create_access_token, get_current_user_id

# Import agents
sys.path.append('/home/ubuntu/job-hunter-saas/backend/agents')
from job_hunter_agent import JobHunterAgent
from job_scraper_agent import JobScraperAgent
from interview_prep_agent import InterviewPrepAgent

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Job Hunter AI", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI agents
API_KEY = os.getenv("ANTHROPIC_API_KEY")
job_hunter = JobHunterAgent(API_KEY)
job_scraper = JobScraperAgent()

# Pydantic models for API
interview_prep = InterviewPrepAgent(API_KEY)
class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CVCreate(BaseModel):
    name: str
    content: str
    is_default: bool = False

class JobSearchRequest(BaseModel):
    filters: dict

class JobApplicationRequest(BaseModel):
    job_data: dict
    cv_id: Optional[str] = None

# ========== AUTH ENDPOINTS ==========

@app.post("/auth/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    """Sign up new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "subscription_tier": new_user.subscription_tier
        }
    }

@app.post("/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "subscription_tier": user.subscription_tier
        }
    }

@app.get("/auth/me")
def get_current_user(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get current user info"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "subscription_tier": user.subscription_tier,
        "applications_this_month": user.applications_this_month
    }

# ========== CV ENDPOINTS ==========

@app.post("/cvs")
def create_cv(cv: CVCreate, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Create new CV"""
    new_cv = UserCV(
        user_id=user_id,
        name=cv.name,
        content=cv.content,
        is_default=cv.is_default
    )
    db.add(new_cv)
    db.commit()
    db.refresh(new_cv)
    
    return {
        "id": new_cv.id,
        "name": new_cv.name,
        "is_default": new_cv.is_default,
        "created_at": new_cv.created_at
    }

@app.get("/cvs")
def get_cvs(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get all user CVs"""
    cvs = db.query(UserCV).filter(UserCV.user_id == user_id).all()
    return [
        {
            "id": cv.id,
            "name": cv.name,
            "content": cv.content,
            "is_default": cv.is_default,
            "created_at": cv.created_at
        }
        for cv in cvs
    ]

@app.get("/cvs/{cv_id}")
def get_cv(cv_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get specific CV"""
    cv = db.query(UserCV).filter(UserCV.id == cv_id, UserCV.user_id == user_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    
    return {
        "id": cv.id,
        "name": cv.name,
        "content": cv.content,
        "is_default": cv.is_default
    }

# ========== JOB SEARCH ENDPOINTS ==========

@app.post("/jobs/search")
async def search_jobs(request: JobSearchRequest, user_id: str = Depends(get_current_user_id)):
    """Search for jobs"""
    jobs = await job_scraper.search_jobs(request.filters)
    return {"jobs": jobs, "total": len(jobs)}

# ========== JOB APPLICATION ENDPOINTS ==========

@app.post("/jobs/apply")
async def apply_to_job(
    request: JobApplicationRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Apply to a job with AI-generated CV and cover letter"""
    
    # Get user's CV
    if request.cv_id:
        cv = db.query(UserCV).filter(UserCV.id == request.cv_id, UserCV.user_id == user_id).first()
    else:
        cv = db.query(UserCV).filter(UserCV.user_id == user_id, UserCV.is_default == True).first()
    
    if not cv:
        raise HTTPException(status_code=400, detail="No CV found. Please create one first.")
    
    # Check usage limits
    user = db.query(User).filter(User.id == user_id).first()
    if user.subscription_tier == "free" and user.applications_this_month >= 5:
        raise HTTPException(status_code=403, detail="Free tier limit reached (5 applications/month)")
    
    # Process application with AI
    result = await job_hunter.process_job_application(
        request.job_data,
        {"cv": cv.content}
    )
    
    # Save application to database
    application = Application(
        user_id=user_id,
        job_title=request.job_data.get("title"),
        company=request.job_data.get("company"),
        job_url=request.job_data.get("url"),
        job_source=request.job_data.get("source"),
        match_score=result.get("match", {}).get("match_score"),
        custom_cv=result.get("custom_cv"),
        cover_letter=result.get("cover_letter"),
        status="applied"
    )
    db.add(application)
    
    # Update usage count
    user.applications_this_month += 1
    
    db.commit()
    db.refresh(application)
    
    return {
        "application_id": application.id,
        "match": result.get("match"),
        "custom_cv": result.get("custom_cv"),
        "cover_letter": result.get("cover_letter"),
        "status": result.get("status")
    }

@app.get("/applications")
def get_applications(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get all user applications"""
    applications = db.query(Application).filter(Application.user_id == user_id).order_by(Application.applied_at.desc()).all()
    return [
        {
            "id": app.id,
            "job_title": app.job_title,
            "company": app.company,
            "job_url": app.job_url,
            "match_score": app.match_score,
            "status": app.status,
            "applied_at": app.applied_at
        }
        for app in applications
    ]

@app.get("/applications/{app_id}")
def get_application(app_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get specific application with CV and cover letter"""
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {
        "id": app.id,
        "job_title": app.job_title,
        "company": app.company,
        "job_url": app.job_url,
        "match_score": app.match_score,
        "custom_cv": app.custom_cv,
        "cover_letter": app.cover_letter,
        "status": app.status,
        "applied_at": app.applied_at
    }

# ========== ROOT ENDPOINT ==========

@app.get("/")
def root():
    return {
        "app": "Job Hunter AI",
        "version": "1.0.0",
        "status": "running"
    }

# Initialize database on startup

@app.post("/jobs/interview-prep")
async def get_interview_prep(request: dict, user_id: str = Depends(get_current_user_id)):
    job_data = request.get("job_data", {})
    result = await interview_prep.generate_interview_prep(job_data)
    return result

@app.delete("/applications/{app_id}")
async def delete_application(app_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id, Application.user_id == user_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(app)
    db.commit()
    return {"status": "deleted", "id": app_id}

@app.delete("/cvs/{cv_id}")
async def delete_cv(cv_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    cv = db.query(UserCV).filter(UserCV.id == cv_id, UserCV.user_id == user_id).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    db.delete(cv)
    db.commit()
    return {"status": "deleted", "id": cv_id}

@app.on_event("startup")
def startup_event():
    init_db()
    print("🚀 Job Hunter AI backend started!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
