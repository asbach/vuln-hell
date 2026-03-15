"""
Admin routes.
A01: Broken access control — role check is client-controlled via JWT payload.
A01: Function-level access control missing on several sub-routes.
A05: Admin panel reachable via predictable URL with no additional factor.
"""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.security import get_current_user, hash_password

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


def _require_admin(request: Request) -> dict:
    """
    A01: Role is read directly from the (attacker-controllable) JWT payload.
    Because the JWT secret is weak ('secret123') and alg:none is accepted,
    an attacker can forge an admin token trivially.
    """
    token = request.cookies.get("token") or request.headers.get("Authorization", "").replace("Bearer ", "")
    user = get_current_user(token) if token else None
    if not user:
        raise PermissionError("Not authenticated")
    # A01: Trusting the 'role' claim in a client-supplied, weakly-signed JWT
    if user.get("role") != "admin":
        raise PermissionError("Admin only")
    return user


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db=Depends(get_db)):
    try:
        _require_admin(request)
    except PermissionError as e:
        return HTMLResponse(str(e), status_code=403)

    users    = db.execute("SELECT * FROM users").fetchall()
    products = db.execute("SELECT * FROM products").fetchall()
    logs     = db.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 50").fetchall()
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "users": [dict(u) for u in users],
            "products": [dict(p) for p in products],
            "logs": [dict(l) for l in logs],
        },
    )


@router.get("/users")
async def admin_list_users(request: Request, db=Depends(get_db)):
    # A01: No auth check on this sub-route at all
    rows = db.execute("SELECT * FROM users").fetchall()
    return [dict(r) for r in rows]


@router.post("/users/{user_id}/reset-password")
async def admin_reset_password(
    user_id: int,
    new_password: str = Form(...),
    db=Depends(get_db),
):
    # A01: No auth check — anyone can reset any user's password
    hashed = hash_password(new_password)
    db.execute(f"UPDATE users SET password='{hashed}' WHERE id={user_id}")
    db.commit()
    return {"message": "Password reset"}


@router.delete("/users/{user_id}")
async def admin_delete_user(user_id: int, request: Request, db=Depends(get_db)):
    # A01: No auth check
    db.execute(f"DELETE FROM users WHERE id={user_id}")
    db.commit()
    return {"message": "User deleted"}


@router.get("/logs")
async def admin_logs(request: Request, db=Depends(get_db)):
    # A09: Audit log entries contain plaintext passwords — exposed here
    # A01: No auth check
    rows = db.execute("SELECT * FROM audit_logs ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]
