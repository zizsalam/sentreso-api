# Database Setup Guide

## Current Status

Migrations are ready but cannot run because PostgreSQL is not available. You have three options:

## Option 1: Use Docker (Recommended for Development)

### Prerequisites
Install Docker Desktop for Windows: https://www.docker.com/products/docker-desktop/

### Steps
1. **Start Docker Desktop**

2. **Start database and Redis services:**
   ```powershell
   docker-compose up -d db redis
   ```

3. **Wait a few seconds for services to start**, then run migrations:
   ```powershell
   python manage.py migrate
   ```

4. **Create superuser:**
   ```powershell
   python manage.py createsuperuser
   ```

## Option 2: Install PostgreSQL Locally

### Prerequisites
Download and install PostgreSQL 14+ from: https://www.postgresql.org/download/windows/

### Steps
1. **Install PostgreSQL** (remember the password you set for the `postgres` user)

2. **Create database and user:**
   - Open pgAdmin or psql command line
   - Run these commands:
     ```sql
     CREATE DATABASE sentreso_db;
     CREATE USER sentreso WITH PASSWORD 'sentreso';
     GRANT ALL PRIVILEGES ON DATABASE sentreso_db TO sentreso;
     ```

3. **Update `.env` file** (if using different credentials):
   ```env
   DATABASE_URL=postgresql://sentreso:sentreso@localhost:5432/sentreso_db
   ```

4. **Run migrations:**
   ```powershell
   python manage.py migrate
   ```

## Option 3: Use a Cloud Database (For Production/Testing)

### Options:
- **ElephantSQL** (Free tier available): https://www.elephantsql.com/
- **Supabase** (Free tier): https://supabase.com/
- **AWS RDS**, **Google Cloud SQL**, etc.

### Steps
1. Create a PostgreSQL database in your chosen service
2. Get the connection string
3. Update `.env` file:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/database
   ```
4. Run migrations:
   ```powershell
   python manage.py migrate
   ```

## Quick Start (If You Choose Docker)

Once Docker is installed:

```powershell
# Navigate to project directory
cd c:\Users\User\sentreso-api\sentreso-api

# Start database and Redis
docker-compose up -d db redis

# Wait 10-15 seconds for services to be ready

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# In another terminal, start RQ worker
python manage.py rqworker default
```

## Redis Setup (Optional for Development)

Redis is required for:
- Background task queue (WhatsApp messages)
- Caching

If using Docker, Redis starts automatically with `docker-compose up -d db redis`.

For local Redis on Windows:
- Install WSL2 and use Redis there, OR
- Use Docker (recommended)

## Verification

After setting up the database, verify the connection:

```powershell
python manage.py check --database default
```

If successful, you should see:
```
System check identified no issues (0 silenced).
```

## Troubleshooting

### "Connection refused" error
- Ensure PostgreSQL is running
- Check that port 5432 is not blocked by firewall
- Verify DATABASE_URL in `.env` file

### "Database does not exist" error
- Create the database first (see Option 2 above)
- Verify database name in DATABASE_URL

### Docker not found
- Install Docker Desktop
- Restart your terminal/PowerShell after installation
- Verify with: `docker --version`

## Current Migration Files Ready

The following migrations are ready to be applied:
- ✅ `apps/collections/migrations/0001_initial.py`
- ✅ `apps/whatsapp/migrations/0001_initial.py`
- ✅ `apps/reconciliation/migrations/0001_initial.py`
- ✅ Existing migrations for core, masters, and agents apps

Once the database is available, simply run:
```powershell
python manage.py migrate
```


