"""
S3 Client for File Difference Analyzer

Handles S3 file operations including downloads, metadata extraction, and file processing.
"""

import os
import tempfile
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from .s3_models import S3FileInfo, S3DownloadConfig
from .extractors import TextExtractor
import time

logger = logging.getLogger(__name__)


class S3Client:
    """Client for S3 operations in file difference analysis"""
    
    def __init__(self, 
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 region_name: Optional[str] = None,
                 endpoint_url: Optional[str] = None,
                 download_config: Optional[S3DownloadConfig] = None):
        """
        Initialize S3 client
        
        Args:
            aws_access_key_id: AWS access key
            aws_secret_access_key: AWS secret key  
            region_name: AWS region
            endpoint_url: Custom S3 endpoint (for MinIO, etc.)
            download_config: Download configuration
        """
        self.download_config = download_config or S3DownloadConfig()
        self.text_extractor = TextExtractor()
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
                endpoint_url=endpoint_url
            )
            logger.info("S3 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    def get_file_info(self, s3_key: str, bucket_name: Optional[str] = None) -> S3FileInfo:
        """
        Get information about an S3 file
        
        Args:
            s3_key: S3 key/path to the file
            bucket_name: S3 bucket name (extracted from s3_key if not provided)
            
        Returns:
            S3FileInfo with file metadata
        """
        if not bucket_name:
            # Extract bucket from s3_key if it's a full S3 URI
            if s3_key.startswith('s3://'):
                parts = s3_key[5:].split('/', 1)
                bucket_name = parts[0]
                s3_key = parts[1] if len(parts) > 1 else ""
            else:
                raise ValueError("bucket_name required if s3_key is not a full S3 URI")
        
        try:
            # Get file metadata
            response = self.s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            
            # Extract file name from key
            file_name = os.path.basename(s3_key) if s3_key else "unknown"
            
            # Detect file type from extension
            file_type = self._detect_file_type(file_name)
            
            return S3FileInfo(
                s3_key=s3_key,
                bucket_name=bucket_name,
                file_name=file_name,
                file_type=file_type,
                size_bytes=response.get('ContentLength'),
                last_modified=response.get('LastModified', '').isoformat() if response.get('LastModified') else None,
                etag=response.get('ETag', '').strip('"') if response.get('ETag') else None,
                metadata=response.get('Metadata', {})
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise FileNotFoundError(f"File not found: s3://{bucket_name}/{s3_key}")
            elif error_code == 'NoSuchBucket':
                raise FileNotFoundError(f"Bucket not found: {bucket_name}")
            else:
                raise Exception(f"S3 error: {error_code} - {e}")
    
    def download_file(self, s3_key: str, bucket_name: Optional[str] = None) -> Tuple[str, S3FileInfo]:
        """
        Download a file from S3 to temporary location
        
        Args:
            s3_key: S3 key/path to the file
            bucket_name: S3 bucket name
            
        Returns:
            Tuple of (local_file_path, S3FileInfo)
        """
        file_info = self.get_file_info(s3_key, bucket_name)
        
        # Create temporary file
        if self.download_config.use_temp_files:
            temp_dir = self.download_config.temp_dir or tempfile.gettempdir()
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                dir=temp_dir,
                suffix=os.path.splitext(file_info.file_name)[1]
            )
            local_path = temp_file.name
            temp_file.close()
        else:
            local_path = os.path.join(tempfile.gettempdir(), file_info.file_name)
        
        try:
            logger.info(f"Downloading s3://{file_info.bucket_name}/{file_info.s3_key} to {local_path}")
            
            # Download file with retries
            for attempt in range(self.download_config.max_retries):
                try:
                    self.s3_client.download_file(
                        file_info.bucket_name,
                        file_info.s3_key,
                        local_path,
                        Config=boto3.s3.transfer.TransferConfig(
                            multipart_threshold=1024 * 25,
                            max_concurrency=10,
                            multipart_chunksize=1024 * 25,
                            use_threads=True
                        )
                    )
                    logger.info(f"Successfully downloaded file to {local_path}")
                    break
                    
                except Exception as e:
                    if attempt == self.download_config.max_retries - 1:
                        raise Exception(f"Failed to download after {self.download_config.max_retries} attempts: {e}")
                    logger.warning(f"Download attempt {attempt + 1} failed: {e}, retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            return local_path, file_info
            
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(local_path):
                os.unlink(local_path)
            raise Exception(f"Failed to download file: {e}")
    
    def extract_text_from_s3(self, s3_key: str, bucket_name: Optional[str] = None) -> Tuple[str, S3FileInfo]:
        """
        Extract text content directly from S3 file
        
        Args:
            s3_key: S3 key/path to the file
            bucket_name: S3 bucket name
            
        Returns:
            Tuple of (extracted_text, S3FileInfo)
        """
        file_info = self.get_file_info(s3_key, bucket_name)
        
        try:
            # Get file object
            response = self.s3_client.get_object(Bucket=file_info.bucket_name, Key=file_info.s3_key)
            
            # Extract text based on file type
            if file_info.file_type in ['pdf', 'docx', 'txt']:
                # For text-based files, download and extract
                local_path, _ = self.download_file(s3_key, bucket_name)
                try:
                    text, _, _ = self.text_extractor.get_file_info(local_path)
                    return text, file_info
                finally:
                    # Clean up temporary file
                    if os.path.exists(local_path):
                        os.unlink(local_path)
            else:
                # For other file types, return placeholder
                return f"[{file_info.file_type.upper()} file content not extractable]", file_info
                
        except Exception as e:
            logger.error(f"Failed to extract text from S3 file: {e}")
            return f"[Error extracting text: {e}]", file_info
    
    def _detect_file_type(self, file_name: str) -> Optional[str]:
        """Detect file type from file name extension"""
        if not file_name:
            return None
            
        ext = os.path.splitext(file_name)[1].lower()
        
        type_mapping = {
            '.pdf': 'pdf',
            '.docx': 'docx', 
            '.doc': 'docx',
            '.xlsx': 'excel',
            '.xls': 'excel',
            '.csv': 'csv',
            '.txt': 'txt',
            '.md': 'txt'
        }
        
        return type_mapping.get(ext)
    
    def cleanup_temp_files(self, file_paths: list):
        """Clean up temporary files"""
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {file_path}: {e}")
