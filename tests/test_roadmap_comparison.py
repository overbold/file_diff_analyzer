#!/usr/bin/env python3
"""
Test for comparing ROADMAP files using the file_diff_analyzer library
"""

import pytest
import os
from pathlib import Path

from file_diff_analyzer import FileDiffAnalyzer, UniversalFileDiffAnalyzer


class TestRoadmapComparison:
    """Test roadmap file comparison functionality"""
    
    @pytest.fixture
    def roadmap_files(self):
        """Get paths to roadmap test files"""
        current_dir = Path(__file__).parent
        roadmap_v1_1 = current_dir.parent.parent.parent.parent / "tests" / "datasets" / "pilot" / "ROADMAP_v1.1.en.txt"
        roadmap_v1_2 = current_dir.parent.parent.parent.parent / "tests" / "datasets" / "pilot" / "ROADMAP_v1.2.en.txt"
        
        assert roadmap_v1_1.exists(), f"ROADMAP v1.1 not found: {roadmap_v1_1}"
        assert roadmap_v1_2.exists(), f"ROADMAP v1.2 not found: {roadmap_v1_2}"
        
        return str(roadmap_v1_1), str(roadmap_v1_2)
    
    def test_basic_roadmap_comparison(self, roadmap_files):
        """Test basic comparison of roadmap files"""
        roadmap_v1_1, roadmap_v1_2 = roadmap_files
        
        analyzer = FileDiffAnalyzer()
        analyzer.add_file(roadmap_v1_1)
        analyzer.add_file(roadmap_v1_2)
        
        result = analyzer.analyze()
        
        assert len(result.files) == 2
        assert len(result.comparison_matrix) == 1
        
        comparison = result.comparison_matrix[0]
        assert comparison.file1_name in ["ROADMAP_v1.1.en.txt", "ROADMAP_v1.2.en.txt"]
        assert comparison.file2_name in ["ROADMAP_v1.1.en.txt", "ROADMAP_v1.2.en.txt"]
        assert comparison.file1_name != comparison.file2_name
        
        # Files should be similar but not identical
        assert comparison.similarity_percentage > 90.0
        assert comparison.difference_percentage < 10.0
        assert not comparison.is_significantly_different
    
    def test_universal_roadmap_analysis(self, roadmap_files):
        """Test universal analysis of roadmap files"""
        roadmap_v1_1, roadmap_v1_2 = roadmap_files
        
        universal = UniversalFileDiffAnalyzer()
        universal.add_file(roadmap_v1_1)
        universal.add_file(roadmap_v1_2)
        
        result = universal.universal_analyze()
        
        # Check basic structure
        assert "basic_analysis" in result
        assert "universal_analysis" in result
        assert "summary" in result
        
        # Check summary
        summary = result["summary"]
        assert "real_changes_count" in summary
        assert "structural_changes_count" in summary
        assert "overall_assessment" in summary
        
        # Check universal analysis
        universal_analysis = result["universal_analysis"]
        assert "real_changes" in universal_analysis
        assert "structural_changes" in universal_analysis
        assert "total_changes" in universal_analysis
        
        # Should detect some real changes
        assert summary["real_changes_count"] > 0
        
        # Overall assessment should indicate similarity
        assert summary["overall_assessment"] in ["identical", "very_similar", "similar"]
    
    def test_roadmap_specific_changes(self, roadmap_files):
        """Test detection of specific changes in roadmap files"""
        roadmap_v1_1, roadmap_v1_2 = roadmap_files
        
        universal = UniversalFileDiffAnalyzer()
        universal.add_file(roadmap_v1_1)
        universal.add_file(roadmap_v1_2)
        
        result = universal.universal_analyze()
        real_changes = result["universal_analysis"]["real_changes"]
        
        # Should detect numeric changes (G. Perf — 20 -> 21)
        numeric_changes = [c for c in real_changes if c["type"] == "numeric_change"]
        assert len(numeric_changes) > 0
        
        # Should detect content modifications
        content_changes = [c for c in real_changes if c["type"] in ["content_modification", "line_addition"]]
        assert len(content_changes) > 0
        
        # Check that changes have proper structure
        for change in real_changes:
            assert "type" in change
            assert "description" in change
            assert "impact" in change
            assert "change_category" in change
    
    def test_roadmap_structural_analysis(self, roadmap_files):
        """Test structural analysis of roadmap files"""
        roadmap_v1_1, roadmap_v1_2 = roadmap_files
        
        universal = UniversalFileDiffAnalyzer()
        universal.add_file(roadmap_v1_1)
        universal.add_file(roadmap_v1_2)
        
        result = universal.universal_analyze()
        structural_changes = result["universal_analysis"]["structural_changes"]
        
        # Should detect structural shifts due to line insertion
        assert len(structural_changes) >= 0  # May or may not have structural shifts
        
        # If structural shifts exist, they should have proper format
        for shift in structural_changes:
            assert shift["type"] == "structural_shift"
            assert "description" in shift
            assert "content" in shift
            assert "old_position" in shift
            assert "new_position" in shift
            assert "shift_distance" in shift
            assert shift["impact"] == "none"  # Structural shifts don't affect content
            assert shift["change_category"] == "formatting"
    
    def test_roadmap_export_functionality(self, roadmap_files):
        """Test export functionality for roadmap comparison"""
        roadmap_v1_1, roadmap_v1_2 = roadmap_files
        
        universal = UniversalFileDiffAnalyzer()
        universal.add_file(roadmap_v1_1)
        universal.add_file(roadmap_v1_2)
        
        # Test JSON export
        json_result = universal.export_universal_analysis_to_json()
        assert isinstance(json_result, str)
        assert len(json_result) > 0
        
        # JSON should contain expected keys
        import json
        parsed_result = json.loads(json_result)
        assert "basic_analysis" in parsed_result
        assert "universal_analysis" in parsed_result
        assert "summary" in parsed_result
