# Sentreso — Collections & Reconciliation API

A Django-based API system for payment collections and reconciliation, with WhatsApp integration for agent communication.

## Tech Stack

- **Framework:** Django 4.2 LTS
- **Database:** PostgreSQL
- **Queue:** Redis + RQ
- **API:** Django REST Framework
- **Documentation:** drf-spectacular (OpenAPI/Swagger)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sentreso-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Start RQ worker** (in separate terminal)
   ```bash
   python manage.py rqworker default
   ```

### Docker Setup

1. **Build and start services**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **View logs**
   ```bash
   docker-compose logs -f
   ```

## Project Structure

```
sentreso-backend/
├── apps/              # Django apps
│   ├── core/         # Shared utilities
│   ├── masters/      # Master/Supplier management
│   ├── agents/       # Agent management
│   └── ...
├── sentreso/         # Project configuration
│   └── settings/     # Environment-based settings
├── tests/            # Test suite
└── scripts/          # Utility scripts
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/api/docs/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
```

### Type Checking
```bash
mypy .
```

## License

Proprietary

