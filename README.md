# File Difference Analyzer

A universal Python library for analyzing differences between files of various formats: PDF, DOCX, Excel, CSV, TXT and text segments.

## Features

- **Universal Analysis**: Works with any file type without hardcoded patterns
- **Multiple Formats**: Supports PDF, DOCX, Excel, CSV, and TXT files
- **Smart Comparison**: Uses intelligent algorithms to distinguish real changes from structural shifts
- **Configurable Tolerance**: Set custom thresholds for determining significant differences
- **JSON Output**: Structured results in JSON format
- **Optimized Performance**: O(n) complexity for individual file processing
- **Extensible**: Easy to add new file format support

## Installation

### Basic Installation

```bash
pip install file-diff-analyzer
```

### With Optional Dependencies

```bash
# Install with PDF support
pip install file-diff-analyzer[pdf]

# Install with all format support
pip install file-diff-analyzer[all]

# Install with development tools
pip install file-diff-analyzer[dev]
```

### From Source

```bash
git clone https://github.com/docus-ai/file-diff-analyzer.git
cd file-diff-analyzer
pip install -e .
```

## Quick Start

### Basic Usage

```python
from file_diff_analyzer import FileDiffAnalyzer, AnalysisConfig

# Create analyzer with custom tolerance
config = AnalysisConfig(tolerance_percentage=25.0)
analyzer = FileDiffAnalyzer(config)

# Add files for comparison
analyzer.add_file("document_v1.pdf")
analyzer.add_file("document_v2.pdf")

# Perform analysis
result = analyzer.analyze()

# Export to JSON
json_result = analyzer.export_to_json()
print(json_result)
```

### Universal Analysis

```python
from file_diff_analyzer import UniversalFileDiffAnalyzer

# Create universal analyzer
universal_analyzer = UniversalFileDiffAnalyzer()

# Add files
universal_analyzer.add_file("file1.txt")
universal_analyzer.add_file("file2.txt")

# Perform universal analysis
result = universal_analyzer.universal_analyze()

# Get detailed change information
print(f"Real changes: {result['summary']['real_changes_count']}")
print(f"Structural shifts: {result['summary']['structural_changes_count']}")
```

### Text Segment Analysis

```python
from file_diff_analyzer import FileDiffAnalyzer

analyzer = FileDiffAnalyzer()

# Add text segments
analyzer.add_text("This is the first version of the text.", "version1")
analyzer.add_text("This is the second version of the text.", "version2")

# Analyze differences
result = analyzer.analyze()
```

## API Reference

### FileDiffAnalyzer

Main analyzer class for basic file comparison.

#### Methods

- `add_file(file_path: str) -> FileDiffAnalyzer`: Add a file for analysis
- `add_text(text: str, name: str) -> FileDiffAnalyzer`: Add a text segment
- `analyze() -> ComparisonResult`: Perform analysis of all added files
- `export_to_json() -> str`: Export results to JSON string

### UniversalFileDiffAnalyzer

Advanced analyzer with intelligent change detection.

#### Methods

- `universal_analyze() -> Dict[str, Any]`: Perform universal analysis
- `export_universal_analysis_to_json() -> str`: Export universal analysis to JSON

### AnalysisConfig

Configuration class for customizing analysis behavior.

#### Parameters

- `tolerance_percentage: float = 30.0`: Threshold for significant differences
- `enable_word_analysis: bool = True`: Enable word-level analysis
- `enable_line_analysis: bool = True`: Enable line-level analysis
- `case_sensitive: bool = False`: Case-sensitive comparison
- `ignore_whitespace: bool = True`: Ignore whitespace differences
- `max_file_size_mb: float = 100.0`: Maximum file size limit

## Supported File Formats

| Format | Extension | Required Package | Status |
|--------|-----------|------------------|---------|
| PDF | `.pdf` | `PyPDF2` | ✅ Supported |
| DOCX | `.docx` | `python-docx` | ✅ Supported |
| Excel | `.xlsx`, `.xls` | `openpyxl` | ✅ Supported |
| CSV | `.csv` | `pandas` | ✅ Supported |
| Text | `.txt` | Built-in | ✅ Supported |
| Text Segments | N/A | Built-in | ✅ Supported |

## Output Format

### Basic Analysis Result

```json
{
  "files": [
    {
      "name": "file1.txt",
      "file_type": "txt",
      "content": "file content...",
      "word_count": 150,
      "line_count": 25,
      "size_bytes": 2048
    }
  ],
  "comparison_matrix": [
    {
      "similarity_percentage": 85.5,
      "difference_percentage": 14.5,
      "common_words": 120,
      "unique_words_file1": 15,
      "unique_words_file2": 20,
      "is_significantly_different": false
    }
  ],
  "tolerance_threshold": 30.0,
  "analysis_timestamp": "2025-08-19T11:15:00"
}
```

### Universal Analysis Result

```json
{
  "basic_analysis": { ... },
  "universal_analysis": {
    "real_changes": [
      {
        "type": "numeric_change",
        "description": "Numeric value changed from 20 to 21",
        "old_content": "G. Perf — 20 parallel /search",
        "new_content": "G. Perf — 21 parallel /search",
        "impact": "minor",
        "change_category": "data_modification"
      }
    ],
    "structural_changes": [],
    "total_changes": 1,
    "analysis_method": "universal_sequence_matching"
  },
  "summary": {
    "real_changes_count": 1,
    "structural_changes_count": 0,
    "overall_assessment": "very_similar",
    "change_impact": "minor_update"
  }
}
```

## Advanced Usage

### Custom Tolerance Configuration

```python
from file_diff_analyzer import AnalysisConfig

# Strict analysis (10% tolerance)
strict_config = AnalysisConfig(
    tolerance_percentage=10.0,
    case_sensitive=True,
    ignore_whitespace=False
)

# Loose analysis (50% tolerance)
loose_config = AnalysisConfig(
    tolerance_percentage=50.0,
    case_sensitive=False,
    ignore_whitespace=True
)
```

### Batch File Analysis

```python
import glob
from file_diff_analyzer import FileDiffAnalyzer

analyzer = FileDiffAnalyzer()

# Add multiple files
for file_path in glob.glob("documents/*.txt"):
    analyzer.add_file(file_path)

# Analyze all files
result = analyzer.analyze()

# Process results
for comparison in result.comparison_matrix:
    if comparison.is_significantly_different:
        print(f"Files are significantly different: {comparison.difference_percentage}%")
```

## Performance Characteristics

- **Time Complexity**: O(n) for individual file processing, O(n²) for pairwise comparisons
- **Memory Usage**: Proportional to file sizes and number of files
- **Optimizations**: Uses set operations for efficient word comparison
- **Scalability**: Suitable for files up to 100MB (configurable)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/docus-ai/file-diff-analyzer.git
cd file-diff-analyzer

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run linting
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=file_diff_analyzer

# Run specific test categories
pytest tests/test_analyzer.py
pytest tests/test_universal_analyzer.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/docus-ai/file-diff-analyzer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/docus-ai/file-diff-analyzer/discussions)

## Changelog

### Version 1.0.0 (2025-08-19)

- Initial release
- Basic file difference analysis
- Universal analyzer with intelligent change detection
- Support for PDF, DOCX, Excel, CSV, and TXT formats
- Configurable tolerance thresholds
- JSON output format
- Comprehensive test coverage

## Roadmap

- [ ] Support for more file formats (RTF, ODT, etc.)
- [ ] Binary file comparison
- [ ] Image-based document analysis
- [ ] Cloud storage integration
- [ ] Web interface
- [ ] Performance optimizations for large files
- [ ] Machine learning-based change classification
