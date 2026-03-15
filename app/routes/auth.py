"""
Authentication routes.
A07: No account lockout, no MFA, weak password policy.
A02: Passwords hashed with MD5 (no salt).
A09: Failed/successful logins not properly logged; passwords appear in audit log.
A04: No rate limiting on login endpoint.
"""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.security import create_token, hash_password, verify_password

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db=Depends(get_db),
):
    # A03: SQL Injection via string concatenation
    query = f"SELECT * FROM users WHERE username = '{username}'"
    user = db.execute(query).fetchone()

    if not user or not verify_password(password, user["password"]):
        # A09: No logging of failed auth attempts
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid credentials"}
        )

    # A09: Password logged in plaintext to audit log
    db.execute(
        "INSERT INTO audit_logs (action, user_id, timestamp, details) VALUES (?,?,datetime('now'),?)",
        ("login", user["id"], f"User {username} logged in with password={password}"),
    )
    db.commit()

    token = create_token(user["id"], user["username"], user["role"])
    response = RedirectResponse(url="/", status_code=302)
    # A07: Token stored in a non-HttpOnly cookie
    response.set_cookie("token", token, httponly=False, secure=False, samesite="none")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),  # A07: no minimum length enforced
    email: str = Form(""),
    role: str = Form("user"),   # A04: mass assignment — caller sets their own role
    db=Depends(get_db),
):
    hashed = hash_password(password)
    try:
        # A03: SQL Injection in INSERT
        db.execute(
            f"INSERT INTO users (username, password, email, role) "
            f"VALUES ('{username}', '{hashed}', '{email}', '{role}')"
        )
        db.commit()
    except Exception as e:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": str(e)}
        )

    return RedirectResponse(url="/login", status_code=302)


@router.post("/api/reset-password")
async def reset_password(
    username: str = Form(...),
    new_password: str = Form(...),  # A04: no token/email verification
    db=Depends(get_db),
):
    """A04: Password reset requires only the username — no email/token challenge."""
    hashed = hash_password(new_password)
    db.execute(
        f"UPDATE users SET password='{hashed}' WHERE username='{username}'"
    )
    db.commit()
    return {"message": "Password reset successful"}


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("token")
    return response


# ── REST login (returns JWT) ──────────────────────────────────────────────────

@router.post("/api/login")
async def api_login(username: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    # A03: SQL Injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hash_password(password)}'"
    user = db.execute(query).fetchone()
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid credentials"})

    token = create_token(user["id"], user["username"], user["role"])
    # A07: Token also returned as query-param-friendly value (ends up in logs)
    return {"access_token": token, "token_type": "bearer", "user_id": user["id"]}
