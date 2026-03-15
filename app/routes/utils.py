"""
Utility / debug routes.
A10: SSRF — arbitrary URL fetch with no allowlist.
A03: Command Injection via os.popen / subprocess shell=True.
A01: Path Traversal — arbitrary file read.
A08: Unsafe deserialization via pickle.
A03: SSTI — user input rendered as a Jinja2 template.
A05: Debug endpoint exposing environment variables.

Bandit-specific findings:
  B301/B403 — pickle import + pickle.loads
  B302/B324 — MD5 via hashlib (in security.py)
  B307      — eval() on user input
  B506      — yaml.unsafe_load()
  B501      — requests with verify=False (SSL cert ignored)
  B602      — subprocess.Popen with shell=True
  B605      — os.popen (start_process_with_a_shell)
  B701      — Jinja2 Template() with no autoescape (SSTI)
  B104      — hardcoded bind-all address 0.0.0.0
"""
import base64
import os
import pickle  # B403
import subprocess  # B404
import ssl
import yaml  # B506

from jinja2 import Template  # B701

import requests
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.database import get_db

router = APIRouter(prefix="/api/utils", tags=["utils"])


@router.post("/ping")
async def ping_host(host: str):
    """A03: Command Injection — host is passed directly to the shell."""
    # e.g. host = "8.8.8.8; cat /etc/passwd"
    result = os.popen(f"ping -c 1 {host}").read()  # noqa: S605
    return {"result": result}


@router.post("/fetch")
async def fetch_url(url: str):
    """
    A10: SSRF — no scheme/host validation.
    Can be used to probe internal services: http://169.254.169.254/latest/meta-data/
    """
    try:
        resp = requests.get(url, timeout=10)  # noqa: S113
        return {"status_code": resp.status_code, "content": resp.text[:5000]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/file")
async def read_file(filename: str):
    """A01/Path Traversal — filename not sanitised, allows ../../etc/passwd."""
    try:
        with open(f"files/{filename}") as f:   # noqa: S603
            return {"content": f.read()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/deserialize")
async def deserialize_data(data: str):
    """
    A08: Unsafe deserialization — base64-encoded pickle payload executed directly.
    Allows Remote Code Execution.
    """
    try:
        obj = pickle.loads(base64.b64decode(data))  # noqa: S301
        return {"result": str(obj)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/render")
async def render_template(template: str):
    """A03: SSTI — user-supplied string rendered as a live Jinja2 template."""
    # e.g. template = "{{ 7*7 }}" or "{{ ''.__class__.__mro__[1].__subclasses__() }}"
    t = Template(template)
    return {"rendered": t.render()}


@router.get("/env")
async def dump_env():
    """A05: Security misconfiguration — full environment dumped to any caller."""
    return dict(os.environ)


@router.post("/redirect")
async def open_redirect(url: str):
    """A01: Open redirect — destination URL not validated."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=url, status_code=302)


@router.post("/exec")
async def exec_code(code: str):
    """
    A03: B307 — eval() on user-supplied input allows arbitrary Python execution.
    e.g. code = "__import__('os').system('id')"
    """
    result = eval(code)  # noqa: S307  # B307
    return {"result": str(result)}


@router.post("/shell")
async def run_shell(command: str):
    """
    A03: B602 — subprocess.Popen with shell=True, user-controlled command string.
    Distinct from os.popen; Bandit flags this as a separate finding (B602).
    """
    proc = subprocess.Popen(  # noqa: S602  # B602
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate(timeout=5)
    return {"stdout": stdout.decode(), "stderr": stderr.decode()}


@router.post("/parse-yaml")
async def parse_yaml(content: str):
    """
    A08: B506 — yaml.load() without a safe Loader.
    Allows arbitrary Python object construction (RCE via PyYAML).
    e.g. content = "!!python/object/apply:os.system ['id']"
    """
    data = yaml.load(content, Loader=yaml.Loader)  # noqa: S506  # B506
    return {"parsed": str(data)}


@router.get("/fetch-ssl-insecure")
async def fetch_ssl_insecure(url: str):
    """
    A02: B501 — SSL certificate verification disabled.
    Enables MITM attacks against outbound requests.
    """
    resp = requests.get(url, verify=False, timeout=10)  # noqa: S501  # B501
    return {"status_code": resp.status_code, "content": resp.text[:2000]}
