# Sentreso API - Rebuild Summary

This document summarizes what was rebuilt based on the documentation provided.

## Overview

The Sentreso API is a Django-based payment collection and reconciliation system with WhatsApp integration. The system was rebuilt from the base repository at https://github.com/zizsalam/sentreso-api based on the documentation provided.

## Components Rebuilt

### 1. Collections App (`apps/collections/`)
- **Collection Model**: Represents payment obligations from agents to masters
- **Status Flow**: pending → paid/failed/cancelled
- **Features**:
  - Create collections with due dates
  - Mark collections as paid
  - Track payment methods and transaction references
  - Automatic webhook notifications
- **Endpoints**:
  - `POST /api/v1/collections/` - Create collection
  - `GET /api/v1/collections/` - List collections (with filters)
  - `POST /api/v1/collections/{id}/mark_paid/` - Mark as paid

### 2. WhatsApp App (`apps/whatsapp/`)
- **WhatsAppTemplate Model**: Reusable message templates with variables
- **WhatsAppMessage Model**: Tracks all messages sent/received
- **Features**:
  - Template-based messaging
  - Variable substitution (agent_name, amount, due_date)
  - Queue-based async message sending
  - Message status tracking (sent, delivered, read, failed)
- **Endpoints**:
  - `GET/POST /api/v1/whatsapp/templates/` - Manage templates
  - `GET /api/v1/whatsapp/messages/` - View messages
  - `POST /api/v1/whatsapp/messages/send_reminder/` - Send collection reminder
  - `POST /api/v1/whatsapp/messages/send/` - Send custom message
- **Background Tasks**:
  - `send_collection_reminder_task` - Sends reminder via RQ queue
  - `send_whatsapp_message_task` - Sends custom message via RQ queue

### 3. Reconciliation App (`apps/reconciliation/`)
- **PaymentMatch Model**: Records payments received that need matching
- **ReconciliationRecord Model**: Tracks reconciliation runs
- **Features**:
  - Automatic payment-to-collection matching
  - Exact amount matching
  - Support for unmatched payments
  - Reconciliation statistics
- **Endpoints**:
  - `POST /api/v1/reconciliation/payments/` - Record payment
  - `GET /api/v1/reconciliation/payments/` - List payments
  - `POST /api/v1/reconciliation/records/start/` - Start reconciliation
  - `GET /api/v1/reconciliation/records/` - View reconciliation history

### 4. Reports App (`apps/reports/`)
- **Dashboard View**: Real-time statistics
- **Collections Export**: CSV export functionality
- **Features**:
  - Recovery rate calculation
  - Average payment delay
  - Agent statistics
  - WhatsApp message statistics
  - Payment matching statistics
- **Endpoints**:
  - `GET /api/v1/reports/dashboard/` - Dashboard statistics
  - `GET /api/v1/reports/collections/export/` - Export collections to CSV

### 5. Core Enhancements
- **Webhook System** (`apps/core/webhooks.py`):
  - HMAC SHA256 signature generation
  - Automatic webhook delivery
  - Retry logic support
  - Events: `collection.created`, `collection.paid`
- **Health Check** (`apps/api/views.py`):
  - Database connectivity check
  - Redis connectivity check
  - Cache functionality check
  - Endpoint: `GET /api/v1/health/`

## API Structure

All endpoints require API key authentication via `Authorization: Bearer {api_key}` header.

### Master Endpoints
- `POST /api/v1/masters/` - Register new master (no auth)
- `GET /api/v1/masters/me/` - Get current master info
- `PATCH /api/v1/masters/me/` - Update master info

### Agent Endpoints
- `GET/POST /api/v1/agents/` - List/create agents
- `GET/PUT/PATCH/DELETE /api/v1/agents/{id}/` - Agent operations

### Collection Endpoints
- `GET/POST /api/v1/collections/` - List/create collections
- `GET/PUT/PATCH /api/v1/collections/{id}/` - Collection operations
- `POST /api/v1/collections/{id}/mark_paid/` - Mark as paid

### WhatsApp Endpoints
- `GET/POST /api/v1/whatsapp/templates/` - Template management
- `GET /api/v1/whatsapp/messages/` - View messages
- `POST /api/v1/whatsapp/messages/send_reminder/` - Send reminder
- `POST /api/v1/whatsapp/messages/send/` - Send custom message

### Reconciliation Endpoints
- `GET/POST /api/v1/reconciliation/payments/` - Payment management
- `POST /api/v1/reconciliation/records/start/` - Start reconciliation
- `GET /api/v1/reconciliation/records/` - View reconciliation history

### Reports Endpoints
- `GET /api/v1/reports/dashboard/` - Dashboard stats
- `GET /api/v1/reports/collections/export/` - Export CSV

## Configuration

### Environment Variables
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection for queue
- `REDIS_CACHE_URL` - Redis connection for cache
- `WHATSAPP_API_URL` - WhatsApp Business API URL (optional)
- `WHATSAPP_API_TOKEN` - WhatsApp API token (optional)
- `WHATSAPP_PHONE_NUMBER_ID` - WhatsApp phone number ID (optional)

### Settings Updates
- Added all new apps to `INSTALLED_APPS`
- Configured RQ queues (default, high_priority, low_priority)
- API key authentication configured
- OpenAPI/Swagger documentation enabled

## Database Models

### Existing Models
- `Master` - Suppliers/lenders
- `Agent` - Mobile money agents/shops

### New Models
- `Collection` - Payment obligations
- `WhatsAppTemplate` - Message templates
- `WhatsAppMessage` - Message tracking
- `PaymentMatch` - Payment records
- `ReconciliationRecord` - Reconciliation runs

## Next Steps

1. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

3. **Start RQ Worker**:
   ```bash
   python manage.py rqworker default
   ```

4. **Configure WhatsApp** (optional):
   - Set `WHATSAPP_API_URL`, `WHATSAPP_API_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`
   - Create approved templates in Meta Business Suite

5. **Test the API**:
   - Use the smoke test script or Postman
   - Check Swagger docs at `/api/docs/`

## Notes

- All models use UUID primary keys
- All models inherit from `BaseModel` with timestamps
- All operations are scoped to the authenticated master
- Webhooks are sent automatically for collection events
- WhatsApp messages are queued for async processing
- Reconciliation matches payments to collections by exact amount

## Files Created

### Collections App
- `apps/collections/models.py`
- `apps/collections/serializers.py`
- `apps/collections/views.py`
- `apps/collections/urls.py`
- `apps/collections/admin.py`
- `apps/collections/managers.py`

### WhatsApp App
- `apps/whatsapp/models.py`
- `apps/whatsapp/serializers.py`
- `apps/whatsapp/views.py`
- `apps/whatsapp/urls.py`
- `apps/whatsapp/admin.py`
- `apps/whatsapp/tasks.py`
- `apps/whatsapp/services.py`

### Reconciliation App
- `apps/reconciliation/models.py`
- `apps/reconciliation/serializers.py`
- `apps/reconciliation/views.py`
- `apps/reconciliation/urls.py`
- `apps/reconciliation/admin.py`
- `apps/reconciliation/services.py`

### Reports App
- `apps/reports/views.py`
- `apps/reports/urls.py`

### Core
- `apps/core/webhooks.py`
- `apps/api/views.py` (health check)

## Testing

The system was designed to match the smoke test requirements:
1. Master API key authentication
2. Agent creation
3. Collection creation
4. WhatsApp reminder sending
5. Message tracking (even when WhatsApp not configured)
6. Payment recording
7. Reconciliation

All endpoints follow the API structure documented in the reconciliation document.

