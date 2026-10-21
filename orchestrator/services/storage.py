import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
import os
from fastapi import UploadFile

logger = logging.getLogger(__name__)

class MinioStorage:
    def __init__(self):
        self.endpoint = os.environ.get("MINIO_URL", "http://localhost:9090")
        self.access_key = os.environ.get("MINIO_ACCESS_KEY", "Gaurav")
        self.secret_key = os.environ.get("MINIO_SECRET_KEY", "password123")
        self.bucket_name = "daemon-jobs"
        
        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4')
        )
        
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            logger.info(f"Bucket {self.bucket_name} not found. Creating it...")
            try:
                self.s3.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Bucket {self.bucket_name} created successfully.")
            except Exception as e:
                logger.warning(f"Could not create bucket {self.bucket_name}: {e}")
        except Exception as conn_err:
            logger.warning(f"Could not reach MinIO to verify bucket ({conn_err}). Will verify on upload.")

    async def upload_file(self, file: UploadFile, object_name: str) -> str:
        self._ensure_bucket_exists()
        try:
            contents = await file.read()
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=contents,
                ContentType=file.content_type
            )
            logger.info(f"Successfully uploaded {object_name} to MinIO")
            return f"minio://{self.bucket_name}/{object_name}"
        except Exception as e:
            logger.error(f"Failed to upload {object_name}: {e}")
            raise e

    def list_results(self, job_id: str) -> list:
        """List all result files for a job in MinIO."""
        try:
            prefix = f"{job_id}/results/"
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            files = []
            for obj in response.get("Contents", []):
                files.append({
                    "key": obj["Key"],
                    "filename": obj["Key"].split("/")[-1],
                    "size": obj["Size"],
                })
            return files
        except Exception as e:
            logger.error(f"Failed to list results for {job_id}: {e}")
            return []

    def download_file(self, object_key: str) -> bytes:
        """Download a file from MinIO and return its bytes."""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
            return response["Body"].read()
        except Exception as e:
            logger.error(f"Failed to download {object_key}: {e}")
            raise e

storage = MinioStorage()
