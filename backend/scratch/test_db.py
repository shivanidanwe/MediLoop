import os
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Connect to the default 'postgres' database first
default_url = "postgresql://postgres:1234@localhost:5432/postgres"
engine = create_engine(default_url)

print("Connecting to default postgres database...")
try:
    # Set autocommit on the connection to allow CREATE DATABASE
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        print("Checking if 'mediloop' database exists...")
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='mediloop'"))
        exists = result.scalar() is not None
        
        if not exists:
            print("Database 'mediloop' does not exist. Creating it...")
            conn.execute(text("CREATE DATABASE mediloop"))
            print("Database 'mediloop' created successfully!")
        else:
            print("Database 'mediloop' already exists.")
            
    # Now verify connection to the new 'mediloop' database
    mediloop_url = "postgresql://postgres:1234@localhost:5432/mediloop"
    mediloop_engine = create_engine(mediloop_url)
    with mediloop_engine.connect() as conn:
        print("Successfully connected to 'mediloop' database!")
        
except Exception as e:
    print(f"Error: {e}")
