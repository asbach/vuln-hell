"""
User routes.
A01: IDOR — any authenticated user can read/update/delete any other user's data.
A02: Full user record (SSN, credit card, API key) returned in API responses.
A01: No ownership checks on PUT/DELETE.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])
templates = Jinja2Templates(directory="app/templates")


def _token_from_request(request: Request) -> dict | None:
    token = request.cookies.get("token") or request.headers.get("Authorization", "").replace("Bearer ", "")
    return get_current_user(token) if token else None


@router.get("", response_class=JSONResponse)
async def list_users(request: Request, db=Depends(get_db)):
    """A01: No authentication required — full user list exposed."""
    rows = db.execute("SELECT id, username, email, role, ssn, credit_card, api_key FROM users").fetchall()
    return [dict(r) for r in rows]


@router.get("/{user_id}", response_class=JSONResponse)
async def get_user(user_id: int, request: Request, db=Depends(get_db)):
    """A01: IDOR — authenticated user can fetch any other user's full record."""
    current = _token_from_request(request)
    if not current:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    # A01: No check that current["user_id"] == user_id
    # A03: user_id is an integer here but the pattern mirrors injectable string params elsewhere
    row = db.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
    if not row:
        return JSONResponse(status_code=404, content={"error": "Not found"})
    return dict(row)


@router.get("/{user_id}/profile", response_class=HTMLResponse)
async def profile_page(user_id: int, request: Request, db=Depends(get_db)):
    """A01: IDOR on web profile page."""
    row = db.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
    if not row:
        return HTMLResponse("User not found", status_code=404)
    return templates.TemplateResponse("profile.html", {"request": request, "user": dict(row)})


@router.put("/{user_id}")
async def update_user(user_id: int, request: Request, db=Depends(get_db)):
    """
    A01: No ownership check.
    A04: Mass assignment — any field including 'role' can be updated.
    """
    current = _token_from_request(request)
    if not current:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    body = await request.json()
    # A04: Mass assignment — caller can set role='admin'
    for field, value in body.items():
        db.execute(
            f"UPDATE users SET {field} = '{value}' WHERE id = {user_id}"
        )
    db.commit()
    return {"message": "User updated"}


@router.delete("/{user_id}")
async def delete_user(user_id: int, request: Request, db=Depends(get_db)):
    """A01: Any authenticated user can delete any other user."""
    current = _token_from_request(request)
    if not current:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    db.execute(f"DELETE FROM users WHERE id = {user_id}")
    db.commit()
    return {"message": "User deleted"}


@router.get("/{user_id}/orders")
async def get_user_orders(user_id: int, request: Request, db=Depends(get_db)):
    """A01: IDOR — any user can view any other user's order history."""
    current = _token_from_request(request)
    if not current:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    rows = db.execute(f"SELECT * FROM orders WHERE user_id = {user_id}").fetchall()
    return [dict(r) for r in rows]
