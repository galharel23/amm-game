"""
Script to safely reset the database by terminating all connections first.
Use this in development only!
"""

import sys
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{os.getenv('DATABASE_USER','ammuser')}:{os.getenv('DATABASE_PASSWORD','ammpassword')}@{os.getenv('DATABASE_HOST','localhost')}:{os.getenv('DATABASE_PORT','5432')}/{os.getenv('DATABASE_NAME','amm_db')}")

# Extract connection parameters
from urllib.parse import urlparse
parsed = urlparse(DATABASE_URL)

db_user = parsed.username
db_password = parsed.password
db_host = parsed.hostname
db_port = parsed.port or 5432
db_name = parsed.path.lstrip('/')

# Connection to PostgreSQL default database (postgres)
ADMIN_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"

print("Connecting to PostgreSQL...")
admin_engine = create_engine(ADMIN_URL)

try:
    with admin_engine.connect() as conn:
        # Enable autocommit for database operations
        conn = conn.connection
        conn.autocommit = True
        cursor = conn.cursor()

        print(f"Terminating all connections to '{db_name}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
            AND pid <> pg_backend_pid();
        """)
        
        print(f"Dropping database '{db_name}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
        
        print(f"Creating database '{db_name}'...")
        cursor.execute(f"CREATE DATABASE {db_name};")
        
        cursor.close()

    print("✓ Database dropped and recreated successfully!")
    
    # Now create tables
    print("\nCreating tables...")
    from app.database import init_db
    init_db()
    print("✓ Tables created successfully!")
    
    print("\n✅ Database reset complete!")

except Exception as e:
    print(f"❌ Error: {e}", file=sys.stderr)
    sys.exit(1)

finally:
    admin_engine.dispose()
