import boto3
from botocore.client import Config
import logging
import os

logger = logging.getLogger(__name__)

class MinioStorage:
    def __init__(self):
        # Allow connecting without credentials if necessary, but use defaults from our Phase 1 setup
        endpoint = os.environ.get("MINIO_URL", "http://localhost:9090")
        access_key = os.environ.get("MINIO_ACCESS_KEY", "Gaurav")
        secret_key = os.environ.get("MINIO_SECRET_KEY", "password123")
        
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        logger.info(f"Initialized MinIO storage at {endpoint}")

    def download_data(self, bucket: str, object_name: str, file_path: str):
        try:
            self.s3.download_file(bucket, object_name, file_path)
            logger.info(f"Downloaded {object_name} to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to download {object_name}: {e}")
            return None

    def upload_result(self, bucket: str, file_path: str, object_name: str):
        try:
            self.s3.upload_file(file_path, bucket, object_name)
            logger.info(f"Uploaded {file_path} to {bucket}/{object_name}")
            return f"minio://{bucket}/{object_name}"
        except Exception as e:
            logger.error(f"Failed to upload {file_path}: {e}")
            return None

storage = MinioStorage()
