# CredentialGuard Backend API

A high-performance Python FastAPI server that provides real-time healthcare provider verification by querying the CMS NPPES Registry.

## Features

- **Real-time NPI Lookup:** Query the official CMS NPPES Registry API
- **Provider Data Transformation:** Clean government JSON into dashboard-ready format
- **CORS Support:** Configured for React frontend integration
- **Async/Await:** High-performance async networking with HTTPX
- **Error Handling:** Comprehensive error handling with meaningful messages
- **Input Validation:** 10-digit NPI format validation

## Quick Start

### Local Development

1. **Create Virtual Environment**
   ```bash
   python3.11 -m venv backend_env
   source backend_env/bin/activate  # On Windows: backend_env\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Server**
   ```bash
   python -m backend.main
   ```

   Server will start at `http://localhost:8000`

4. **Test Health Check**
   ```bash
   curl http://localhost:8000/
   ```

### API Endpoints

#### Health Check
```
GET /
Response: {"status":"online","system":"CredentialGuard Revenue Engine"}
```

#### Provider Lookup
```
GET /api/v1/providers/lookup/{npi}

Parameters:
  npi (string): 10-digit National Provider Identifier

Response:
{
  "first_name": "John",
  "last_name": "Doe",
  "credential": "MD",
  "specialty": "Internal Medicine",
  "state": "CA",
  "npi": "1234567893",
  "status": "Active",
  "last_updated": "2024-01-04"
}

Errors:
  400: Invalid NPI format (must be 10 digits)
  404: NPI not found or CMS API error
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```
PORT=8000
ENVIRONMENT=production
FRONTEND_URL=http://localhost:3000
FRONTEND_URL_PROD=https://your-frontend-domain.com
CMS_NPPES_API_URL=https://npiregistry.cms.hhs.gov/api/
CMS_NPPES_TIMEOUT=10
LOG_LEVEL=INFO
```

## Deployment

### Railway (Recommended)
1. Connect GitHub repository to Railway
2. Railway auto-detects Python project
3. Installs dependencies from `requirements.txt`
4. Runs using `Procfile` command
5. Set environment variables in Railway dashboard

### Heroku
```bash
heroku login
heroku create credentialguard-backend
git push heroku main
```

### Docker
```bash
docker build -t credentialguard-backend .
docker run -p 8000:8000 credentialguard-backend
```

## Architecture

```
backend/
├── main.py              # FastAPI application entry point
├── services/
│   ├── __init__.py
│   └── nppes.py        # CMS NPPES Registry integration
├── requirements.txt     # Python dependencies
├── Procfile            # Deployment configuration
└── railway.json        # Railway-specific config
```

## Key Components

### `main.py`
- FastAPI application setup
- CORS middleware configuration
- Health check endpoint
- Provider lookup endpoint with validation

### `services/nppes.py`
- Async HTTPX client for API calls
- CMS NPPES Registry integration
- Data transformation and validation
- Error handling with meaningful messages

## Performance

- **Async Processing:** Non-blocking I/O for high throughput
- **Timeout Protection:** 10-second timeout prevents hanging requests
- **Error Recovery:** Graceful error handling with meaningful messages
- **CORS Optimization:** Configured for frontend domain

## Security

- Input validation on NPI format
- CORS restricted to frontend domains
- No sensitive data in logs
- Timeout protection against DoS
- Error messages don't expose system details

## Monitoring

### Local Development
```bash
# Watch logs
tail -f logs/app.log

# Monitor performance
python -m backend.main
```

### Production (Railway)
- Dashboard shows request metrics
- Error tracking and alerting
- Automatic restarts on failure
- Log aggregation

## Troubleshooting

### NPI Lookup Returns 404
- Verify NPI is exactly 10 digits
- Check CMS NPPES API is accessible
- Review logs for detailed error

### CORS Errors
- Verify frontend domain in `origins` list in `main.py`
- Restart server after changes

### Timeout Errors
- Check network connectivity
- Verify CMS API is responding
- Increase timeout if needed (modify `nppes.py`)

## Testing

### Test with Valid NPI
```bash
curl http://localhost:8000/api/v1/providers/lookup/1234567893
```

### Test with Invalid NPI
```bash
curl http://localhost:8000/api/v1/providers/lookup/123  # Too short
curl http://localhost:8000/api/v1/providers/lookup/abcd567893  # Non-numeric
```

## Dependencies

- **fastapi:** Modern web framework
- **uvicorn:** ASGI server
- **httpx:** Async HTTP client
- **pydantic:** Data validation
- **python-multipart:** Form data handling

## License

MIT

## Support

For issues or questions, refer to the main DEPLOYMENT_GUIDE.md
