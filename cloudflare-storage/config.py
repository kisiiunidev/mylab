import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ["FLASK_SECRET_KEY"]

    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_UPLOAD_MB", "50")
    ) * 1024 * 1024

    R2_ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
    R2_ACCESS_KEY_ID = os.environ["R2_ACCESS_KEY_ID"]
    R2_SECRET_ACCESS_KEY = os.environ["R2_SECRET_ACCESS_KEY"]
    R2_BUCKET_NAME = os.environ["R2_BUCKET_NAME"]
    R2_PUBLIC_BASE_URL = os.environ["R2_PUBLIC_BASE_URL"].rstrip("/")
