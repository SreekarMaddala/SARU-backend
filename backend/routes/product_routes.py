from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.product import Product
from backend.auth import get_current_company

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[dict])
def list_products(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    products = db.query(Product).filter(Product.company_id == current_company.id).all()
    return [{"id": p.id, "name": p.name, "description": p.description} for p in products]


@router.post("/", response_model=dict)
def create_product(payload: dict, db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    name = payload.get("name")
    description = payload.get("description")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    product = Product(name=name, description=description, company_id=current_company.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"id": product.id, "name": product.name, "description": product.description}


