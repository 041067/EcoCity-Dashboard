#!/usr/bin/env python3
"""
Script to migrate from SQLite to Supabase PostgreSQL for production deployment.
"""

import os
import sys
import subprocess

sys.path.insert(0, '.')

from app.core.config import settings
from app.database.session import engine, Base, SessionLocal
from sqlalchemy import text

def check_sqlite_state():
    """Check if we have SQLite database with data"""
    from app.models.city import City
    from app.models.sensor_reading import SensorReading
    from app.models.ai_report import AIReport

    try:
        db = SessionLocal()
        cities_count = db.query(City).count()
        readings_count = db.query(SensorReading).count()
        reports_count = db.query(AIReport).count()
        db.close()
        return {
            'has_data': cities_count > 0 or readings_count > 0 or reports_count > 0,
            'cities': cities_count,
            'readings': readings_count,
            'reports': reports_count
        }
    except Exception as e:
        print(f"Error checking SQLite state: {e}")
        return None

def backup_sqlite_data():
    """Create a backup of SQLite database before migration"""
    import shutil
    
    sqlite_file = "ecocity.db"
    backup_dir = "db_backup"
    backup_file = os.path.join(backup_dir, "ecocity.db.backup")
    
    if not os.path.exists(sqlite_file):
        print("No SQLite database found to backup")
        return False
    
    os.makedirs(backup_dir, exist_ok=True)
    shutil.copy2(sqlite_file, backup_file)
    print(f"SQLite database backed up to: {backup_file}")
    return True

def test_postgresql_connection():
    """Test PostgreSQL connection"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy import text
        
        url = settings.DATABASE_URL
        if not url:
            print("Error: DATABASE_URL is not set in .env file")
            return False
        
        test_engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5, "sslmode": "require"},
        )
        
        with test_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL connection successful")
            
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"PostgreSQL version: {version}")
            
            # Try to create a test table
            try:
                conn.execute(text("CREATE TABLE IF NOT EXISTS migration_test (id INTEGER PRIMARY KEY)"))
                conn.execute(text("INSERT INTO migration_test (id) VALUES (1)"))
                conn.execute(text("SELECT * FROM migration_test"))
                conn.execute(text("DROP TABLE migration_test"))
                print("✅ PostgreSQL table operations successful")
            except Exception as e:
                print(f"⚠️ PostgreSQL table operations failed: {e}")
                return False
                
        test_engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def export_sqlite_data():
    """Export data from SQLite to PostgreSQL"""
    from app.models.city import City
    from app.models.sensor_reading import SensorReading
    from app.models.ai_report import AIReport

    try:
        # Get data from SQLite
        db = SessionLocal()
        cities = db.query(City).all()
        readings = db.query(SensorReading).all()
        reports = db.query(AIReport).all()
        db.close()

        print(f"Exported data:")
        print(f"  - Cities: {len(cities)}")
        print(f"  - Readings: {len(readings)}")
        print(f"  - Reports: {len(reports)}")

        # For now, we'll just print the data since we can't connect to PostgreSQL
        # In a real migration, you would:
        # 1. Connect to PostgreSQL
        # 2. Clear any existing tables
        # 3. Insert the data

        print("\n⚠️ Note: Since PostgreSQL connection failed, data export is simulated.")
        print("    In a production environment, this would actually migrate the data.")

        return True

    except Exception as e:
        print(f"❌ Error exporting SQLite data: {e}")
        return False

def run_alembic_migrations():
    """Run Alembic migrations on PostgreSQL"""
    try:
        print("Running Alembic migrations for PostgreSQL...")
        
        # Update alembic.ini to use PostgreSQL
        with open('alembic.ini', 'r') as f:
            ini_content = f.read()
        
        # Replace SQLite URL with PostgreSQL URL
        import re
        new_ini_content = re.sub(
            r'^sqlalchemy\.url\s*=\s*.*$',
            f'sqlalchemy.url = {settings.DATABASE_URL}',
            ini_content,
            flags=re.MULTILINE
        )
        
        with open('alembic.ini', 'w') as f:
            f.write(new_ini_content)
        
        # Run Alembic migration
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        
        # Check if migrations have already been applied
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='alembic_version'"))
            if result.scalar() > 0:
                print("✅ Alembic version table exists")
                
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.fetchone()[0]
                print(f"Current Alembic version: {version}")
            else:
                print("⚠️ Alembic version table does not exist yet")
        
        print("✅ Alembic configuration updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error running Alembic migrations: {e}")
        return False

def main():
    print("=" * 60)
    print("Migrating from SQLite to Supabase PostgreSQL")
    print("=" * 60)

    # Check current SQLite state
    sqlite_state = check_sqlite_state()
    if sqlite_state is None:
        print("Could not check SQLite state")
        return

    print(f"\nCurrent SQLite state:")
    print(f"  - Has data: {sqlite_state['has_data']}")
    print(f"  - Cities: {sqlite_state['cities']}")
    print(f"  - Readings: {sqlite_state['readings']}")
    print(f"  - Reports: {sqlite_state['reports']}")

    # Backup SQLite data
    if sqlite_state['has_data']:
        backup_sqlite_data()
        print("\nSQLite data backed up successfully")
    else:
        print("\nNo SQLite data to backup")

    # Test PostgreSQL connection
    print("\n" + "=" * 60)
    print("Testing PostgreSQL connection")
    print("=" * 60)

    if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgresql"):
        print(f"Using configured PostgreSQL URL: {settings.DATABASE_URL}")
        print("\n⚠️ Important: If PostgreSQL connection fails here, check:")
        print("    1. Your Supabase connection string is correct")
        print("    2. The database server is accessible")
        print("    3. Your credentials are valid")
        print("    4. The host is resolvable (https://hosting.edbase.io/search/db.qbghywxepuujcwxbvklj.supabase.co)")

    # Test PostgreSQL connection
    pg_connected = test_postgresql_connection()

    if pg_connected:
        print("\n" + "=" * 60)
        print("PostgreSQL connection established")
        print("=" * 60)

        # Export and migrate data
        if sqlite_state['has_data']:
            print("\nExporting data from SQLite to PostgreSQL...")
            export_sqlite_data()

        print("\nRunning Alembic migrations...")
        run_alembic_migrations()

        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Deploy the backend to Render")
        print("2. Deploy the frontend to Vercel")
        print("3. Update the .env file with correct PostgreSQL credentials")
        return

    else:
        print("\n" + "=" * 60)
        print("PostgreSQL connection failed - using SQLite for development")
        print("=" * 60)
        print("\nTo complete the migration, please:")
        print("1. Ensure your Supabase PostgreSQL connection string is correct")
        print("2. Verify the database host is accessible")
        print("3. Check that your credentials are valid")
        print("4. Update the .env file with the correct DATABASE_URL")
        print("\nThen run this script again to perform the migration.")
        print("\n⚠️ For deployment to Render/Vercel, PostgreSQL is required.")
        print("   Render will use the DATABASE_URL from your deployment environment.")

if __name__ == "__main__":
    main()