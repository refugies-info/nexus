# Environment Variables Reference

**Date**: 2025-10-21
**Purpose**: Complete reference for all environment variables used in the Nexus orchestration system

---

## Overview

The Nexus pipeline requires environment variables for:
- Database connectivity (Supabase)
- AI/LLM processing (Vercel AI Gateway)
- External APIs (Data Inclusion)
- Logging and monitoring
- Application configuration

---

## Required Variables

### Supabase Configuration

| Variable | Value | Purpose | Example |
|----------|-------|---------|---------|
| `SUPABASE_URL` | PostgreSQL API endpoint | Database connection | `http://localhost:54321` or `https://project.supabase.co` |
| `SUPABASE_KEY` | Anon/Service key | API authentication | `eyJhbGc...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key | Admin operations (optional) | `eyJhbGc...` |

**Local Development**:
```bash
# Get from: supabase start
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Production**:
```bash
# Get from: Supabase dashboard → Settings → API
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Vercel AI Gateway Configuration

| Variable | Value | Purpose | Example |
|----------|-------|---------|---------|
| `VERCEL_AI_GATEWAY_URL` | Gateway API endpoint | LLM request routing | `https://api.vercel.ai/v1` |
| `VERCEL_AI_GATEWAY_TOKEN` | Authentication token | API access | `sk_...` |

**Configuration**:
```bash
# Get from: Vercel dashboard → AI Gateway settings
VERCEL_AI_GATEWAY_URL=https://api.vercel.ai/v1
VERCEL_AI_GATEWAY_TOKEN=sk_your_token_here
```

**Purpose**:
- Routes all LLM requests (enrichment, langage_clair, translation)
- Provides centralized invoicing
- Enables model abstraction (switch models without code changes)
- Handles rate limiting and fallback

---

### Data Inclusion API Configuration

| Variable | Value | Purpose | Example |
|----------|-------|---------|---------|
| `DATA_INCLUSION_API_URL` | API endpoint | Fetch service data | `https://staging.api.data.inclusion.beta.gouv.fr` |
| `DATA_INCLUSION_API_KEY` | API key (optional) | Authentication (if required) | `api_key_...` |

**Staging** (no API key required):
```bash
DATA_INCLUSION_API_URL=https://staging.api.data.inclusion.beta.gouv.fr
```

**Production** (if API key required):
```bash
DATA_INCLUSION_API_URL=https://api.data.inclusion.beta.gouv.fr
DATA_INCLUSION_API_KEY=your_api_key_here
```

---

## Optional Variables

### Application Configuration

| Variable | Value | Purpose | Default |
|----------|-------|---------|---------|
| `ENVIRONMENT` | `development`, `staging`, `production` | Deployment environment | `development` |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Logging verbosity | `INFO` |
| `CORS_ORIGINS` | Comma-separated URLs | CORS allowed origins | `http://localhost:3000,http://localhost:8000` |
| `API_PORT` | Port number | FastAPI server port | `8000` |

**Example**:
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
API_PORT=8000
```

---

### AI Processing Configuration

| Variable | Value | Purpose | Default |
|----------|-------|---------|---------|
| `AI_ENRICHMENT_MODEL` | Model name | Enrichment LLM | `gpt-4` |
| `AI_LANGAGE_CLAIR_MODEL` | Model name | Langage Clair LLM | `gpt-4` |
| `AI_TRANSLATION_MODEL` | Model name | Translation LLM | `gpt-4` |
| `AI_FAST_MODE_MODEL` | Model name | Fast mode (catch-up) LLM | `gpt-3.5-turbo` |
| `AI_MAX_RETRIES` | Integer | Retry attempts for API failures | `3` |
| `AI_TIMEOUT_SECONDS` | Integer | Request timeout | `30` |

**Example**:
```bash
# Normal mode (new programs)
AI_ENRICHMENT_MODEL=gpt-4
AI_LANGAGE_CLAIR_MODEL=gpt-4
AI_TRANSLATION_MODEL=gpt-4

# Fast mode (smart catch-up)
AI_FAST_MODE_MODEL=gpt-3.5-turbo

# Retry configuration
AI_MAX_RETRIES=3
AI_TIMEOUT_SECONDS=30
```

---

### Monitoring & Observability

| Variable | Value | Purpose | Default |
|----------|-------|---------|---------|
| `SENTRY_DSN` | Sentry project URL | Error tracking | (empty) |
| `STRUCTURED_LOGGING` | `true`, `false` | JSON structured logs | `true` |
| `CORRELATION_ID_HEADER` | Header name | Correlation ID tracking | `X-Correlation-ID` |

**Example**:
```bash
SENTRY_DSN=https://your_key@sentry.io/your_project_id
STRUCTURED_LOGGING=true
CORRELATION_ID_HEADER=X-Correlation-ID
```

---

### n8n Configuration

| Variable | Value | Purpose | Default |
|----------|-------|---------|---------|
| `N8N_URL` | n8n instance URL | Workflow engine | `http://localhost:5678` |
| `N8N_API_KEY` | API key | n8n authentication | (empty) |
| `N8N_WEBHOOK_URL` | Public webhook URL | Webhook callbacks | `http://localhost:5678` |

**Local Development**:
```bash
N8N_URL=http://localhost:5678
N8N_WEBHOOK_URL=http://localhost:5678
```

**Production**:
```bash
N8N_URL=https://n8n.your-domain.com
N8N_API_KEY=your_api_key_here
N8N_WEBHOOK_URL=https://n8n.your-domain.com
```

---

### Streamlit Configuration (Diff Review UI)

| Variable | Value | Purpose | Default |
|----------|-------|---------|---------|
| `STREAMLIT_SERVER_PORT` | Port number | Streamlit server port | `8501` |
| `STREAMLIT_SERVER_ADDRESS` | Address | Streamlit server address | `localhost` |
| `STREAMLIT_LOGGER_LEVEL` | `debug`, `info`, `warning`, `error` | Streamlit logging | `info` |

**Example**:
```bash
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_LOGGER_LEVEL=info
```

---

## Environment Files

### `.env` (Local Development)

```bash
# Supabase
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Vercel AI Gateway
VERCEL_AI_GATEWAY_URL=https://api.vercel.ai/v1
VERCEL_AI_GATEWAY_TOKEN=sk_...

# Data Inclusion API
DATA_INCLUSION_API_URL=https://staging.api.data.inclusion.beta.gouv.fr

# Application
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
API_PORT=8000

# AI Processing
AI_ENRICHMENT_MODEL=gpt-4
AI_LANGAGE_CLAIR_MODEL=gpt-4
AI_TRANSLATION_MODEL=gpt-4
AI_FAST_MODE_MODEL=gpt-3.5-turbo
AI_MAX_RETRIES=3
AI_TIMEOUT_SECONDS=30

# n8n
N8N_URL=http://localhost:5678
N8N_WEBHOOK_URL=http://localhost:5678

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### `.env.production` (Production)

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Vercel AI Gateway
VERCEL_AI_GATEWAY_URL=https://api.vercel.ai/v1
VERCEL_AI_GATEWAY_TOKEN=sk_...

# Data Inclusion API
DATA_INCLUSION_API_URL=https://api.data.inclusion.beta.gouv.fr
DATA_INCLUSION_API_KEY=your_api_key_here

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com
API_PORT=8000

# AI Processing
AI_ENRICHMENT_MODEL=gpt-4
AI_LANGAGE_CLAIR_MODEL=gpt-4
AI_TRANSLATION_MODEL=gpt-4
AI_FAST_MODE_MODEL=gpt-3.5-turbo
AI_MAX_RETRIES=3
AI_TIMEOUT_SECONDS=30

# Monitoring
SENTRY_DSN=https://your_key@sentry.io/your_project_id
STRUCTURED_LOGGING=true

# n8n
N8N_URL=https://n8n.your-domain.com
N8N_API_KEY=your_api_key_here
N8N_WEBHOOK_URL=https://n8n.your-domain.com

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

---

## Loading Environment Variables

### Python (FastAPI)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_role_key: str | None = None

    # Vercel AI Gateway
    vercel_ai_gateway_url: str
    vercel_ai_gateway_token: str

    # Data Inclusion API
    data_inclusion_api_url: str
    data_inclusion_api_key: str | None = None

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    api_port: int = 8000

    # AI Processing
    ai_enrichment_model: str = "gpt-4"
    ai_langage_clair_model: str = "gpt-4"
    ai_translation_model: str = "gpt-4"
    ai_fast_mode_model: str = "gpt-3.5-turbo"
    ai_max_retries: int = 3
    ai_timeout_seconds: int = 30

    # Monitoring
    sentry_dsn: str | None = None
    structured_logging: bool = True

    # n8n
    n8n_url: str = "http://localhost:5678"
    n8n_webhook_url: str = "http://localhost:5678"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Node.js (n8n)

```javascript
// Load from process.env
const config = {
  supabaseUrl: process.env.SUPABASE_URL,
  supabaseKey: process.env.SUPABASE_KEY,
  vercelAiGatewayUrl: process.env.VERCEL_AI_GATEWAY_URL,
  vercelAiGatewayToken: process.env.VERCEL_AI_GATEWAY_TOKEN,
  dataInclusionApiUrl: process.env.DATA_INCLUSION_API_URL,
  environment: process.env.ENVIRONMENT || 'development',
};
```

---

## Security Best Practices

### ✅ DO

- ✅ Store sensitive values in `.env` (local) or secrets manager (production)
- ✅ Never commit `.env` to Git (add to `.gitignore`)
- ✅ Use different keys for development, staging, production
- ✅ Rotate API keys regularly
- ✅ Use environment-specific `.env.production`, `.env.staging` files
- ✅ Document all required variables
- ✅ Validate variables on application startup

### ❌ DON'T

- ❌ Hardcode secrets in code
- ❌ Commit `.env` files to Git
- ❌ Share API keys in messages or documentation
- ❌ Use same keys across environments
- ❌ Log sensitive values
- ❌ Use weak or default API keys

---

## Validation on Startup

```python
# apps/orchestration/src/config.py
from pydantic import ValidationError
import sys

try:
    settings = Settings()
    print("✅ All environment variables loaded successfully")
except ValidationError as e:
    print("❌ Missing or invalid environment variables:")
    for error in e.errors():
        print(f"  - {error['loc'][0]}: {error['msg']}")
    sys.exit(1)
```

---

## Troubleshooting

### Missing Required Variables

**Error**: `ValidationError: 1 validation error for Settings`

**Solution**: Check `.env` file has all required variables:
```bash
# Print all required variables
grep -E "^[A-Z_]+" .env | sort
```

### Invalid Supabase Connection

**Error**: `Connection refused` or `401 Unauthorized`

**Solution**: Verify Supabase is running and credentials are correct:
```bash
# Test Supabase connection
curl -H "Authorization: Bearer $SUPABASE_KEY" \
  $SUPABASE_URL/rest/v1/
```

### Vercel AI Gateway Failures

**Error**: `401 Unauthorized` or `Rate limit exceeded`

**Solution**: Check gateway token and rate limits:
```bash
# Test gateway connection
curl -H "Authorization: Bearer $VERCEL_AI_GATEWAY_TOKEN" \
  $VERCEL_AI_GATEWAY_URL/models
```

---

## References

- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Supabase Environment Variables](https://supabase.com/docs/guides/local-development)
- [Vercel AI Gateway Configuration](https://vercel.com/docs/ai-gateway)
- [12 Factor App - Config](https://12factor.net/config)
