from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.profile.model import Profile
from app.profile.schemas import ProfileCreate, ProfileUpdate


def get_profile(
    db: Session,
    user: User,
) -> Profile | None:

    return db.scalar(
        select(Profile).where(Profile.user_id == user.id)
    )


def create_profile(
    db: Session,
    user: User,
    profile_data: ProfileCreate,
) -> Profile:

    existing_profile = get_profile(db, user)

    if existing_profile:
        raise ValueError("Profile already exists")

    profile_dict = profile_data.model_dump()

    profile = Profile(
        user_id=user.id,
        phone=profile_dict["phone"],
        location=profile_dict["location"],
        college=profile_dict["college"],
        degree=profile_dict["degree"],
        graduation_year=profile_dict["graduation_year"],
        skills=profile_dict["skills"],
        bio=profile_dict["bio"],
        github_url=str(profile_dict["github_url"]) if profile_dict["github_url"] else None,
        linkedin_url=str(profile_dict["linkedin_url"]) if profile_dict["linkedin_url"] else None,
        portfolio_url=str(profile_dict["portfolio_url"]) if profile_dict["portfolio_url"] else None,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile

def update_profile(
    db: Session,
    user: User,
    profile_data: ProfileUpdate,
) -> Profile | None:

    profile = get_profile(db, user)

    if not profile:
        return None

    profile_dict = profile_data.model_dump()

    profile.phone = profile_dict["phone"]
    profile.location = profile_dict["location"]
    profile.college = profile_dict["college"]
    profile.degree = profile_dict["degree"]
    profile.graduation_year = profile_dict["graduation_year"]
    profile.skills = profile_dict["skills"]
    profile.bio = profile_dict["bio"]

    profile.github_url = (
        str(profile_dict["github_url"])
        if profile_dict["github_url"]
        else None
    )

    profile.linkedin_url = (
        str(profile_dict["linkedin_url"])
        if profile_dict["linkedin_url"]
        else None
    )

    profile.portfolio_url = (
        str(profile_dict["portfolio_url"])
        if profile_dict["portfolio_url"]
        else None
    )

    db.commit()
    db.refresh(profile)

    return profile