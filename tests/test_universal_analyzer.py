"""
Tests for the UniversalFileDiffAnalyzer class
"""

import pytest
import tempfile
import os
from pathlib import Path

from file_diff_analyzer import UniversalFileDiffAnalyzer, AnalysisConfig, FileType


class TestUniversalFileDiffAnalyzer:
    """Test cases for UniversalFileDiffAnalyzer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = UniversalFileDiffAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test universal analyzer initialization"""
        assert self.analyzer.basic_analyzer is not None
        assert self.analyzer.config is not None
        assert hasattr(self.analyzer, 'patterns')
        assert len(self.analyzer.patterns) > 0
    
    def test_pattern_compilation(self):
        """Test that all patterns are properly compiled"""
        for pattern_name, pattern in self.analyzer.patterns.items():
            assert hasattr(pattern, 'findall')  # Should be a compiled regex
            assert hasattr(pattern, 'search')
            assert hasattr(pattern, 'match')
    
    def test_add_file_delegation(self):
        """Test that add_file delegates to basic analyzer"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Hello world")
        
        self.analyzer.add_file(test_file)
        assert self.analyzer.basic_analyzer.get_file_count() == 1
    
    def test_add_text_delegation(self):
        """Test that add_text delegates to basic analyzer"""
        self.analyzer.add_text("Hello world", "test1")
        assert self.analyzer.basic_analyzer.get_file_count() == 1
    
    def test_analyze_delegation(self):
        """Test that analyze delegates to basic analyzer"""
        self.analyzer.add_text("Hello world", "test1")
        self.analyzer.add_text("Hello universe", "test2")
        
        result = self.analyzer.analyze()
        assert result is not None
        assert len(result.files) == 2
    
    def test_universal_analyze_insufficient_files(self):
        """Test universal analysis with insufficient files"""
        self.analyzer.add_text("Hello", "test1")
        
        with pytest.raises(ValueError, match="Minimum 2 files required"):
            self.analyzer.universal_analyze()
    
    def test_universal_analyze_exactly_two_files(self):
        """Test universal analysis with exactly two files"""
        self.analyzer.add_text("Hello world", "test1")
        self.analyzer.add_text("Hello universe", "test2")
        
        result = self.analyzer.universal_analyze()
        
        assert result is not None
        assert "basic_analysis" in result
        assert "universal_analysis" in result
        assert "summary" in result
    
    def test_universal_analyze_too_many_files(self):
        """Test universal analysis with more than two files"""
        self.analyzer.add_text("File 1", "file1")
        self.analyzer.add_text("File 2", "file2")
        self.analyzer.add_text("File 3", "file3")
        
        result = self.analyzer.universal_analyze()
        
        # Should return error for more than 2 files
        assert "error" in result["universal_analysis"]
    
    def test_numeric_change_detection(self):
        """Test detection of numeric changes"""
        self.analyzer.add_text("Version 1.0 with 100 items", "old")
        self.analyzer.add_text("Version 2.0 with 200 items", "new")
        
        result = self.analyzer.universal_analyze()
        real_changes = result["universal_analysis"]["real_changes"]
        
        # Should detect numeric changes
        numeric_changes = [c for c in real_changes if c["type"] == "numeric_change"]
        assert len(numeric_changes) > 0
    
    def test_version_change_detection(self):
        """Test detection of version changes"""
        self.analyzer.add_text("Software version 1.2.3", "old")
        self.analyzer.add_text("Software version 2.0.0", "new")
        
        result = self.analyzer.universal_analyze()
        real_changes = result["universal_analysis"]["real_changes"]
        
        # Should detect version changes
        version_changes = [c for c in real_changes if c["type"] == "version_change"]
        assert len(version_changes) > 0
    
    def test_date_change_detection(self):
        """Test detection of date changes"""
        self.analyzer.add_text("Last updated: 2024-01-01", "old")
        self.analyzer.add_text("Last updated: 2025-01-01", "new")
        
        result = self.analyzer.universal_analyze()
        real_changes = result["universal_analysis"]["real_changes"]
        
        # Should detect date changes
        date_changes = [c for c in real_changes if c["type"] == "date_change"]
        assert len(date_changes) > 0
    
    def test_url_change_detection(self):
        """Test detection of URL changes"""
        self.analyzer.add_text("Visit http://example.com", "old")
        self.analyzer.add_text("Visit https://example.com", "new")
        
        result = self.analyzer.universal_analyze()
        real_changes = result["universal_analysis"]["real_changes"]
        
        # Should detect URL changes
        url_changes = [c for c in real_changes if c["type"] == "url_change"]
        assert len(url_changes) > 0
    
    def test_email_change_detection(self):
        """Test detection of email changes"""
        self.analyzer.add_text("Contact: old@example.com", "old")
        self.analyzer.add_text("Contact: new@example.com", "new")
        
        result = self.analyzer.universal_analyze()
        real_changes = result["universal_analysis"]["real_changes"]
        
        # Should detect email changes
        email_changes = [c for c in real_changes if c["type"] == "email_change"]
        assert len(email_changes) > 0
    
    def test_line_addition_detection(self):
        """Test detection of line additions"""
        self.analyzer.add_text("Line 1\nLine 2", "old")
        self.analyzer.add_text("Line 1\nNew line\nLine 2", "new")
        
        result = self.analyzer.universal_analyze()
        real_changes = result["universal_analysis"]["real_changes"]
        
        # Should detect line additions
        additions = [c for c in real_changes if c["type"] == "line_addition"]
        assert len(additions) > 0
    
    def test_line_deletion_detection(self):
        """Test detection of line deletions"""
        self.analyzer.add_text("Line 1\nLine to delete\nLine 2", "old")
        self.analyzer.add_text("Line 1\nLine 2", "new")
        
        result = self.analyzer.universal_analyze()
        real_changes = result["universal_analysis"]["real_changes"]
        
        # Should detect line deletions
        deletions = [c for c in real_changes if c["type"] == "line_deletion"]
        assert len(deletions) > 0
    
    def test_structural_shift_detection(self):
        """Test detection of structural shifts"""
        self.analyzer.add_text("Line 1\nLine 2\nLine 3", "old")
        self.analyzer.add_text("Line 1\nInserted line\nLine 2\nLine 3", "new")
        
        result = self.analyzer.universal_analyze()
        structural_changes = result["universal_analysis"]["structural_changes"]
        
        # Should detect structural shifts
        assert len(structural_changes) > 0
    
    def test_line_type_classification(self):
        """Test line type classification"""
        # Test markdown header
        line_type = self.analyzer._classify_line_type("# Header")
        assert line_type == "markdown_header"
        
        # Test numbered list
        line_type = self.analyzer._classify_line_type("1. First item")
        assert line_type == "numbered_list_item"
        
        # Test bullet list
        line_type = self.analyzer._classify_line_type("- Bullet item")
        assert line_type == "bullet_list_item"
        
        # Test code block
        line_type = self.analyzer._classify_line_type("`code`")
        assert line_type == "code_block"
        
        # Test email
        line_type = self.analyzer._classify_line_type("user@example.com")
        assert line_type == "email"
        
        # Test URL
        line_type = self.analyzer._classify_line_type("https://example.com")
        assert line_type == "url"
        
        # Test date
        line_type = self.analyzer._classify_line_type("2025-01-01")
        assert line_type == "date"
        
        # Test numeric
        line_type = self.analyzer._classify_line_type("123.45")
        assert line_type == "numeric"
        
        # Test empty line
        line_type = self.analyzer._classify_line_type("")
        assert line_type == "empty_line"
        
        # Test regular text
        line_type = self.analyzer._classify_line_type("Regular text content")
        assert line_type == "text"
    
    def test_numbered_item_detection(self):
        """Test numbered item detection"""
        assert self.analyzer._is_numbered_item("1. First item") is True
        assert self.analyzer._is_numbered_item("2) Second item") is True
        assert self.analyzer._is_numbered_item("10. Tenth item") is True
        assert self.analyzer._is_numbered_item("Regular text") is False
        assert self.analyzer._is_numbered_item("- Bullet item") is False
    
    def test_bullet_item_detection(self):
        """Test bullet item detection"""
        assert self.analyzer._is_bullet_item("- Bullet item") is True
        assert self.analyzer._is_bullet_item("* Another bullet") is True
        assert self.analyzer._is_bullet_item("+ Plus bullet") is True
        assert self.analyzer._is_bullet_item("Regular text") is False
        assert self.analyzer._is_bullet_item("1. Numbered item") is False
    
    def test_number_extraction(self):
        """Test number extraction from numbered items"""
        assert self.analyzer._extract_number("1. First item") == 1
        assert self.analyzer._extract_number("2) Second item") == 2
        assert self.analyzer._extract_number("10. Tenth item") == 10
        assert self.analyzer._extract_number("Regular text") is None
    
    def test_numeric_impact_assessment(self):
        """Test numeric impact assessment"""
        # Minor change (less than 10%)
        impact = self.analyzer._assess_numeric_impact(["100"], ["105"])
        assert impact == "minor"
        
        # Moderate change (10-100%)
        impact = self.analyzer._assess_numeric_impact(["100"], ["150"])
        assert impact == "moderate"
        
        # Major change (more than 100%)
        impact = self.analyzer._assess_numeric_impact(["100"], ["300"])
        assert impact == "major"
    
    def test_version_impact_assessment(self):
        """Test version impact assessment"""
        # Major version bump
        impact = self.analyzer._assess_version_impact(["1.0.0"], ["2.0.0"])
        assert impact == "major"
        
        # Minor version bump
        impact = self.analyzer._assess_version_impact(["1.0.0"], ["1.1.0"])
        assert impact == "moderate"
        
        # Patch version bump
        impact = self.analyzer._assess_version_impact(["1.0.0"], ["1.0.1"])
        assert impact == "minor"
    
    def test_universal_assessment(self):
        """Test universal assessment calculation"""
        # Test with no significant changes
        analysis = {"real_changes": [{"impact": "none"}]}
        assessment = self.analyzer._get_universal_assessment(analysis)
        assert assessment == "identical"
        
        # Test with few significant changes
        analysis = {"real_changes": [{"impact": "minor"}, {"impact": "moderate"}]}
        assessment = self.analyzer._get_universal_assessment(analysis)
        assert assessment == "very_similar"
        
        # Test with many significant changes
        analysis = {"real_changes": [{"impact": "major"}] * 6}
        assessment = self.analyzer._get_universal_assessment(analysis)
        assert assessment == "moderately_similar"
    
    def test_change_impact_calculation(self):
        """Test change impact calculation"""
        # Test with no significant changes
        analysis = {"real_changes": [{"impact": "none"}]}
        impact = self.analyzer._get_universal_change_impact(analysis)
        assert impact == "no_changes"
        
        # Test with minor changes
        analysis = {"real_changes": [{"impact": "minor"}] * 2}
        impact = self.analyzer._get_universal_change_impact(analysis)
        assert impact == "minor_update"
        
        # Test with major changes
        analysis = {"real_changes": [{"impact": "major"}] * 6}
        impact = self.analyzer._get_universal_change_impact(analysis)
        assert impact == "major_update"
    
    def test_change_categories(self):
        """Test change category calculation"""
        analysis = {
            "real_changes": [
                {"change_category": "data_modification"},
                {"change_category": "version_update"},
                {"change_category": "data_modification"}
            ]
        }
        
        categories = self.analyzer._get_change_categories(analysis)
        assert categories["data_modification"] == 2
        assert categories["version_update"] == 1
    
    def test_export_universal_analysis_to_json(self):
        """Test JSON export of universal analysis"""
        self.analyzer.add_text("Hello world", "test1")
        self.analyzer.add_text("Hello universe", "test2")
        
        json_result = self.analyzer.export_universal_analysis_to_json()
        
        assert isinstance(json_result, str)
        assert len(json_result) > 0
        assert "universal_analysis" in json_result
        assert "summary" in json_result
    
    def test_complex_scenario(self):
        """Test complex analysis scenario with multiple types of changes"""
        old_content = """# Document v1.0
Last updated: 2024-01-01
Contact: old@example.com
Visit: http://example.com

1. First item
2. Second item
3. Third item

Performance: 100 requests/second"""

        new_content = """# Document v2.0
Last updated: 2025-01-01
Contact: new@example.com
Visit: https://example.com

1. First item
2. Second item
3. Third item
4. Fourth item

Performance: 200 requests/second"""

        self.analyzer.add_text(old_content, "old")
        self.analyzer.add_text(new_content, "new")
        
        result = self.analyzer.universal_analyze()
        
        # Should detect various types of changes
        real_changes = result["universal_analysis"]["real_changes"]
        change_types = [c["type"] for c in real_changes]
        
        assert "version_change" in change_types
        assert "date_change" in change_types
        assert "email_change" in change_types
        assert "url_change" in change_types
        assert "numeric_change" in change_types
        assert "line_addition" in change_types
        
        # Summary should be accurate
        summary = result["summary"]
        assert summary["real_changes_count"] > 0
        assert summary["overall_assessment"] in ["very_similar", "similar", "moderately_similar"]
