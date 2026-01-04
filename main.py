from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.nppes import lookup_npi
import uvicorn
import os

app = FastAPI(title="CredentialGuard API", version="1.0.0")

# SECURITY: CORS Configuration - Dynamic for Development and Production
# Define allowed origins
origins = [
    "http://localhost:5173",      # Vite Local
    "http://localhost:3000",      # React Local
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://credentialguard.vercel.app",  # Replace with your actual Vercel/Netlify domain
    "https://3000-ipahdds43nead0dqlwouk-445dfc90.us2.manus.computer",  # Manus Frontend
    os.getenv("FRONTEND_URL"),     # Dynamic Production URL from environment variable
]

# Filter out None values in case environment variable isn't set
origins = [origin for origin in origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GLOBAL EXCEPTION HANDLERS - Ensure CORS headers on ALL error responses
# This fixes the "Failed to fetch" error on 404s and 500s
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": True},
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}", "error": True},
        headers={"Access-Control-Allow-Origin": "*"}
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
