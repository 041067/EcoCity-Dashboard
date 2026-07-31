import sys
sys.path.insert(0, '.')

from app.database.session import engine
from sqlalchemy import text

print("Testing PostgreSQL connection...")
try:
    conn = engine.connect()
    result = conn.execute(text("SELECT version()"))
    version = result.fetchone()[0]
    print(f"PostgreSQL version: {version}")
    
    result = conn.execute(text("SELECT current_database()"))
    db_name = result.fetchone()[0]
    print(f"Current database: {db_name}")
    
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
    tables = [row[0] for row in result]
    print(f"Tables in database: {tables}")
    
    conn.close()
    print("✅ PostgreSQL connection successful!")
except Exception as e:
    print(f"❌ PostgreSQL connection failed: {e}")
    import traceback
    traceback.print_exc()