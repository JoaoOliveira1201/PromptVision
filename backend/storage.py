import os
import uuid
from typing import Optional
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_exponential

if os.getenv("STORAGE_BACKEND") == "s3":
    import boto3

class StorageService(ABC):
    @abstractmethod
    def upload_video(self, file_path: str, file_name: Optional[str] = None) -> str:
        pass

class S3StorageService(StorageService):
    def __init__(self):
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.s3_region = os.getenv("AWS_DEFAULT_REGION")
        self.s3_client = boto3.client(
            "s3",
            region_name=self.s3_region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def upload_video(self, file_path: str, file_name: Optional[str] = None) -> str:
        if not file_name:
            file_name = f"{uuid.uuid4()}.mp4"
        self.s3_client.upload_file(file_path, self.s3_bucket, file_name, ExtraArgs={"ACL": "public-read"})
        video_url = f"https://{self.s3_bucket}.s3.{self.s3_region}.amazonaws.com/{file_name}"
        return video_url

class LocalStorageService(StorageService):
    def __init__(self):
        self.videos_dir = os.path.join(os.path.dirname(__file__), "..", "videos")
        if not os.path.exists(self.videos_dir):
            os.makedirs(self.videos_dir)

    def upload_video(self, file_path: str, file_name: Optional[str] = None) -> str:
        if not file_name:
            file_name = f"{uuid.uuid4()}.mp4"
        destination_path = os.path.join(self.videos_dir, file_name)
        os.rename(file_path, destination_path)
        video_url = f"/videos/{file_name}"
        return video_url

def get_storage_service() -> StorageService:
    if os.getenv("STORAGE_BACKEND") == "s3":
        return S3StorageService()
    else:
        return LocalStorageService()
