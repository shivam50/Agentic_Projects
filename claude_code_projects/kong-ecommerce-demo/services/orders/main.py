from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/orders_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    items = Column(JSON, nullable=False)   # [{product_id, name, price, quantity}]
    total = Column(Float, nullable=False)
    status = Column(String, default="pending")   # pending | processing | shipped | delivered
    shipping_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orders Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic schemas ──────────────────────────────────────────

class OrderItem(BaseModel):
    product_id: int
    name: str
    price: float
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItem]
    shipping_address: Optional[str] = None


class OrderOut(BaseModel):
    id: int
    user_id: str
    items: List[dict]
    total: float
    status: str
    shipping_address: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── DB dependency ─────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_id(
    x_consumer_username: Optional[str] = Header(None),   # injected by Kong OIDC
    x_user_id: Optional[str] = Header(None),             # custom header fallback
) -> str:
    """Resolve caller identity from Kong-injected headers."""
    return x_consumer_username or x_user_id or "anonymous"


# ── Routes ────────────────────────────────────────────────────

@app.get("/api/orders", response_model=List[OrderOut])
def list_orders(user_id: str = Depends(get_user_id), db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()


@app.get("/api/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/api/orders", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderCreate,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    total = sum(item.price * item.quantity for item in payload.items)
    order = Order(
        user_id=user_id,
        items=[item.model_dump() for item in payload.items],
        total=total,
        shipping_address=payload.shipping_address,
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@app.patch("/api/orders/{order_id}/status", response_model=OrderOut)
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    allowed = {"pending", "processing", "shipped", "delivered", "cancelled"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed}")
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    db.refresh(order)
    return order


@app.get("/health")
def health():
    return {"status": "ok", "service": "orders"}
