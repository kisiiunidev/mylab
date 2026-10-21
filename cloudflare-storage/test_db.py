
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os
import sys

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    sys.exit("DATABASE_URL is missing from .env")

engine = create_engine(
    database_url,
    pool_pre_ping=True,
)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT DATABASE(), VERSION(), CURRENT_USER()")
        )
        database, version, user = result.one()

        print("Database connection successful.")
        print(f"Database: {database}")
        print(f"Server version: {version}")
        print(f"Connected as: {user}")

except Exception as exc:
    print(f"Database connection failed: {exc}")
    sys.exit(1)

finally:
    engine.dispose()
