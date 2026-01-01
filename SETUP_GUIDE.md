# Sentreso API - Setup Guide

## ✅ Completed Steps

1. ✅ **Dependencies Installed**
   - All required packages from `requirements.txt` have been installed
   - Updated `django-rq` to version 2.10.3 (compatible version)

2. ✅ **Migrations Created**
   - Created migrations for all new apps:
     - `collections` - Collection model
     - `whatsapp` - WhatsAppTemplate and WhatsAppMessage models
     - `reconciliation` - PaymentMatch and ReconciliationRecord models
   - Note: Reports app doesn't need migrations (no models)

## 🔧 Next Steps

### 1. Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
DEBUG=True
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://sentreso:sentreso@localhost:5432/sentreso_db

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_URL=redis://localhost:6379/1

# WhatsApp (Optional - for production)
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_API_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id

# API Keys
API_KEY_PREFIX_LIVE=sk_live_
API_KEY_PREFIX_TEST=sk_test_
```

**To generate a SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Set Up Database

#### Option A: Using Docker Compose (Recommended)

```bash
# Start PostgreSQL and Redis
docker-compose up -d db redis

# Wait a few seconds for services to start, then run migrations
python manage.py migrate
```

#### Option B: Local PostgreSQL

1. Install PostgreSQL 14+
2. Create database:
   ```sql
   CREATE DATABASE sentreso_db;
   CREATE USER sentreso WITH PASSWORD 'sentreso';
   GRANT ALL PRIVILEGES ON DATABASE sentreso_db TO sentreso;
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```

### 3. Create Superuser

```bash
python manage.py createsuperuser
```

This will allow you to:
- Access Django admin at `http://localhost:8000/admin/`
- Create Masters and manage the system

### 4. Start Development Server

```bash
python manage.py runserver
```

The API will be available at:
- API: `http://localhost:8000/api/v1/`
- Admin: `http://localhost:8000/admin/`
- Swagger Docs: `http://localhost:8000/api/docs/`
- Health Check: `http://localhost:8000/api/v1/health/`

### 5. Start RQ Worker (Required for WhatsApp)

In a **separate terminal**, start the RQ worker to process background tasks:

```bash
python manage.py rqworker default
```

This worker processes:
- WhatsApp message sending
- Collection reminders
- Other async tasks

### 6. Test the API

#### Quick Health Check
```bash
curl http://localhost:8000/api/v1/health/
```

#### Create a Master
```bash
curl -X POST http://localhost:8000/api/v1/masters/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Master",
    "email": "test@example.com",
    "webhook_url": "https://example.com/webhook"
  }'
```

Save the `api_key` from the response - you'll need it for authenticated requests.

#### Get Master Info
```bash
curl http://localhost:8000/api/v1/masters/me/ \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 📋 Smoke Test Checklist

Based on the smoke test document, verify:

1. ✅ Health check passes
2. ✅ Create Master and get API key
3. ✅ Create Agent
4. ✅ Create Collection
5. ✅ Send WhatsApp reminder (will fail gracefully if WhatsApp not configured)
6. ✅ Verify WhatsAppMessage record exists
7. ✅ Record payment
8. ✅ Run reconciliation
9. ✅ Verify collection marked as paid

## 🐛 Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify database exists and user has permissions

### Redis Connection Error
- Ensure Redis is running
- Check `REDIS_URL` in `.env`
- For Docker: `docker-compose up -d redis`

### Migration Errors
- If you see "table already exists" errors, you may need to reset:
  ```bash
  python manage.py migrate --fake-initial
  ```

### WhatsApp Not Working
- This is expected if `WHATSAPP_API_URL` is not configured
- Messages will be logged but marked as "failed"
- The system continues to work for other features

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🔐 Security Notes

- Never commit `.env` file to version control
- Use strong `SECRET_KEY` in production
- Rotate API keys regularly
- Use HTTPS in production
- Configure proper `ALLOWED_HOSTS` for production

## 🚀 Production Deployment

For production:
1. Set `ENVIRONMENT=production` in `.env`
2. Set `DEBUG=False`
3. Configure proper database credentials
4. Set up SSL/HTTPS
5. Configure proper `ALLOWED_HOSTS`
6. Use environment-specific settings
7. Set up proper logging
8. Configure WhatsApp Business API credentials

## 📝 Next Development Steps

1. Set up the database and run migrations
2. Create a superuser
3. Test the API endpoints
4. Configure WhatsApp (if needed)
5. Set up webhook endpoints for testing
6. Run the smoke test script

