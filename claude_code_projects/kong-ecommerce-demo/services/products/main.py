from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/products_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Products Service", version="1.0.0", root_path="")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic schemas ──────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    category: Optional[str] = None
    image_url: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: Optional[str]
    image_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── DB dependency ─────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Seed data ─────────────────────────────────────────────────

SEED_PRODUCTS = [
    dict(name="Wireless Headphones", description="Premium noise-cancelling headphones", price=149.99, stock=50, category="Electronics", image_url="https://placehold.co/400x300/1a1a2e/white?text=Headphones"),
    dict(name="Mechanical Keyboard", description="RGB mechanical keyboard with Cherry MX switches", price=89.99, stock=30, category="Electronics", image_url="https://placehold.co/400x300/16213e/white?text=Keyboard"),
    dict(name="Smart Watch", description="Fitness tracker with heart rate monitor and GPS", price=199.99, stock=40, category="Electronics", image_url="https://placehold.co/400x300/0f3460/white?text=Smart+Watch"),
    dict(name="Running Shoes", description="Lightweight running shoes for all terrains", price=79.99, stock=100, category="Sports", image_url="https://placehold.co/400x300/533483/white?text=Shoes"),
    dict(name="Yoga Mat", description="Non-slip premium yoga mat, 6mm thick", price=35.99, stock=75, category="Sports", image_url="https://placehold.co/400x300/2b2d42/white?text=Yoga+Mat"),
    dict(name="Water Bottle", description="Insulated stainless steel bottle, 32oz", price=29.99, stock=120, category="Sports", image_url="https://placehold.co/400x300/8d99ae/white?text=Water+Bottle"),
    dict(name="Coffee Maker", description="12-cup programmable coffee maker with thermal carafe", price=59.99, stock=25, category="Home", image_url="https://placehold.co/400x300/2d6a4f/white?text=Coffee+Maker"),
    dict(name="Air Purifier", description="HEPA air purifier, covers up to 500 sq ft", price=129.99, stock=20, category="Home", image_url="https://placehold.co/400x300/1b4332/white?text=Air+Purifier"),
]


@app.on_event("startup")
async def startup():
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            db.add_all([Product(**p) for p in SEED_PRODUCTS])
            db.commit()
    finally:
        db.close()


# ── Routes ────────────────────────────────────────────────────

@app.get("/api/products", response_model=List[ProductOut])
def list_products(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Product)
    if category:
        q = q.filter(Product.category == category)
    return q.offset(skip).limit(limit).all()


@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/api/products", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/health")
def health():
    return {"status": "ok", "service": "products"}
