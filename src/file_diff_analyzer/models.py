"""
Data models for the File Difference Analyzer library

Defines Pydantic models for structured data handling and JSON output.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class FileType(str, Enum):
    """Supported file types"""
    PDF = "pdf"
    DOCX = "docx"
    EXCEL = "excel"
    CSV = "csv"
    TXT = "txt"
    TEXT_SEGMENT = "text_segment"


class FileInfo(BaseModel):
    """Information about a file or text segment"""
    name: str = Field(..., description="File name or text segment identifier")
    file_type: FileType = Field(..., description="Type of file or text segment")
    content: str = Field(..., description="Extracted text content")
    word_count: int = Field(..., description="Number of words in the content")
    line_count: int = Field(..., description="Number of lines in the content")
    size_bytes: Optional[int] = Field(None, description="File size in bytes (if applicable)")


class DifferenceInfo(BaseModel):
    """Information about differences between two files"""
    similarity_percentage: float = Field(..., description="Percentage of similarity between files")
    difference_percentage: float = Field(..., description="Percentage of differences between files")
    common_words: int = Field(..., description="Number of common words between files")
    unique_words_file1: int = Field(..., description="Number of unique words in first file")
    unique_words_file2: int = Field(..., description="Number of unique words in second file")
    is_significantly_different: bool = Field(..., description="Whether files are significantly different based on tolerance")


class ComparisonResult(BaseModel):
    """Result of file comparison analysis"""
    files: List[FileInfo] = Field(..., description="Information about analyzed files")
    comparison_matrix: List[DifferenceInfo] = Field(..., description="Matrix of pairwise comparisons")
    tolerance_threshold: float = Field(..., description="Tolerance threshold used for analysis")
    analysis_timestamp: str = Field(..., description="Timestamp when analysis was performed")


class AnalysisConfig(BaseModel):
    """Configuration for file analysis"""
    tolerance_percentage: float = Field(
        default=30.0, 
        ge=0.0, 
        le=100.0,
        description="Tolerance percentage for determining if files are significantly different"
    )
    enable_word_analysis: bool = Field(
        default=True,
        description="Enable word-level analysis"
    )
    enable_line_analysis: bool = Field(
        default=True,
        description="Enable line-level analysis"
    )
    case_sensitive: bool = Field(
        default=False,
        description="Whether to perform case-sensitive comparison"
    )
    ignore_whitespace: bool = Field(
        default=True,
        description="Whether to ignore whitespace differences"
    )
    max_file_size_mb: float = Field(
        default=100.0,
        ge=0.1,
        le=1000.0,
        description="Maximum file size in MB for analysis"
    )
