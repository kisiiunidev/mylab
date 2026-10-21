import boto3
from botocore.config import Config


def create_r2_client(app):
    return boto3.client(
        "s3",
        endpoint_url=(
            f"https://{app.config['R2_ACCOUNT_ID']}"
            ".r2.cloudflarestorage.com"
        ),
        aws_access_key_id=app.config["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=app.config["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )
