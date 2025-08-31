"""
S3-specific models for the File Difference Analyzer library

Defines models for working with S3 files and cloud storage integration.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from .models import FileType


class S3FileInfo(BaseModel):
    """Information about a file stored in S3"""
    model_config = ConfigDict(
        json_encoders={FileType: lambda v: v.value}
    )
    
    s3_key: str = Field(..., description="S3 key/path to the file")
    bucket_name: Optional[str] = Field(None, description="S3 bucket name")
    file_name: str = Field(..., description="Original file name")
    file_type: Optional[FileType] = Field(None, description="Detected file type")
    size_bytes: Optional[int] = Field(None, description="File size in bytes")
    last_modified: Optional[str] = Field(None, description="Last modified timestamp")
    etag: Optional[str] = Field(None, description="S3 ETag for versioning")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional S3 metadata")


class S3ComparisonRequest(BaseModel):
    """Request for comparing two S3 files"""
    left_file: S3FileInfo = Field(..., description="Left file for comparison")
    right_file: S3FileInfo = Field(..., description="Right file for comparison")
    analysis_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Analysis configuration")
    download_options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="S3 download options")


class S3ComparisonResult(BaseModel):
    """Result of S3 file comparison"""
    left_file: S3FileInfo = Field(..., description="Left file information")
    right_file: S3FileInfo = Field(..., description="Right file information")
    comparison_result: Dict[str, Any] = Field(..., description="Comparison analysis result")
    download_status: Dict[str, Any] = Field(..., description="S3 download status for both files")
    analysis_timestamp: str = Field(..., description="When analysis was performed")
    s3_operation_logs: List[str] = Field(default_factory=list, description="S3 operation logs")


class S3DownloadConfig(BaseModel):
    """Configuration for S3 file downloads"""
    chunk_size: int = Field(default=8192, description="Download chunk size in bytes")
    max_retries: int = Field(default=3, description="Maximum download retry attempts")
    timeout_seconds: int = Field(default=300, description="Download timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Whether to verify SSL certificates")
    use_temp_files: bool = Field(default=True, description="Whether to use temporary files for downloads")
    temp_dir: Optional[str] = Field(None, description="Custom temporary directory path")

