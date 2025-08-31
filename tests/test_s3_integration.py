"""
Tests for S3 integration in File Difference Analyzer

Tests S3 client, models, and analyzer functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from file_diff_analyzer.s3_models import (
    S3FileInfo, S3ComparisonRequest, S3ComparisonResult, S3DownloadConfig
)
from file_diff_analyzer.s3_client import S3Client
from file_diff_analyzer.s3_analyzer import S3FileDiffAnalyzer
from file_diff_analyzer.models import FileType


class TestS3Models:
    """Test S3-specific data models"""
    
    def test_s3_file_info_creation(self):
        """Test S3FileInfo model creation"""
        file_info = S3FileInfo(
            s3_key="test/file.pdf",
            bucket_name="test-bucket",
            file_name="test.pdf",
            file_type=FileType.PDF,
            size_bytes=1024
        )
        
        assert file_info.s3_key == "test/file.pdf"
        assert file_info.bucket_name == "test-bucket"
        assert file_info.file_name == "test.pdf"
        assert file_info.file_type == FileType.PDF
        assert file_info.size_bytes == 1024
    
    def test_s3_comparison_request(self):
        """Test S3ComparisonRequest model creation"""
        left_file = S3FileInfo(
            s3_key="left/file.pdf",
            bucket_name="test-bucket",
            file_name="left.pdf"
        )
        right_file = S3FileInfo(
            s3_key="right/file.pdf", 
            bucket_name="test-bucket",
            file_name="right.pdf"
        )
        
        request = S3ComparisonRequest(
            left_file=left_file,
            right_file=right_file,
            analysis_config={"tolerance_percentage": 20.0}
        )
        
        assert request.left_file == left_file
        assert request.right_file == right_file
        assert request.analysis_config["tolerance_percentage"] == 20.0
    
    def test_s3_download_config_defaults(self):
        """Test S3DownloadConfig default values"""
        config = S3DownloadConfig()
        
        assert config.chunk_size == 8192
        assert config.max_retries == 3
        assert config.timeout_seconds == 300
        assert config.verify_ssl is True
        assert config.use_temp_files is True


class TestS3Client:
    """Test S3 client functionality"""
    
    @patch('boto3.client')
    def test_s3_client_initialization(self, mock_boto3):
        """Test S3 client initialization"""
        mock_s3 = Mock()
        mock_boto3.return_value = mock_s3
        
        client = S3Client(
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret",
            region_name="us-east-1"
        )
        
        assert client.s3_client == mock_s3
        mock_boto3.assert_called_once_with(
            's3',
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret", 
            region_name="us-east-1",
            endpoint_url=None
        )
    
    def test_detect_file_type(self):
        """Test file type detection from filename"""
        client = S3Client()
        
        assert client._detect_file_type("test.pdf") == "pdf"
        assert client._detect_file_type("document.docx") == "docx"
        assert client._detect_file_type("data.xlsx") == "excel"
        assert client._detect_file_type("info.txt") == "txt"
        assert client._detect_file_type("unknown.xyz") is None


class TestS3Analyzer:
    """Test S3 file analyzer functionality"""
    
    def test_s3_analyzer_initialization(self):
        """Test S3 analyzer initialization"""
        mock_s3_client = Mock()
        analyzer = S3FileDiffAnalyzer(s3_client=mock_s3_client)
        
        assert analyzer.s3_client == mock_s3_client
        assert analyzer.temp_files == []
        assert analyzer.universal_analyzer is not None
    
    def test_s3_analyzer_cleanup(self):
        """Test temporary file cleanup"""
        mock_s3_client = Mock()
        analyzer = S3FileDiffAnalyzer(s3_client=mock_s3_client)
        
        # Add some mock temp files
        analyzer.temp_files = ["/tmp/file1.pdf", "/tmp/file2.pdf"]
        
        analyzer.cleanup()
        
        mock_s3_client.cleanup_temp_files.assert_called_once_with([
            "/tmp/file1.pdf", "/tmp/file2.pdf"
        ])
        assert analyzer.temp_files == []
    
    def test_context_manager(self):
        """Test context manager functionality"""
        mock_s3_client = Mock()
        
        with S3FileDiffAnalyzer(s3_client=mock_s3_client) as analyzer:
            analyzer.temp_files = ["/tmp/test.pdf"]
        
        # Should call cleanup on exit
        mock_s3_client.cleanup_temp_files.assert_called_once_with(["/tmp/test.pdf"])


class TestS3Integration:
    """Integration tests for S3 functionality"""
    
    @patch('boto3.client')
    def test_full_s3_comparison_flow(self, mock_boto3):
        """Test complete S3 comparison flow with mocked S3"""
        # Mock S3 client
        mock_s3 = Mock()
        mock_boto3.return_value = mock_s3
        
        # Mock S3 responses
        mock_s3.head_object.side_effect = [
            {
                'ContentLength': 1024,
                'LastModified': datetime.now(),
                'ETag': '"test-etag-1"',
                'Metadata': {}
            },
            {
                'ContentLength': 2048,
                'LastModified': datetime.now(),
                'ETag': '"test-etag-2"',
                'Metadata': {}
            }
        ]
        
        # Mock download
        mock_s3.download_file.return_value = None
        
        # Create temporary test files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f2:
            
            f1.write("This is test file 1")
            f2.write("This is test file 2")
            f1_path, f2_path = f1.name, f2.name
        
        try:
            # Initialize components
            s3_client = S3Client()
            analyzer = S3FileDiffAnalyzer(s3_client=s3_client)
            
            # Mock the download_file method to return our test files
            s3_client.download_file = Mock(return_value=(f1_path, Mock()))
            s3_client.download_file.side_effect = [
                (f1_path, Mock()),
                (f2_path, Mock())
            ]
            
            # Perform comparison
            result = analyzer.compare_s3_files_simple(
                "s3://test-bucket/file1.txt",
                "s3://test-bucket/file2.txt"
            )
            
            # Verify results
            assert "comparison_result" in result
            assert "basic_analysis" in result["comparison_result"]
            
            basic = result["comparison_result"]["basic_analysis"]
            assert "similarity_percentage" in basic
            assert "difference_percentage" in basic
            
        finally:
            # Cleanup
            analyzer.cleanup()
            os.unlink(f1_path)
            os.unlink(f2_path)


if __name__ == "__main__":
    pytest.main([__file__])
