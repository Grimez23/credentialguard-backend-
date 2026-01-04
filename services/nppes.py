import httpx

async def lookup_npi(npi_number: str):
    """
    Queries the CMS NPPES Registry API for provider data.
    """
    # Official CMS NPI Registry API endpoint
    url = "https://npiregistry.cms.hhs.gov/api/"
    params = {
        'number': npi_number,
        'version': '2.1'
    }
    
    # Use HTTPX for high-performance async networking
    async with httpx.AsyncClient() as client:
        try:
            # 10-second timeout to prevent hanging
            response = await client.get(url, params=params, timeout=10.0)
        except httpx.RequestError:
            raise Exception("Connection to CMS Registry Failed")

    if response.status_code != 200:
        raise Exception(f"CMS Registry Error: {response.status_code}")
        
    data = response.json()
    
    # Validation: Ensure results exist in the response
    if not data.get("results"):
        raise Exception("NPI Not Found")
        
    provider = data["results"][0]
    
    # Data Transformation: Clean messy government JSON into Dashboard-ready JSON
    return {
        "first_name": provider["basic"].get("first_name", ""),
        "last_name": provider["basic"].get("last_name", ""),
        "credential": provider["basic"].get("credential", "N/A"),
        "specialty": provider["taxonomies"][0].get("desc", "Unknown") if provider.get("taxonomies") else "Unknown",
        "state": provider["addresses"][0].get("state", "Unknown") if provider.get("addresses") else "Unknown",
        "npi": npi_number,
        "status": "Active", # Inferred for MVP
        "last_updated": provider["basic"].get("last_updated", "Unknown")
    }
