from sqlalchemy.orm import Session
from backend.app.modules.products.model import Product
from backend.app.modules.products.schema import ProductCreate


def get_products_by_company(db: Session, company_id: int):
    return db.query(Product).filter(Product.company_id == company_id).all()


def create_product(db: Session, product: ProductCreate, company_id: int):
    db_product = Product(**product.model_dump(), company_id=company_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_product_by_id(db: Session, product_id: int, company_id: int):
    return db.query(Product).filter(Product.id == product_id, Product.company_id == company_id).first()

