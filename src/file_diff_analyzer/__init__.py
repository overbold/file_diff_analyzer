"""
File Difference Analyzer Library

A universal library for analyzing differences between files of various formats:
PDF, DOCX, Excel, CSV, TXT and text segments.

Key features:
- Text extraction from files of different formats
- Difference analysis with configurable tolerance threshold
- JSON output format
- Optimized O(n) complexity
- Universal pattern recognition for any file type
- S3 integration for cloud file comparison
"""

from .analyzer import FileDiffAnalyzer
from .universal_analyzer import UniversalFileDiffAnalyzer
from .models import ComparisonResult, FileInfo, DifferenceInfo, AnalysisConfig
from .extractors import TextExtractor

# S3 integration components
from .s3_models import S3FileInfo, S3ComparisonRequest, S3ComparisonResult, S3DownloadConfig
from .s3_client import S3Client
from .s3_analyzer import S3FileDiffAnalyzer

__version__ = "1.1.0"  # Increment version for S3 support
__all__ = [
    "FileDiffAnalyzer",
    "UniversalFileDiffAnalyzer", 
    "ComparisonResult",
    "FileInfo",
    "DifferenceInfo",
    "TextExtractor",
    "AnalysisConfig",
    # S3 components
    "S3FileInfo",
    "S3ComparisonRequest", 
    "S3ComparisonResult",
    "S3DownloadConfig",
    "S3Client",
    "S3FileDiffAnalyzer"
]
