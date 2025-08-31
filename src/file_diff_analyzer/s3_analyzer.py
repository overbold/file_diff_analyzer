"""
S3-compatible File Difference Analyzer

Extends the file difference analyzer to work with S3 files directly.
"""

import os
import tempfile
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from .s3_client import S3Client
from .s3_models import S3FileInfo, S3ComparisonRequest, S3ComparisonResult, S3DownloadConfig
from .universal_analyzer import UniversalFileDiffAnalyzer
from .models import AnalysisConfig

logger = logging.getLogger(__name__)


class S3FileDiffAnalyzer:
    """S3-compatible file difference analyzer"""
    
    def __init__(self, 
                 s3_client: Optional[S3Client] = None,
                 analysis_config: Optional[AnalysisConfig] = None,
                 download_config: Optional[S3DownloadConfig] = None):
        """
        Initialize S3 file difference analyzer
        
        Args:
            s3_client: S3 client instance
            analysis_config: Analysis configuration
            download_config: S3 download configuration
        """
        self.s3_client = s3_client
        self.analysis_config = analysis_config or AnalysisConfig()
        self.download_config = download_config or S3DownloadConfig()
        self.universal_analyzer = UniversalFileDiffAnalyzer(analysis_config)
        self.temp_files = []  # Track temporary files for cleanup
        
    def compare_s3_files(self, request: S3ComparisonRequest) -> S3ComparisonResult:
        """
        Compare two S3 files and return detailed analysis
        
        Args:
            request: S3 comparison request with file information
            
        Returns:
            S3ComparisonResult with comparison analysis
        """
        if not self.s3_client:
            raise ValueError("S3 client not initialized")
        
        logger.info(f"Starting S3 file comparison: {request.left_file.file_name} vs {request.right_file.file_name}")
        
        try:
            # Get file information
            left_info = self.s3_client.get_file_info(
                request.left_file.s3_key, 
                request.left_file.bucket_name
            )
            right_info = self.s3_client.get_file_info(
                request.right_file.s3_key, 
                request.right_file.bucket_name
            )
            
            # Download files for analysis
            left_path, left_download_info = self.s3_client.download_file(
                left_info.s3_key, 
                left_info.bucket_name
            )
            right_path, right_download_info = self.s3_client.download_file(
                right_info.s3_key, 
                right_info.bucket_name
            )
            
            # Track temporary files
            self.temp_files.extend([left_path, right_path])
            
            # Perform analysis using universal analyzer
            self.universal_analyzer.add_file(left_path)
            self.universal_analyzer.add_file(right_path)
            
            # Get analysis results
            basic_result = self.universal_analyzer.analyze()
            universal_result = self.universal_analyzer.universal_analyze()
            
            # Prepare comparison result
            comparison_result = {
                "basic_analysis": {
                    "similarity_percentage": basic_result.comparison_matrix[0].similarity_percentage,
                    "difference_percentage": basic_result.comparison_matrix[0].difference_percentage,
                    "is_significantly_different": basic_result.comparison_matrix[0].is_significantly_different,
                    "common_words": basic_result.comparison_matrix[0].common_words,
                    "unique_words_file1": basic_result.comparison_matrix[0].unique_words_file1,
                    "unique_words_file2": basic_result.comparison_matrix[0].unique_words_file2
                },
                "universal_analysis": universal_result,
                "file_metadata": {
                    "left_file": {
                        "s3_key": left_info.s3_key,
                        "bucket": left_info.bucket_name,
                        "size_bytes": left_info.size_bytes,
                        "file_type": left_info.file_type,
                        "last_modified": left_info.last_modified
                    },
                    "right_file": {
                        "s3_key": right_info.s3_key,
                        "bucket": right_info.bucket_name,
                        "size_bytes": right_info.size_bytes,
                        "file_type": right_info.file_type,
                        "last_modified": right_info.last_modified
                    }
                }
            }
            
            # Prepare download status
            download_status = {
                "left_file": {
                    "status": "success",
                    "local_path": left_path,
                    "size_bytes": left_info.size_bytes,
                    "download_time": datetime.now().isoformat()
                },
                "right_file": {
                    "status": "success", 
                    "local_path": right_path,
                    "size_bytes": right_info.size_bytes,
                    "download_time": datetime.now().isoformat()
                }
            }
            
            return S3ComparisonResult(
                left_file=left_info,
                right_file=right_info,
                comparison_result=comparison_result,
                download_status=download_status,
                analysis_timestamp=datetime.now().isoformat(),
                s3_operation_logs=[
                    f"Downloaded {left_info.file_name} from s3://{left_info.bucket_name}/{left_info.s3_key}",
                    f"Downloaded {right_info.file_name} from s3://{right_info.bucket_name}/{right_info.s3_key}",
                    "Analysis completed successfully"
                ]
            )
            
        except Exception as e:
            logger.error(f"S3 file comparison failed: {e}")
            
            # Return error result
            return S3ComparisonResult(
                left_file=request.left_file,
                right_file=request.right_file,
                comparison_result={
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                download_status={
                    "left_file": {"status": "error", "error": str(e)},
                    "right_file": {"status": "error", "error": str(e)}
                },
                analysis_timestamp=datetime.now().isoformat(),
                s3_operation_logs=[f"Analysis failed: {e}"]
            )
    
    def compare_s3_files_simple(self, 
                               left_s3_key: str, 
                               right_s3_key: str,
                               left_bucket: Optional[str] = None,
                               right_bucket: Optional[str] = None) -> Dict[str, Any]:
        """
        Simple S3 file comparison with minimal configuration
        
        Args:
            left_s3_key: S3 key for left file
            right_s3_key: S3 key for right file
            left_bucket: Bucket for left file (extracted from s3_key if not provided)
            right_bucket: Bucket for right file (extracted from s3_key if not provided)
            
        Returns:
            Comparison result dictionary
        """
        # Create simple request
        request = S3ComparisonRequest(
            left_file=S3FileInfo(
                s3_key=left_s3_key,
                bucket_name=left_bucket,
                file_name=os.path.basename(left_s3_key)
            ),
            right_file=S3FileInfo(
                s3_key=right_s3_key,
                bucket_name=right_bucket,
                file_name=os.path.basename(right_s3_key)
            )
        )
        
        result = self.compare_s3_files(request)
        return result.model_dump()  # Use model_dump instead of dict for Pydantic v2
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.s3_client:
            self.s3_client.cleanup_temp_files(self.temp_files)
        self.temp_files.clear()
        logger.info("Cleaned up temporary files")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()
