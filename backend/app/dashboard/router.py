from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User

from app.dashboard.schemas import DashboardResponse
from app.dashboard.service import DashboardService


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("/me", response_model=DashboardResponse)
def get_my_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = DashboardService()

    return service.get_dashboard_data(
        user=current_user,
        db=db,
    )