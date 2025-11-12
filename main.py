import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Product, Review, Order

app = FastAPI(title="Nanoplastia Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Nanoplastia Shop API Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, "name", "✅ Connected")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# -----------------------------
# Seed product endpoint (idempotent)
# -----------------------------
class SeedResponse(BaseModel):
    created: bool
    slug: str

@app.post("/api/seed", response_model=SeedResponse)
def seed_product():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    slug = "nanoplastia-pro"
    exists = db.product.find_one({"slug": slug})
    if exists:
        return {"created": False, "slug": slug}

    product = Product(
        title="Nanoplastia Pro Treatment",
        slug=slug,
        description=(
            "Trattamento lisciante e ricostruttivo avanzato a base di nanoparticelle. "
            "Riduce il crespo, dona lucentezza e rinforza la fibra capillare."
        ),
        price=79.90,
        in_stock=True,
        images=[
            "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?q=80&w=1200&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1512203492609-8f2f3b1c2b9d?q=80&w=1200&auto=format&fit=crop"
        ],
        benefits=[
            "Liscio setoso fino a 12 settimane",
            "Riduzione del crespo del 90%",
            "Formula senza formaldeide",
            "Adatto a tutti i tipi di capelli"
        ],
        ingredients="Aminoacidi, cheratina idrolizzata, complesso vitaminico, oli nutrienti",
        how_to_use=(
            "Lavare i capelli, applicare il prodotto su lunghezze e punte, asciugare e procedere con la piastra. "
            "Lasciare agire e risciacquare secondo indicazioni professionali."
        ),
    )

    create_document("product", product)
    return {"created": True, "slug": slug}

# -----------------------------
# Public endpoints
# -----------------------------
@app.get("/api/products")
def list_products():
    items = get_documents("product")
    # Normalize ObjectId
    for it in items:
        it["id"] = str(it.pop("_id", ""))
    return items

@app.get("/api/products/{slug}")
def get_product(slug: str):
    doc = db.product.find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    doc["id"] = str(doc.pop("_id", ""))
    return doc

@app.get("/api/reviews/{slug}")
def get_reviews(slug: str):
    reviews = get_documents("review", {"product_slug": slug})
    for r in reviews:
        r["id"] = str(r.pop("_id", ""))
    return reviews

@app.post("/api/reviews/{slug}")
def create_review(slug: str, review: Review):
    # Ensure product exists
    if not db.product.find_one({"slug": slug}):
        raise HTTPException(status_code=404, detail="Product not found")
    create_document("review", review)
    return {"ok": True}

# -----------------------------
# Checkout
# -----------------------------
@app.post("/api/checkout")
def checkout(order: Order):
    # Compute total server-side safety (also provided in payload)
    total = sum(item.quantity * item.unit_price for item in order.items)
    order.total_amount = total
    order_id = create_document("order", order)
    return {"order_id": order_id, "status": "received"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
