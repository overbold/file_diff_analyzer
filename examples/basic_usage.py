#!/usr/bin/env python3
"""
Basic usage example for File Difference Analyzer

This example demonstrates the basic functionality of the library.
"""

from file_diff_analyzer import FileDiffAnalyzer, AnalysisConfig


def basic_comparison_example():
    """Basic file comparison example"""
    print("🔍 Basic File Comparison Example")
    print("=" * 50)
    
    # Create analyzer with default configuration
    analyzer = FileDiffAnalyzer()
    
    # Add text segments for comparison
    analyzer.add_text("Hello world! This is the first version.", "version1")
    analyzer.add_text("Hello world! This is the second version with changes.", "version2")
    
    # Perform analysis
    result = analyzer.analyze()
    
    # Display results
    print(f"Files analyzed: {len(result.files)}")
    print(f"Tolerance threshold: {result.tolerance_threshold}%")
    print(f"Analysis timestamp: {result.analysis_timestamp}")
    
    # Show comparison details
    for i, comparison in enumerate(result.comparison_matrix):
        print(f"\nComparison {i+1}:")
        print(f"  Similarity: {comparison.similarity_percentage}%")
        print(f"  Difference: {comparison.difference_percentage}%")
        print(f"  Common words: {comparison.common_words}")
        print(f"  Unique in file 1: {comparison.unique_words_file1}")
        print(f"  Unique in file 2: {comparison.unique_words_file2}")
        print(f"  Significantly different: {comparison.is_significantly_different}")
    
    # Export to JSON
    json_result = analyzer.export_to_json()
    print(f"\nJSON export length: {len(json_result)} characters")


def custom_configuration_example():
    """Example with custom configuration"""
    print("\n🔧 Custom Configuration Example")
    print("=" * 50)
    
    # Create custom configuration
    config = AnalysisConfig(
        tolerance_percentage=15.0,  # More strict tolerance
        case_sensitive=True,        # Case-sensitive comparison
        ignore_whitespace=False     # Don't ignore whitespace
    )
    
    analyzer = FileDiffAnalyzer(config)
    
    # Add text segments
    analyzer.add_text("Hello World", "case1")
    analyzer.add_text("hello world", "case2")
    
    result = analyzer.analyze()
    comparison = result.comparison_matrix[0]
    
    print(f"Custom tolerance: {config.tolerance_percentage}%")
    print(f"Case sensitive: {config.case_sensitive}")
    print(f"Ignore whitespace: {config.ignore_whitespace}")
    print(f"Result - Significantly different: {comparison.is_significantly_different}")


def multiple_files_example():
    """Example with multiple files"""
    print("\n📁 Multiple Files Example")
    print("=" * 50)
    
    analyzer = FileDiffAnalyzer()
    
    # Add multiple text segments
    texts = [
        ("Hello world", "file1"),
        ("Hello universe", "file2"),
        ("Hello galaxy", "file3")
    ]
    
    for text, name in texts:
        analyzer.add_text(text, name)
    
    result = analyzer.analyze()
    
    print(f"Files analyzed: {len(result.files)}")
    print(f"Total comparisons: {len(result.comparison_matrix)}")
    
    # Show all comparisons
    for i, comparison in enumerate(result.comparison_matrix):
        print(f"  Comparison {i+1}: {comparison.similarity_percentage}% similar")


def performance_example():
    """Example demonstrating performance characteristics"""
    print("\n⚡ Performance Example")
    print("=" * 50)
    
    analyzer = FileDiffAnalyzer()
    
    # Create large text segments
    base_text = "This is a sample text with repeated content. " * 1000
    modified_text = base_text + "Additional content at the end."
    
    print("Adding large text segments...")
    analyzer.add_text(base_text, "large1")
    analyzer.add_text(modified_text, "large2")
    
    print("Performing analysis...")
    result = analyzer.analyze()
    
    comparison = result.comparison_matrix[0]
    print(f"Large text analysis completed:")
    print(f"  Similarity: {comparison.similarity_percentage}%")
    print(f"  Difference: {comparison.difference_percentage}%")
    print(f"  Significantly different: {comparison.is_significantly_different}")


def main():
    """Main function to run all examples"""
    print("🚀 File Difference Analyzer - Basic Examples")
    print("=" * 60)
    
    try:
        basic_comparison_example()
        custom_configuration_example()
        multiple_files_example()
        performance_example()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
