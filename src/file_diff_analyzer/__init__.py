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
"""

from .analyzer import FileDiffAnalyzer
from .universal_analyzer import UniversalFileDiffAnalyzer
from .models import ComparisonResult, FileInfo, DifferenceInfo, AnalysisConfig
from .extractors import TextExtractor

__version__ = "1.0.0"
__all__ = [
    "FileDiffAnalyzer",
    "UniversalFileDiffAnalyzer", 
    "ComparisonResult",
    "FileInfo",
    "DifferenceInfo",
    "TextExtractor",
    "AnalysisConfig"
]
