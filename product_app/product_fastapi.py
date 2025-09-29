from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db_config import session , engine, get_db
from model import Product
from default_data import products
import db_model

router = APIRouter()(prefix="/products", tags=["products"])

db_model.Base.metadata.create_all(bind=engine)  # Create Table structure

def init_db():                                  # Create Default Data
    conn = session()
    count = conn.query(db_model.Product).count()
    if count == 0:
        for product in products:
            conn.add(db_model.Product(**product.model_dump()))
    conn.commit()

init_db()

@router.get("/")
def greet():
    return "Welcome to Python"

@router.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(db_model.Product).all()
    return products

@router.get("/products/{id}")
def get_product_by_id(id : int, db: Session = Depends(get_db)):
    product = db.query(db_model.Product).filter(db_model.Product.id == id).first()
    if product:
        return product
    else:
        return "Product not found!!"
        
@router.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db.add(db_model.Product(**product.model_dump()))
    db.commit()
    return product


@router.put("/products/{id}")
def update_product(id: int, updated_product: Product, db: Session = Depends(get_db)):
    product = db.query(db_model.Product).filter(db_model.Product.id == id).first()
    if product:
        product.id = updated_product.id
        product.name = updated_product.name
        product.description = updated_product.description
        product.price = updated_product.price
        product.quantity = updated_product.quantity
        db.commit()
        return "Product Updated Successfully!!"
    else:    
        return {"error": "Product not found!!"}

@router.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(db_model.Product).filter(db_model.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product deleted successfully!!"
    else:
        return "Product not found!!"