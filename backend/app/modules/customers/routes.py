from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from backend.app.core.security import get_current_company
from backend.app.db.session import get_db
from backend.app.modules.analytics import service as analytics_service
from backend.app.modules.customers.schema import CustomerProfileResponse

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/{customer_id}/profile", response_model=CustomerProfileResponse)
def get_customer_profile(
    customer_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_company=Depends(get_current_company),
):
    profile = analytics_service.customer_profile_service(db, current_company.id, customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Customer not found")
    return profile
