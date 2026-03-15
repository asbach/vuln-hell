"""
Main application entry point.
A05: Debug mode enabled, CORS wildcard, stack traces exposed.
A05: No rate limiting anywhere.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routes import admin, auth, products, users, utils

# A05: debug=True leaks internal details in error responses
app = FastAPI(
    title="VulnShop API",
    description="Vulnerable demo app — DO NOT deploy in production",
    debug=True,
)

templates = Jinja2Templates(directory="app/templates")

# A05: CORS wildcard — any origin may read responses including credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(admin.router)
app.include_router(utils.router)


@app.on_event("startup")
def startup():
    init_db()


# A05: Unhandled exceptions return full stack trace to client
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "traceback": traceback.format_exc()},
    )


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
