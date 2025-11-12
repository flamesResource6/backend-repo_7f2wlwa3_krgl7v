"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Core user example (kept for reference)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

# Ecommerce: Single flagship product (Nanoplastia)
class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product"
    """
    title: str = Field(..., description="Product title")
    slug: str = Field(..., description="URL-friendly identifier")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in euros")
    in_stock: bool = Field(True, description="Whether product is in stock")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    benefits: List[str] = Field(default_factory=list, description="Key benefits list")
    ingredients: Optional[str] = Field(None, description="Ingredients overview")
    how_to_use: Optional[str] = Field(None, description="How to use instructions")
    rating_average: float = Field(0.0, ge=0, le=5, description="Average rating")
    rating_count: int = Field(0, ge=0, description="Number of ratings")

class Review(BaseModel):
    """Product reviews collection
    Collection name: "review"
    """
    product_slug: str = Field(..., description="Related product slug")
    name: str = Field(..., description="Reviewer name")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    comment: Optional[str] = Field(None, description="Text review")

class OrderItem(BaseModel):
    product_slug: str
    quantity: int = Field(..., ge=1, le=10)
    unit_price: float = Field(..., ge=0)

class Order(BaseModel):
    """Orders collection
    Collection name: "order"
    """
    customer_name: str
    customer_email: EmailStr
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    postal_code: str
    country: str
    phone: Optional[str] = None
    notes: Optional[str] = None
    items: List[OrderItem]
    total_amount: float = Field(..., ge=0)
    status: str = Field("pending", description="pending, paid, shipped, cancelled")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
