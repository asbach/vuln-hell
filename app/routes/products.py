"""
Product routes.
A03: SQL Injection in search parameter.
A03: Stored XSS — description rendered unescaped in templates.
A03: Reflected XSS — search term echoed back without sanitisation.
"""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.security import get_current_user

router = APIRouter(tags=["products"])
templates = Jinja2Templates(directory="app/templates")


def _token_from_request(request: Request) -> dict | None:
    token = request.cookies.get("token") or request.headers.get("Authorization", "").replace("Bearer ", "")
    return get_current_user(token) if token else None


@router.get("/products", response_class=HTMLResponse)
async def products_page(request: Request, search: str = "", db=Depends(get_db)):
    # A03: SQL Injection — search param directly interpolated
    query = f"SELECT * FROM products WHERE name LIKE '%{search}%' OR description LIKE '%{search}%'"
    rows = db.execute(query).fetchall()
    return templates.TemplateResponse(
        "products.html",
        {
            "request": request,
            "products": [dict(r) for r in rows],
            "search": search,          # A03: reflected back unescaped in template
        },
    )


@router.get("/api/products")
async def list_products(search: str = "", category: str = "", db=Depends(get_db)):
    # A03: SQL Injection in both parameters
    query = (
        f"SELECT * FROM products WHERE "
        f"(name LIKE '%{search}%' OR description LIKE '%{search}%')"
        f" AND (category LIKE '%{category}%' OR '{category}' = '')"
    )
    rows = db.execute(query).fetchall()
    return [dict(r) for r in rows]


@router.get("/api/products/{product_id}")
async def get_product(product_id: int, db=Depends(get_db)):
    row = db.execute(f"SELECT * FROM products WHERE id = {product_id}").fetchone()
    if not row:
        return JSONResponse(status_code=404, content={"error": "Not found"})
    return dict(row)


@router.post("/api/products")
async def create_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),   # A03: stored XSS — no sanitisation
    price: float = Form(...),
    category: str = Form(""),
    db=Depends(get_db),
):
    current = _token_from_request(request)
    if not current:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    # A03: SQL Injection + stored XSS payload persisted
    db.execute(
        f"INSERT INTO products (name, description, price, owner_id, category) "
        f"VALUES ('{name}', '{description}', {price}, {current['user_id']}, '{category}')"
    )
    db.commit()
    return {"message": "Product created"}


@router.delete("/api/products/{product_id}")
async def delete_product(product_id: int, request: Request, db=Depends(get_db)):
    """A01: No ownership check — any user can delete any product."""
    current = _token_from_request(request)
    if not current:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    db.execute(f"DELETE FROM products WHERE id = {product_id}")
    db.commit()
    return {"message": "Deleted"}
