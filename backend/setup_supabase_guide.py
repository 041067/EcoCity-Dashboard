#!/usr/bin/env python3
"""
Guide to set up PostgreSQL database for production deployment.

This script provides instructions to help you migrate from SQLite to Supabase PostgreSQL.
"""

import os
import sys

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_current_setup():
    """Check current project setup"""
    print_header("Current Project Setup")

    backend_dir = os.path.join(os.getcwd(), "backend")
    
    # Check .env file
    env_path = os.path.join(backend_dir, ".env")
    if os.path.exists(env_path):
        print(f"✅ .env file exists: {env_path}")
        with open(env_path, "r") as f:
            content = f.read()
            if "DATABASE_URL=postgresql://" in content:
                print(f"✅ PostgreSQL URL configured")
                # Extract just the URL for display
                for line in content.splitlines():
                    if line.startswith("DATABASE_URL="):
                        print(f"   {line}")
            else:
                print(f"⚠️ No PostgreSQL URL found in .env")
    else:
        print(f"❌ .env file missing: {env_path}")

    # Check alembic.ini
    alembic_path = os.path.join(backend_dir, "alembic.ini")
    if os.path.exists(alembic_path):
        print(f"✅ alembic.ini file exists: {alembic_path}")
    else:
        print(f"❌ alembic.ini file missing: {alembic_path}")

    # Check requirements.txt
    req_path = os.path.join(backend_dir, "requirements.txt")
    if os.path.exists(req_path):
        print(f"✅ requirements.txt file exists: {req_path}")
        with open(req_path, "r") as f:
            if "psycopg2-binary" in f.read():
                print(f"✅ psycopg2-binary dependency configured")
            else:
                print(f"⚠️ psycopg2-binary dependency missing")
    else:
        print(f"❌ requirements.txt file missing: {req_path}")

def guide_step_by_step():
    """Guide users through PostgreSQL setup"""

    print_header("PostgreSQL Migration Guide for Production")

    print("\n" + "=" * 70)
    print("STEP 1: Test PostgreSQL Connection")
    print("=" * 70)
    print("""
The current .env file contains a PostgreSQL URL:
  DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres

⚠️  The hostname 'db.qbghywxepuujcwxbvklj.supabase.co' may not be resolvable in your environment.

SOLUTIONS:

1. Use Supabase Pooler (Recommended for IPv4 support):
   - Go to your Supabase dashboard
   - Navigate to Database > Connection string
   - Select "Session Pooler (IPv4)" or "Session Pooler (IPv6)"
   - Copy the connection string (format: postgresql://postgres:yourpassword@aws-0-your-region-1.pooler.supabase.com:6543/postgres)

2. Use Direct PostgreSQL (if IPv6 supported):
   - In Supabase dashboard, go to Database > Connection string
   - Select "Direct" connection
   - Copy the connection string (format: postgresql://postgres:yourpassword@db.your-project.supabase.co:5432/postgres)

3. For local development (if PostgreSQL is available):
   - Install PostgreSQL locally
   - Create a database and user
   - Update DATABASE_URL in .env file

Example connection strings:
  • Pooler IPv4: postgresql://postgres:yourpassword@aws-0-us-west-1.pooler.supabase.com:6543/postgres
  • Direct IPv6: postgresql://postgres:yourpassword@db.your-project.supabase.co:5432/postgres
""")

    print("\n" + "=" * 70)
    print("STEP 2: Update .env File")
    print("=" * 70)

    print("""
Replace the DATABASE_URL in C:\\EcoCity-Dashboard\\backend\\.env with a working connection string:

Example (replace with your actual credentials):
  DATABASE_URL=postgresql://postgres:your_actual_password@aws-0-your-region-1.pooler.supabase.com:6543/postgres

Keep these environment variables:
  GROQ_API_KEY=your_groq_api_key_here
  OPEN_METEO_URL=https://api.open-meteo.com/v1
  ENVIRONMENT=production
""")

    print("\n" + "=" * 70)
    print("STEP 3: Test Connection")
    print("=" * 70)

    print("""
Run this script to test the connection:

python -c "
from app.core.config import settings
from app.database.session import engine

try:
    conn = engine.connect()
    result = conn.execute('SELECT 1')
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

If connection fails:
  1. Verify the connection string is correct
  2. Check that your Supabase project is accessible
  3. Ensure the database user has proper permissions
  4. Confirm the database exists
""")

    print("\n" + "=" * 70)
    print("STEP 4: Run Database Migrations")
    print("=" * 70)

    print("""
After successful connection, run these commands to create database tables:

cd backend
alembic upgrade head

This will:
  • Create the 'cities' table
  • Create the 'sensor_readings' table  
  • Create the 'ai_reports' table
  • Set up proper indexes and constraints
""")

    print("\n" + "=" * 70)
    print("STEP 5: Update Alembic Configuration")
    print("=" * 70)

    print("""
Update alembic.ini to use PostgreSQL:

[alembic]
script_location = alembic
sqlalchemy.url = postgresql://postgres:yourpassword@your-suppabase-host:5432/postgres
""")

    print("\n" + "=" * 70)
    print("STEP 6: Remove SQLite Fallback")
    print("=" * 70)

    print("""
Update app/database/session.py to use PostgreSQL:

• Remove SQLite fallback (comment out or delete SQLite code)
• Use strict PostgreSQL connection with SSL
• Remove any SQLite-specific error handling

The code should try to connect to PostgreSQL and fail if not available.
""")

    print("\n" + "=" * 70)
    print("STEP 7: Update Frontend Configuration")
    print("=" * 70)

    print("""
Update frontend/.env if needed:

VITE_API_URL=https://your-backend-domain.com/api

Or if accessing via proxy:
VITE_API_URL=/api
""")

def show_migration_commands():
    """Show actual migration commands"""
    print("\n" + "=" * 70)
    print("READY-TO-EXECUTE COMMANDS")
    print("=" * 70)

    print("""
# 1. Backup current SQLite database (if exists)
mv ecocity.db ecocity-db-backup.sqlitedb 2>/dev/null || echo "No SQLite database to backup"

# 2. Run migration script
python migrate_to_supabase.py

# 3. Alternative: Direct connection check
python -c "
from app.core.config import settings
try:
    from app.database.session import engine
    conn = engine.connect()
    result = conn.execute('SELECT 1')
    print('PostgreSQL connection: SUCCESS')
    conn.close()
except Exception as e:
    print(f'PostgreSQL connection: FAILED - {e}')
    print('Run this to use SQLite (for development only):')
    print('sqlite:///ecocity.db')
"

# 4. After PostgreSQL works, run alembic migration
cd backend
alembic upgrade head
""")

def main():
    print_header("PostgreSQL Database Setup Guide for EcoCity Dashboard")

    check_current_setup()
    guide_step_by_step()
    show_migration_commands()

    print_header("FAQ")
    print("""
Q: What if PostgreSQL connection fails?
A: 1. Use Supabase Pooler connection string
   2. Check if the project host is correct
   3. Verify credentials are up to date
   4. Ensure the database exists

Q: Should I use SQLite or PostgreSQL?
A: Use PostgreSQL for production (Render/Vercel deployment)
   Use SQLite only for local development

Q: What happens if migration fails?
A: We have a backup mechanism. The last working state is preserved.

Q: How do I know when to run migrations?
A: Run migrations once after successfully connecting to PostgreSQL.
""")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
1. Obtain the correct PostgreSQL connection string from your Supabase dashboard
2. Update the .env file
3. Run the migration script
4. Test the API endpoints
5. Deploy to Render (backend) and Vercel (frontend)

Remember: Production uses PostgreSQL, development can use SQLite.
""")

if __name__ == "__main__":
    main()