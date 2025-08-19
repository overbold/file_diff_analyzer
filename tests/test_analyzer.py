"""
Tests for the main FileDiffAnalyzer class
"""

import pytest
import tempfile
import os
from pathlib import Path

from file_diff_analyzer import FileDiffAnalyzer, AnalysisConfig, FileType


class TestFileDiffAnalyzer:
    """Test cases for FileDiffAnalyzer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = FileDiffAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test analyzer initialization"""
        assert self.analyzer.config is not None
        assert self.analyzer.get_file_count() == 0
        assert isinstance(self.analyzer.config, AnalysisConfig)
    
    def test_custom_config_initialization(self):
        """Test analyzer with custom configuration"""
        config = AnalysisConfig(tolerance_percentage=25.0, case_sensitive=True)
        analyzer = FileDiffAnalyzer(config)
        assert analyzer.config.tolerance_percentage == 25.0
        assert analyzer.config.case_sensitive is True
    
    def test_add_text(self):
        """Test adding text segments"""
        self.analyzer.add_text("Hello world", "test1")
        self.analyzer.add_text("Hello universe", "test2")
        
        assert self.analyzer.get_file_count() == 2
        assert "test1" in self.analyzer.get_file_names()
        assert "test2" in self.analyzer.get_file_names()
    
    def test_add_file_txt(self):
        """Test adding text files"""
        # Create test text file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Hello world\nThis is a test file")
        
        self.analyzer.add_file(test_file)
        
        assert self.analyzer.get_file_count() == 1
        assert self.analyzer.get_file_types()[0] == FileType.TXT
    
    def test_analyze_insufficient_files(self):
        """Test analysis with insufficient files"""
        self.analyzer.add_text("Hello", "test1")
        
        with pytest.raises(ValueError, match="At least 2 files required"):
            self.analyzer.analyze()
    
    def test_basic_analysis(self):
        """Test basic file analysis"""
        self.analyzer.add_text("Hello world", "test1")
        self.analyzer.add_text("Hello universe", "test2")
        
        result = self.analyzer.analyze()
        
        assert result is not None
        assert len(result.files) == 2
        assert len(result.comparison_matrix) == 1
        assert result.tolerance_threshold == 30.0
        
        comparison = result.comparison_matrix[0]
        assert comparison.similarity_percentage > 0
        assert comparison.difference_percentage > 0
        assert comparison.common_words > 0
    
    def test_identical_files(self):
        """Test analysis of identical files"""
        self.analyzer.add_text("Hello world", "test1")
        self.analyzer.add_text("Hello world", "test2")
        
        result = self.analyzer.analyze()
        comparison = result.comparison_matrix[0]
        
        assert comparison.similarity_percentage == 100.0
        assert comparison.difference_percentage == 0.0
        assert comparison.is_significantly_different is False
    
    def test_completely_different_files(self):
        """Test analysis of completely different files"""
        self.analyzer.add_text("Hello world", "test1")
        self.analyzer.add_text("Completely different content", "test2")
        
        result = self.analyzer.analyze()
        comparison = result.comparison_matrix[0]
        
        assert comparison.similarity_percentage < 50.0
        assert comparison.difference_percentage > 50.0
        assert comparison.is_significantly_different is True
    
    def test_tolerance_threshold(self):
        """Test custom tolerance threshold"""
        config = AnalysisConfig(tolerance_percentage=10.0)
        analyzer = FileDiffAnalyzer(config)
        
        analyzer.add_text("Hello world", "test1")
        analyzer.add_text("Hello universe", "test2")
        
        result = analyzer.analyze()
        comparison = result.comparison_matrix[0]
        
        # With 10% tolerance, these should be significantly different
        assert comparison.is_significantly_different is True
    
    def test_case_sensitive_analysis(self):
        """Test case-sensitive analysis"""
        config = AnalysisConfig(case_sensitive=True)
        analyzer = FileDiffAnalyzer(config)
        
        analyzer.add_text("Hello World", "test1")
        analyzer.add_text("hello world", "test2")
        
        result = analyzer.analyze()
        comparison = result.comparison_matrix[0]
        
        # Case-sensitive should show more differences
        assert comparison.difference_percentage > 0
    
    def test_case_insensitive_analysis(self):
        """Test case-insensitive analysis"""
        config = AnalysisConfig(case_sensitive=False)
        analyzer = FileDiffAnalyzer(config)
        
        analyzer.add_text("Hello World", "test1")
        analyzer.add_text("hello world", "test2")
        
        result = analyzer.analyze()
        comparison = result.comparison_matrix[0]
        
        # Case-insensitive should show fewer differences
        assert comparison.similarity_percentage > 0
    
    def test_whitespace_handling(self):
        """Test whitespace handling"""
        config = AnalysisConfig(ignore_whitespace=True)
        analyzer = FileDiffAnalyzer(config)
        
        analyzer.add_text("Hello world", "test1")
        analyzer.add_text("  Hello   world  ", "test2")
        
        result = analyzer.analyze()
        comparison = result.comparison_matrix[0]
        
        # Should be very similar when ignoring whitespace
        assert comparison.similarity_percentage > 90.0
    
    def test_multiple_files(self):
        """Test analysis of multiple files"""
        self.analyzer.add_text("File 1 content", "file1")
        self.analyzer.add_text("File 2 content", "file2")
        self.analyzer.add_text("File 3 content", "file3")
        
        result = self.analyzer.analyze()
        
        # 3 files = 3 comparisons (1-2, 1-3, 2-3)
        assert len(result.comparison_matrix) == 3
        assert len(result.files) == 3
    
    def test_export_to_json(self):
        """Test JSON export functionality"""
        self.analyzer.add_text("Hello world", "test1")
        self.analyzer.add_text("Hello universe", "test2")
        
        json_result = self.analyzer.export_to_json()
        
        assert isinstance(json_result, str)
        assert len(json_result) > 0
        assert "test1" in json_result
        assert "test2" in json_result
    
    def test_clear_files(self):
        """Test clearing all files"""
        self.analyzer.add_text("Hello", "test1")
        self.analyzer.add_text("World", "test2")
        
        assert self.analyzer.get_file_count() == 2
        
        self.analyzer.clear_files()
        
        assert self.analyzer.get_file_count() == 0
        assert len(self.analyzer.get_file_names()) == 0
    
    def test_get_file_info(self):
        """Test getting file information"""
        self.analyzer.add_text("Hello world\nSecond line", "test1")
        
        file_names = self.analyzer.get_file_names()
        file_types = self.analyzer.get_file_types()
        
        assert len(file_names) == 1
        assert file_names[0] == "test1"
        assert file_types[0] == FileType.TEXT_SEGMENT
    
    def test_empty_text_handling(self):
        """Test handling of empty text"""
        self.analyzer.add_text("", "empty1")
        self.analyzer.add_text("", "empty2")
        
        result = self.analyzer.analyze()
        comparison = result.comparison_matrix[0]
        
        # Empty files should be identical
        assert comparison.similarity_percentage == 100.0
        assert comparison.difference_percentage == 0.0
    
    def test_special_characters(self):
        """Test handling of special characters"""
        self.analyzer.add_text("Hello @world! #test", "special1")
        self.analyzer.add_text("Hello world test", "special2")
        
        result = self.analyzer.analyze()
        comparison = result.comparison_matrix[0]
        
        # Should handle special characters appropriately
        assert comparison.similarity_percentage > 0
        assert comparison.difference_percentage > 0
    
    def test_large_text_handling(self):
        """Test handling of large text segments"""
        large_text = "Hello world " * 1000  # 12,000 words
        
        self.analyzer.add_text(large_text, "large1")
        self.analyzer.add_text(large_text + " extra", "large2")
        
        result = self.analyzer.analyze()
        comparison = result.comparison_matrix[0]
        
        # Should handle large texts efficiently
        assert comparison.similarity_percentage > 95.0
        assert comparison.difference_percentage < 5.0


class TestAnalysisConfig:
    """Test cases for AnalysisConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = AnalysisConfig()
        
        assert config.tolerance_percentage == 30.0
        assert config.enable_word_analysis is True
        assert config.enable_line_analysis is True
        assert config.case_sensitive is False
        assert config.ignore_whitespace is True
        assert config.max_file_size_mb == 100.0
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = AnalysisConfig(
            tolerance_percentage=15.0,
            case_sensitive=True,
            ignore_whitespace=False,
            max_file_size_mb=50.0
        )
        
        assert config.tolerance_percentage == 15.0
        assert config.case_sensitive is True
        assert config.ignore_whitespace is False
        assert config.max_file_size_mb == 50.0
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid tolerance
        config = AnalysisConfig(tolerance_percentage=50.0)
        assert config.tolerance_percentage == 50.0
        
        # Edge cases
        config = AnalysisConfig(tolerance_percentage=0.0)
        assert config.tolerance_percentage == 0.0
        
        config = AnalysisConfig(tolerance_percentage=100.0)
        assert config.tolerance_percentage == 100.0
    
    def test_config_immutability(self):
        """Test that configuration is immutable after creation"""
        config = AnalysisConfig(tolerance_percentage=25.0)
        
        # Should not be able to modify after creation
        with pytest.raises(AttributeError):
            config.tolerance_percentage = 50.0
