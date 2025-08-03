"""
SKYCODE.NO HOSTING DASHBOARD - FastAPI Backend

# LOCK INSTRUCTIONS:
# - Listen ONLY on port 8098.
# - Serve all APIs under /api/v1 path.
# - Allow CORS ONLY for origin https://cp.skycode.no.
# - Restrict all file access to /home/skycode.no/public_html/cp/.
# - ALL responses MUST be JSON.
# - Use central config.py constants ONLY for ports and paths.
# - Enforce locking and backup on all system-modifying endpoints.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import config

app = FastAPI(openapi_prefix="/api/v1")

# LOCK: CORS only allows origin cp.skycode.no
origins = [config.ALLOWED_ORIGIN]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def enforce_rules(request: Request, call_next):
    # LOCK: Reject requests NOT on port 8098 or wrong host
    if request.url.port != config.API_PORT:
        return JSONResponse({"error": f"Invalid port. Must use port {config.API_PORT}"}, status_code=400)
    if request.headers.get("host") != "cp.skycode.no":
        return JSONResponse({"error": "Invalid Host header."}, status_code=400)
    response = await call_next(request)
    if "application/json" not in response.headers.get("content-type", ""):
        # Override non-json response
        return JSONResponse({"error": "Response must be JSON only."}, status_code=500)
    return response

# Further route implementations with LOCK comments...

if __name__ == "__main__":
    import uvicorn
    # LOCK: Use port 8098 ONLY
    uvicorn.run("main:app", host="127.0.0.1", port=config.API_PORT)
