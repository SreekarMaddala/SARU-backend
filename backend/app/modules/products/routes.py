from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.modules.products.model import Product
from backend.app.modules.products.schema import ProductCreate, ProductRead, ProductUpdate
from backend.app.modules.products.service import (
    get_products_by_company,
    create_product,
    get_product_by_company_and_id,
)
from backend.app.core.security import get_current_company

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    products = get_products_by_company(db, current_company.id)
    return products


@router.post("/", response_model=ProductRead)
def create_product_route(payload: ProductCreate, db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    if not payload.name:
        raise HTTPException(status_code=400, detail="name is required")
    existing = db.query(Product).filter(
        Product.company_id == current_company.id,
        Product.model_number == payload.model_number,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Model number already exists")
    product = create_product(db, payload, current_company.id)
    return product


@router.put("/{product_id}/", response_model=ProductRead)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    product = get_product_by_company_and_id(db, current_company.id, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if payload.name is not None:
        product.name = payload.name
    if payload.description is not None:
        product.description = payload.description
    if payload.model_number is not None:
        product.model_number = payload.model_number

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}/")
def delete_product(product_id: int, db: Session = Depends(get_db), current_company=Depends(get_current_company)):
    product = get_product_by_company_and_id(db, current_company.id, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

