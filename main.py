from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.base import BaseHTTPMiddleware
from services.nppes import lookup_npi
import uvicorn
import os

app = FastAPI(title="CredentialGuard API", version="1.0.0")

# Custom middleware to force CORS headers on ALL responses
class CORSMiddlewareForce(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Handle preflight requests
        if request.method == "OPTIONS":
            return JSONResponse(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Access-Control-Max-Age": "600",
                }
            )
        
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Expose-Headers"] = "*"
        return response

# Add custom CORS middleware FIRST (before everything else)
app.add_middleware(CORSMiddlewareForce)

# Also add standard CORS middleware for OPTIONS requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# GLOBAL EXCEPTION HANDLERS - Ensure CORS headers on ALL error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": True},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}", "error": True},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )

@app.get("/")
def health_check():
    return {"status": "online", "system": "CredentialGuard Revenue Engine"}

@app.get("/api/v1/providers/lookup/{npi}")
async def get_provider(npi: str):
    """
    Lookup provider credentials from CMS NPPES Registry.
    Always returns 200 OK. Check the error flag in response.
    """
    if not npi or len(npi) != 10 or not npi.isdigit():
        return {
            "error": True,
            "detail": "Invalid NPI format. Must be 10 digits.",
            "npi": npi
        }
    
    try:
        provider_data = await lookup_npi(npi)
        return provider_data
    except Exception as e:
        return {
            "error": True,
            "detail": f"Error looking up NPI: {str(e)}",
            "npi": npi
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
