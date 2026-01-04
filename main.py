from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.services.nppes import lookup_npi
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

@app.get("/")
def health_check():
    return {"status": "online", "system": "CredentialGuard Revenue Engine"}

@app.get("/api/v1/providers/lookup/{npi}")
async def get_provider(npi: str):
    """
    Lookup provider credentials from CMS NPPES Registry.
    
    Args:
        npi: 10-digit National Provider Identifier
        
    Returns:
        Provider data including name, credentials, and risk status
    """
    if not npi or len(npi) != 10 or not npi.isdigit():
        return {"error": "Invalid NPI format. Must be 10 digits."}
    
    try:
        provider_data = await lookup_npi(npi)
        return provider_data
    except Exception as e:
        return {"error": str(e), "npi": npi}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
