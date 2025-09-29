from fastapi import FastAPI
from auth import router as auth_router
from product_apiroute import router as products_router

app = FastAPI(title="My FastAPI App")

# Optional root endpoint
@app.get("/", tags=["Test"])
def read_root():
    return {"msg": "Welcome to the API"}

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(products_router, prefix="/products", tags=["products"])

# Run with:
# uvicorn main:app --reload
