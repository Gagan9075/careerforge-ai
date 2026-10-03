from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.resume.extractor import extract_resume_text
from app.resume.model import Resume
from app.resume.parser import parse_resume_text


router = APIRouter(prefix="/api/resume", tags=["Resume Upload"])

UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Validate file extension
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported",
        )

    # 2. Read and validate file size
    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must be 5 MB or less",
        )

    # 3. Generate unique filename
    filename = f"{current_user.id}_{uuid4()}{extension}"

    file_path = UPLOAD_DIR / filename

    # 4. Save uploaded file
    file_path.write_bytes(file_content)

    # 5. Extract text from the uploaded resume
    try:
        extracted_text = extract_resume_text(file_path)
    except Exception as exc:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail=f"Could not extract resume text: {str(exc)}",
        )

    # 6. Parse resume sections
    parsed_resume = parse_resume_text(extracted_text)

    # 7. Check whether the user already has a resume
    existing_resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .first()
    )

    if existing_resume:
        # Update existing resume
        existing_resume.title = (
            parsed_resume["header"].splitlines()[0]
            if parsed_resume["header"]
            else "Uploaded Resume"
        )

        existing_resume.name = parsed_resume["name"]
        existing_resume.email = parsed_resume["email"]
        existing_resume.phone = parsed_resume["phone"]
        existing_resume.location = parsed_resume["location"]

        existing_resume.summary = parsed_resume["summary"]
        existing_resume.skills = parsed_resume["skills"]
        existing_resume.experience = parsed_resume["experience"]
        existing_resume.education = parsed_resume["education"]
        existing_resume.projects = parsed_resume["projects"]
        existing_resume.certifications = parsed_resume["certifications"]

        resume = existing_resume

    else:
        # Create new resume
        resume = Resume(
            user_id=current_user.id,
            title=(
                parsed_resume["header"].splitlines()[0]
                if parsed_resume["header"]
                else "Uploaded Resume"
            ),
            name=parsed_resume["name"],
            email=parsed_resume["email"],
            phone=parsed_resume["phone"],
            location=parsed_resume["location"],
            summary=parsed_resume["summary"],
            skills=parsed_resume["skills"],
            experience=parsed_resume["experience"],
            education=parsed_resume["education"],
            projects=parsed_resume["projects"],
            certifications=parsed_resume["certifications"],
        )

        db.add(resume)

    # 8. Save changes
    db.commit()
    db.refresh(resume)

    return {
        "message": "Resume uploaded and parsed successfully",
        "resume_id": str(resume.id),
        "filename": filename,
        "original_filename": file.filename,
        "user_id": str(current_user.id),
        "parsed_sections": {
            "summary": bool(parsed_resume["summary"]),
            "skills": bool(parsed_resume["skills"]),
            "experience": bool(parsed_resume["experience"]),
            "education": bool(parsed_resume["education"]),
            "projects": bool(parsed_resume["projects"]),
            "certifications": bool(parsed_resume["certifications"]),
        },
    }