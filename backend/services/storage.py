import os
import uuid
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

class StorageService:
    """MinIO storage service for uploaded images"""
    
    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "password123")
        self.bucket_name = os.getenv("MINIO_BUCKET", "menu-images")
        self.secure = False  # Use HTTP for local development
        
        # Initialize MinIO client
        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
            else:
                logger.info(f"MinIO bucket exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating MinIO bucket: {e}")
            raise
    
    async def store_image(self, image_file: UploadFile) -> str:
        """Store uploaded image in MinIO"""
        try:
            # Generate unique filename
            file_extension = image_file.filename.split('.')[-1] if '.' in image_file.filename else 'jpg'
            object_name = f"uploads/{uuid.uuid4()}.{file_extension}"
            
            # Reset file pointer
            await image_file.seek(0)
            
            # Read file content
            file_content = await image_file.read()
            
            # Upload to MinIO
            from io import BytesIO
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=BytesIO(file_content),
                length=len(file_content),
                content_type=image_file.content_type
            )
            
            # Return the object path
            image_path = f"minio://{self.bucket_name}/{object_name}"
            logger.info(f"Stored image: {image_path}")
            
            return image_path
            
        except Exception as e:
            logger.error(f"Error storing image: {e}")
            raise
    
    def get_image_url(self, object_name: str) -> str:
        """Get presigned URL for image access"""
        try:
            # Generate presigned URL (valid for 1 hour)
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=3600  # 1 hour
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def delete_image(self, object_name: str):
        """Delete image from MinIO"""
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=object_name
            )
            logger.info(f"Deleted image: {object_name}")
        except S3Error as e:
            logger.error(f"Error deleting image: {e}")
            raise 