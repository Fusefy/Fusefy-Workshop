"""
Google Cloud Storage utilities for document management.

This module provides helper functions for interacting with Google Cloud Storage,
including document upload, download, signed URL generation, and metadata management.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from google.cloud import storage
from google.cloud.exceptions import NotFound

from src.config.settings import settings

logger = logging.getLogger(__name__)


class GCSManager:
    """
    Manager class for Google Cloud Storage operations.
    
    Provides methods for uploading, downloading, and managing documents
    stored in Google Cloud Storage buckets.
    """
    
    def __init__(self):
        """Initialize the GCS manager with client and bucket configuration."""
        self.client = None
        self.bucket_name = settings.GCS_BUCKET_NAME
        
    def _get_client(self) -> storage.Client:
        """Get or create GCS client."""
        if not self.client:
            self.client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        return self.client
    
    def _get_bucket(self) -> storage.Bucket:
        """Get the configured GCS bucket."""
        client = self._get_client()
        return client.bucket(self.bucket_name)
    
    async def ensure_bucket_exists(self) -> bool:
        """
        Ensure the configured bucket exists, create if necessary.
        
        Returns:
            True if bucket exists or was created successfully
        """
        try:
            client = self._get_client()
            bucket = client.bucket(self.bucket_name)
            
            if not bucket.exists():
                bucket = client.create_bucket(
                    self.bucket_name,
                    location=settings.VERTEX_AI_LOCATION
                )
                logger.info(f"Created GCS bucket: {self.bucket_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            return False
    
    def generate_signed_url(self, 
                          blob_name: str, 
                          expiration_hours: int = 24,
                          method: str = "GET") -> Optional[str]:
        """
        Generate a signed URL for accessing a GCS object.
        
        Args:
            blob_name: Name of the blob in GCS
            expiration_hours: URL expiration time in hours
            method: HTTP method for the URL (GET, PUT, etc.)
            
        Returns:
            Signed URL string or None if generation fails
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(blob_name)
            
            expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
            
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method=method
            )
            
            logger.info(f"Generated signed URL for {blob_name}")
            return signed_url
            
        except Exception as e:
            logger.error(f"Failed to generate signed URL for {blob_name}: {e}")
            return None
    
    def get_blob_metadata(self, blob_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a GCS blob.
        
        Args:
            blob_name: Name of the blob in GCS
            
        Returns:
            Dictionary containing blob metadata or None if not found
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(blob_name)
            
            if not blob.exists():
                return None
            
            blob.reload()  # Refresh metadata
            
            metadata = {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created.isoformat() if blob.time_created else None,
                'updated': blob.updated.isoformat() if blob.updated else None,
                'etag': blob.etag,
                'md5_hash': blob.md5_hash,
                'custom_metadata': blob.metadata or {}
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get metadata for {blob_name}: {e}")
            return None
    
    def list_claim_documents(self, claim_id: UUID) -> List[Dict[str, Any]]:
        """
        List all documents associated with a claim.
        
        Args:
            claim_id: The claim ID to search for
            
        Returns:
            List of document metadata dictionaries
        """
        try:
            bucket = self._get_bucket()
            prefix = f"claims/{claim_id}/"
            
            documents = []
            for blob in bucket.list_blobs(prefix=prefix):
                doc_metadata = {
                    'name': blob.name,
                    'filename': blob.name.split('/')[-1],  # Extract filename
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'created': blob.time_created.isoformat() if blob.time_created else None,
                    'gcs_uri': f"gs://{self.bucket_name}/{blob.name}",
                    'custom_metadata': blob.metadata or {}
                }
                documents.append(doc_metadata)
            
            logger.info(f"Found {len(documents)} documents for claim {claim_id}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents for claim {claim_id}: {e}")
            return []
    
    def delete_blob(self, blob_name: str) -> bool:
        """
        Delete a blob from GCS.
        
        Args:
            blob_name: Name of the blob to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(blob_name)
            
            if blob.exists():
                blob.delete()
                logger.info(f"Deleted blob: {blob_name}")
                return True
            else:
                logger.warning(f"Blob not found for deletion: {blob_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete blob {blob_name}: {e}")
            return False
    
    def copy_blob(self, 
                 source_blob_name: str, 
                 destination_blob_name: str,
                 destination_bucket: Optional[str] = None) -> bool:
        """
        Copy a blob within GCS.
        
        Args:
            source_blob_name: Name of the source blob
            destination_blob_name: Name of the destination blob
            destination_bucket: Destination bucket (uses same bucket if None)
            
        Returns:
            True if copy was successful
        """
        try:
            source_bucket = self._get_bucket()
            source_blob = source_bucket.blob(source_blob_name)
            
            if destination_bucket:
                client = self._get_client()
                dest_bucket = client.bucket(destination_bucket)
            else:
                dest_bucket = source_bucket
            
            dest_blob = source_bucket.copy_blob(source_blob, dest_bucket, destination_blob_name)
            
            logger.info(f"Copied blob from {source_blob_name} to {destination_blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy blob: {e}")
            return False
    
    def update_blob_metadata(self, 
                           blob_name: str, 
                           metadata: Dict[str, str]) -> bool:
        """
        Update custom metadata for a blob.
        
        Args:
            blob_name: Name of the blob to update
            metadata: Dictionary of metadata key-value pairs
            
        Returns:
            True if update was successful
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(blob_name)
            
            if not blob.exists():
                logger.error(f"Blob not found: {blob_name}")
                return False
            
            blob.metadata = metadata
            blob.patch()
            
            logger.info(f"Updated metadata for blob: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metadata for {blob_name}: {e}")
            return False
    
    def get_blob_content(self, blob_name: str) -> Optional[bytes]:
        """
        Download blob content as bytes.
        
        Args:
            blob_name: Name of the blob to download
            
        Returns:
            Blob content as bytes or None if download fails
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(blob_name)
            
            if not blob.exists():
                logger.error(f"Blob not found: {blob_name}")
                return None
            
            content = blob.download_as_bytes()
            logger.info(f"Downloaded blob content: {blob_name}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to download blob {blob_name}: {e}")
            return None


# Global GCS manager instance
gcs_manager = GCSManager()