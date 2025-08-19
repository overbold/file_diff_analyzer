#!/usr/bin/env python3
"""
Universal Analysis Example for File Difference Analyzer

This example demonstrates the advanced universal analysis capabilities.
"""

from file_diff_analyzer import UniversalFileDiffAnalyzer, AnalysisConfig


def universal_analysis_example():
    """Universal analysis example with intelligent change detection"""
    print("🧠 Universal Analysis Example")
    print("=" * 50)
    
    # Create universal analyzer
    analyzer = UniversalFileDiffAnalyzer()
    
    # Create content with various types of changes
    old_content = """# Project Documentation v1.0
Last updated: 2024-01-15
Contact: developer@example.com
Website: http://example.com

## Features
1. Basic functionality
2. User authentication
3. Data processing

## Performance
- Response time: 100ms
- Throughput: 1000 requests/second
- Memory usage: 512MB

## Configuration
API_VERSION=1.0
DEBUG_MODE=false
MAX_CONNECTIONS=100"""

    new_content = """# Project Documentation v2.0
Last updated: 2025-01-15
Contact: team@example.com
Website: https://example.com

## Features
1. Basic functionality
2. User authentication
3. Data processing
4. Advanced analytics

## Performance
- Response time: 80ms
- Throughput: 1500 requests/second
- Memory usage: 768MB

## Configuration
API_VERSION=2.0
DEBUG_MODE=true
MAX_CONNECTIONS=200"""

    # Add content for analysis
    analyzer.add_text(old_content, "old_version")
    analyzer.add_text(new_content, "new_version")
    
    # Perform universal analysis
    result = analyzer.universal_analyze()
    
    # Display results
    print(f"Analysis completed successfully!")
    print(f"Analysis method: {result['universal_analysis']['analysis_method']}")
    
    # Show summary
    summary = result['summary']
    print(f"\n📊 Summary:")
    print(f"  Real changes: {summary['real_changes_count']}")
    print(f"  Structural shifts: {summary['structural_changes_count']}")
    print(f"  Overall assessment: {summary['overall_assessment']}")
    print(f"  Change impact: {summary['change_impact']}")
    
    # Show change categories
    if summary['change_categories']:
        print(f"\n📋 Change Categories:")
        for category, count in summary['change_categories'].items():
            print(f"  • {category}: {count}")
    
    # Show real changes
    real_changes = result['universal_analysis']['real_changes']
    if real_changes:
        print(f"\n🎯 Real Changes Detected:")
        for i, change in enumerate(real_changes, 1):
            print(f"  {i}. {change['type']}: {change['description']}")
            print(f"     Impact: {change['impact']}")
            print(f"     Category: {change['change_category']}")
            if 'old_content' in change:
                print(f"     Old: {change['old_content'][:50]}...")
            if 'new_content' in change:
                print(f"     New: {change['new_content'][:50]}...")
            print()
    
    # Show structural shifts
    structural_changes = result['universal_analysis']['structural_chifts']
    if structural_changes:
        print(f"\n📐 Structural Shifts (No Content Impact):")
        for i, shift in enumerate(structural_changes, 1):
            print(f"  {i}. {shift['description']}")
            print(f"     Content: {shift['content'][:50]}...")
            print(f"     Shift distance: {shift['shift_distance']} positions")
            print()


def pattern_detection_example():
    """Example demonstrating pattern detection capabilities"""
    print("\n🔍 Pattern Detection Example")
    print("=" * 50)
    
    analyzer = UniversalFileDiffAnalyzer()
    
    # Test various pattern changes
    test_cases = [
        ("Version 1.0", "Version 2.0", "version_change"),
        ("100 users", "200 users", "numeric_change"),
        ("2024-01-01", "2025-01-01", "date_change"),
        ("http://site.com", "https://site.com", "url_change"),
        ("user@old.com", "user@new.com", "email_change"),
    ]
    
    for old_text, new_text, expected_type in test_cases:
        analyzer.clear_files()
        analyzer.add_text(old_text, "old")
        analyzer.add_text(new_text, "new")
        
        result = analyzer.universal_analyze()
        real_changes = result['universal_analysis']['real_changes']
        
        if real_changes:
            detected_type = real_changes[0]['type']
            print(f"✓ {old_text} → {new_text}")
            print(f"  Detected: {detected_type}")
            print(f"  Expected: {expected_type}")
            print(f"  Match: {'✅' if detected_type == expected_type else '❌'}")
        else:
            print(f"✗ {old_text} → {new_text}")
            print(f"  No change detected")
        print()


def structural_analysis_example():
    """Example demonstrating structural change analysis"""
    print("\n🏗️ Structural Analysis Example")
    print("=" * 50)
    
    analyzer = UniversalFileDiffAnalyzer()
    
    # Create content with structural changes
    original = """1. First item
2. Second item
3. Third item
4. Fourth item"""

    modified = """1. First item
2. Second item
New item inserted
3. Third item
4. Fourth item"""

    analyzer.add_text(original, "original")
    analyzer.add_text(modified, "modified")
    
    result = analyzer.universal_analyze()
    
    print("Original structure:")
    print(original)
    print("\nModified structure:")
    print(modified)
    
    # Show what was detected
    real_changes = result['universal_analysis']['real_changes']
    structural_changes = result['universal_analysis']['structural_chifts']
    
    print(f"\n📊 Analysis Results:")
    print(f"  Real changes: {len(real_changes)}")
    print(f"  Structural shifts: {len(structural_changes)}")
    
    if real_changes:
        print(f"\n🎯 Real Changes:")
        for change in real_changes:
            print(f"  • {change['description']}")
    
    if structural_changes:
        print(f"\n📐 Structural Shifts:")
        for shift in structural_changes:
            print(f"  • {shift['description']}")


def line_type_classification_example():
    """Example demonstrating line type classification"""
    print("\n🏷️ Line Type Classification Example")
    print("=" * 50)
    
    analyzer = UniversalFileDiffAnalyzer()
    
    # Test various line types
    test_lines = [
        "# Markdown Header",
        "1. Numbered list item",
        "- Bullet list item",
        "`code snippet`",
        "user@example.com",
        "https://example.com",
        "2025-01-01",
        "123.45",
        "",
        "Regular text content"
    ]
    
    print("Line Type Classification:")
    for line in test_lines:
        line_type = analyzer._classify_line_type(line)
        print(f"  '{line}' → {line_type}")


def main():
    """Main function to run all universal analysis examples"""
    print("🚀 File Difference Analyzer - Universal Analysis Examples")
    print("=" * 70)
    
    try:
        universal_analysis_example()
        pattern_detection_example()
        structural_analysis_example()
        line_type_classification_example()
        
        print("\n✅ All universal analysis examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
