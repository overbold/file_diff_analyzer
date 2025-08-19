"""
Core File Difference Analyzer

Main analyzer class for comparing files and detecting differences
with configurable tolerance thresholds.
"""

import re
from datetime import datetime
from typing import List, Set
from .models import FileInfo, DifferenceInfo, ComparisonResult, AnalysisConfig, FileType
from .extractors import TextExtractor


class FileDiffAnalyzer:
    """Main analyzer for detecting differences between files"""
    
    def __init__(self, config: AnalysisConfig = None):
        self.config = config or AnalysisConfig()
        self._files: List[FileInfo] = []
        self._text_extractor = TextExtractor()
    
    def add_file(self, file_path: str) -> 'FileDiffAnalyzer':
        """Adds a file for analysis"""
        text, file_type, size_bytes = self._text_extractor.get_file_info(file_path)
        
        file_info = FileInfo(
            name=file_path,
            file_type=file_type,
            content=text,
            word_count=len(text.split()),
            line_count=len(text.split('\n')),
            size_bytes=size_bytes
        )
        
        self._files.append(file_info)
        return self
    
    def add_text(self, text: str, name: str = "text_segment") -> 'FileDiffAnalyzer':
        """Adds a text segment for analysis"""
        file_info = FileInfo(
            name=name,
            file_type=FileType.TEXT_SEGMENT,
            content=text,
            word_count=len(text.split()),
            line_count=len(text.split('\n')),
            size_bytes=len(text.encode('utf-8'))
        )
        
        self._files.append(file_info)
        return self
    
    def analyze(self) -> ComparisonResult:
        """Performs analysis of all added files"""
        if len(self._files) < 2:
            raise ValueError("At least 2 files required for analysis")
        
        comparison_matrix = []
        
        # Perform pairwise comparisons
        for i in range(len(self._files)):
            for j in range(i + 1, len(self._files)):
                diff_info = self._compare_files(self._files[i], self._files[j])
                comparison_matrix.append(diff_info)
        
        return ComparisonResult(
            files=self._files,
            comparison_matrix=comparison_matrix,
            tolerance_threshold=self.config.tolerance_percentage,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _compare_files(self, file1: FileInfo, file2: FileInfo) -> DifferenceInfo:
        """Compares two files and returns difference information"""
        # Check if any file is PDF - if so, normalize structure by removing empty lines from non-PDF files
        has_pdf = file1.file_type == FileType.PDF or file2.file_type == FileType.PDF
        
        # Extract words from both files with conditional normalization
        words1 = self._extract_words(file1.content, normalize_structure=(has_pdf and file1.file_type != FileType.PDF))
        words2 = self._extract_words(file2.content, normalize_structure=(has_pdf and file2.file_type != FileType.PDF))
        
        # Calculate set operations
        common_words = words1.intersection(words2)
        unique_words_file1 = words1 - words2
        unique_words_file2 = words2 - words1
        
        # Calculate percentages
        total_unique_words = len(unique_words_file1) + len(unique_words_file2)
        total_words = len(words1) + len(words2)
        
        if total_words == 0:
            similarity_percentage = 100.0
            difference_percentage = 0.0
        else:
            similarity_percentage = (len(common_words) * 2 / total_words) * 100
            difference_percentage = (total_unique_words / total_words) * 100
        
        # Determine if files are significantly different
        is_significantly_different = difference_percentage > self.config.tolerance_percentage
        
        return DifferenceInfo(
            similarity_percentage=round(similarity_percentage, 2),
            difference_percentage=round(difference_percentage, 2),
            common_words=len(common_words),
            unique_words_file1=len(unique_words_file1),
            unique_words_file2=len(unique_words_file2),
            is_significantly_different=is_significantly_different
        )
    
    def _extract_words(self, text: str, normalize_structure: bool = False) -> Set[str]:
        """Extracts and normalizes words from text"""
        if not text:
            return set()
        
        # Apply configuration options
        if not self.config.case_sensitive:
            text = text.lower()
        
        # Conditionally normalize structure - only if requested (for non-PDF files when PDF is involved)
        if normalize_structure:
            # Remove empty lines to normalize structure across different file formats
            # This ensures PDF, TXT, DOCX files are compared consistently
            lines = text.split('\n')
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            normalized_text = '\n'.join(non_empty_lines)
        else:
            # Keep original structure (for PDF files or when no PDF is involved)
            normalized_text = text
        
        if self.config.ignore_whitespace:
            # Split by whitespace and filter empty strings
            words = [word.strip() for word in normalized_text.split() if word.strip()]
        else:
            # Split by newlines and spaces, preserve structure
            words = []
            for line in normalized_text.split('\n'):
                line_words = [word.strip() for word in line.split() if word.strip()]
                words.extend(line_words)
        
        # Remove punctuation and special characters
        cleaned_words = []
        for word in words:
            cleaned_word = re.sub(r'[^\w\s]', '', word)
            if cleaned_word:
                cleaned_words.append(cleaned_word)
        
        return set(cleaned_words)
    
    def get_file_count(self) -> int:
        """Returns the number of files added for analysis"""
        return len(self._files)
    
    def clear_files(self):
        """Clears all added files"""
        self._files.clear()
    
    def get_file_names(self) -> List[str]:
        """Returns names of all added files"""
        return [file.name for file in self._files]
    
    def get_file_types(self) -> List[FileType]:
        """Returns types of all added files"""
        return [file.file_type for file in self._files]
    
    def export_to_json(self) -> str:
        """Exports analysis results to JSON string"""
        result = self.analyze()
        return result.model_dump_json(indent=2)
