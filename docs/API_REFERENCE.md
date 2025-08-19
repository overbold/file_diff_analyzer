# API Reference

This document provides detailed information about the File Difference Analyzer library's API.

## Table of Contents

- [Core Classes](#core-classes)
- [Data Models](#data-models)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Error Handling](#error-handling)

## Core Classes

### FileDiffAnalyzer

The main analyzer class for basic file comparison.

#### Constructor

```python
FileDiffAnalyzer(config: Optional[AnalysisConfig] = None)
```

**Parameters:**
- `config` (Optional[AnalysisConfig]): Configuration object for analysis parameters. Defaults to `None` (uses default configuration).

#### Methods

##### add_file(file_path: str) -> FileDiffAnalyzer

Adds a file for analysis.

**Parameters:**
- `file_path` (str): Path to the file to analyze.

**Returns:**
- `FileDiffAnalyzer`: Self for method chaining.

**Raises:**
- `FileNotFoundError`: If the file doesn't exist.
- `ImportError`: If required dependencies for the file format are not installed.

**Example:**
```python
analyzer = FileDiffAnalyzer()
analyzer.add_file("document.pdf")
analyzer.add_file("document.docx")
```

##### add_text(text: str, name: str = "text_segment") -> FileDiffAnalyzer

Adds a text segment for analysis.

**Parameters:**
- `text` (str): Text content to analyze.
- `name` (str): Identifier for the text segment. Defaults to "text_segment".

**Returns:**
- `FileDiffAnalyzer`: Self for method chaining.

**Example:**
```python
analyzer = FileDiffAnalyzer()
analyzer.add_text("Hello world", "version1")
analyzer.add_text("Hello universe", "version2")
```

##### analyze() -> ComparisonResult

Performs analysis of all added files.

**Returns:**
- `ComparisonResult`: Analysis results containing comparison matrix and file information.

**Raises:**
- `ValueError`: If fewer than 2 files are added for analysis.

**Example:**
```python
result = analyzer.analyze()
print(f"Similarity: {result.comparison_matrix[0].similarity_percentage}%")
```

##### export_to_json() -> str

Exports analysis results to JSON string.

**Returns:**
- `str`: JSON-formatted string of analysis results.

**Example:**
```python
json_result = analyzer.export_to_json()
with open("analysis_result.json", "w") as f:
    f.write(json_result)
```

##### get_file_count() -> int

Returns the number of files added for analysis.

**Returns:**
- `int`: Number of files.

**Example:**
```python
count = analyzer.get_file_count()
print(f"Analyzing {count} files")
```

##### clear_files()

Clears all added files.

**Example:**
```python
analyzer.clear_files()
assert analyzer.get_file_count() == 0
```

##### get_file_names() -> List[str]

Returns names of all added files.

**Returns:**
- `List[str]`: List of file names.

**Example:**
```python
names = analyzer.get_file_names()
print(f"Files: {', '.join(names)}")
```

##### get_file_types() -> List[FileType]

Returns types of all added files.

**Returns:**
- `List[FileType]`: List of file types.

**Example:**
```python
types = analyzer.get_file_types()
for name, file_type in zip(analyzer.get_file_names(), types):
    print(f"{name}: {file_type}")
```

### UniversalFileDiffAnalyzer

Advanced analyzer with intelligent change detection.

#### Constructor

```python
UniversalFileDiffAnalyzer(config: Optional[AnalysisConfig] = None)
```

**Parameters:**
- `config` (Optional[AnalysisConfig]): Configuration object for analysis parameters. Defaults to `None` (uses default configuration).

#### Methods

##### universal_analyze() -> Dict[str, Any]

Performs universal analysis with detection of any type of changes.

**Returns:**
- `Dict[str, Any]`: Comprehensive analysis results including basic analysis, universal analysis, and summary.

**Raises:**
- `ValueError`: If fewer than 2 files are added for analysis.

**Example:**
```python
result = universal_analyzer.universal_analyze()
print(f"Real changes: {result['summary']['real_changes_count']}")
```

##### export_universal_analysis_to_json() -> str

Exports universal analysis results to JSON string.

**Returns:**
- `str`: JSON-formatted string of universal analysis results.

**Example:**
```python
json_result = universal_analyzer.export_universal_analysis_to_json()
with open("universal_analysis.json", "w") as f:
    f.write(json_result)
```

**Note:** `UniversalFileDiffAnalyzer` inherits all methods from `FileDiffAnalyzer` and adds the universal analysis capabilities.

### TextExtractor

Handles text extraction from various file formats.

#### Constructor

```python
TextExtractor()
```

#### Methods

##### extract_text(file_path: str) -> Tuple[str, FileType]

Extracts text from a file and determines its type.

**Parameters:**
- `file_path` (str): Path to the file.

**Returns:**
- `Tuple[str, FileType]`: Tuple containing extracted text and file type.

**Raises:**
- `FileNotFoundError`: If the file doesn't exist.
- `ImportError`: If required dependencies for the file format are not installed.
- `ValueError`: If the file format is unsupported.

**Example:**
```python
extractor = TextExtractor()
text, file_type = extractor.extract_text("document.pdf")
print(f"Type: {file_type}, Content length: {len(text)}")
```

##### get_file_info(file_path: str) -> Tuple[str, FileType, int]

Gets file information including text content, type, and size.

**Parameters:**
- `file_path` (str): Path to the file.

**Returns:**
- `Tuple[str, FileType, int]`: Tuple containing text content, file type, and size in bytes.

**Example:**
```python
text, file_type, size = extractor.get_file_info("document.docx")
print(f"Size: {size} bytes")
```

## Data Models

### FileType

Enumeration of supported file types.

```python
class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    EXCEL = "excel"
    CSV = "csv"
    TXT = "txt"
    TEXT_SEGMENT = "text_segment"
```

### FileInfo

Information about a file or text segment.

```python
class FileInfo(BaseModel):
    name: str                    # File name or text segment identifier
    file_type: FileType         # Type of file or text segment
    content: str                # Extracted text content
    word_count: int             # Number of words in the content
    line_count: int             # Number of lines in the content
    size_bytes: Optional[int]   # File size in bytes (if applicable)
```

### DifferenceInfo

Information about differences between two files.

```python
class DifferenceInfo(BaseModel):
    similarity_percentage: float    # Percentage of similarity between files
    difference_percentage: float    # Percentage of differences between files
    common_words: int              # Number of common words between files
    unique_words_file1: int        # Number of unique words in first file
    unique_words_file2: int        # Number of unique words in second file
    is_significantly_different: bool  # Whether files are significantly different based on tolerance
```

### ComparisonResult

Result of file comparison analysis.

```python
class ComparisonResult(BaseModel):
    files: List[FileInfo]           # Information about analyzed files
    comparison_matrix: List[DifferenceInfo]  # Matrix of pairwise comparisons
    tolerance_threshold: float      # Tolerance threshold used for analysis
    analysis_timestamp: str         # Timestamp when analysis was performed
```

## Configuration

### AnalysisConfig

Configuration class for customizing analysis behavior.

```python
class AnalysisConfig(BaseModel):
    tolerance_percentage: float = 30.0      # Threshold for significant differences (0-100%)
    enable_word_analysis: bool = True       # Enable word-level analysis
    enable_line_analysis: bool = True       # Enable line-level analysis
    case_sensitive: bool = False            # Case-sensitive comparison
    ignore_whitespace: bool = True          # Ignore whitespace differences
    max_file_size_mb: float = 100.0        # Maximum file size limit in MB
```

**Validation Rules:**
- `tolerance_percentage`: Must be between 0.0 and 100.0
- `max_file_size_mb`: Must be between 0.1 and 1000.0

**Example:**
```python
config = AnalysisConfig(
    tolerance_percentage=15.0,    # More strict tolerance
    case_sensitive=True,          # Case-sensitive comparison
    ignore_whitespace=False       # Don't ignore whitespace
)
analyzer = FileDiffAnalyzer(config)
```

## Usage Examples

### Basic File Comparison

```python
from file_diff_analyzer import FileDiffAnalyzer

# Create analyzer
analyzer = FileDiffAnalyzer()

# Add files
analyzer.add_file("document_v1.pdf")
analyzer.add_file("document_v2.pdf")

# Perform analysis
result = analyzer.analyze()

# Access results
for comparison in result.comparison_matrix:
    print(f"Similarity: {comparison.similarity_percentage}%")
    print(f"Difference: {comparison.difference_percentage}%")
    print(f"Significantly different: {comparison.is_significantly_different}")
```

### Universal Analysis

```python
from file_diff_analyzer import UniversalFileDiffAnalyzer

# Create universal analyzer
universal = UniversalFileDiffAnalyzer()

# Add files
universal.add_file("config_v1.txt")
universal.add_file("config_v2.txt")

# Perform universal analysis
result = universal.universal_analyze()

# Access detailed results
summary = result['summary']
print(f"Real changes: {summary['real_changes_count']}")
print(f"Structural shifts: {summary['structural_changes_count']}")
print(f"Overall assessment: {summary['overall_assessment']}")

# Access specific changes
real_changes = result['universal_analysis']['real_changes']
for change in real_changes:
    print(f"Change: {change['type']}")
    print(f"Description: {change['description']}")
    print(f"Impact: {change['impact']}")
```

### Custom Configuration

```python
from file_diff_analyzer import FileDiffAnalyzer, AnalysisConfig

# Create custom configuration
config = AnalysisConfig(
    tolerance_percentage=10.0,     # Very strict tolerance
    case_sensitive=True,           # Case-sensitive
    ignore_whitespace=False,       # Don't ignore whitespace
    max_file_size_mb=50.0         # Limit file size to 50MB
)

# Create analyzer with custom config
analyzer = FileDiffAnalyzer(config)

# Use analyzer as usual
analyzer.add_file("file1.txt")
analyzer.add_file("file2.txt")
result = analyzer.analyze()
```

### Text Segment Analysis

```python
from file_diff_analyzer import FileDiffAnalyzer

analyzer = FileDiffAnalyzer()

# Add text segments
analyzer.add_text("This is the first version of the text.", "version1")
analyzer.add_text("This is the second version with some changes.", "version2")

# Analyze differences
result = analyzer.analyze()

# Export results
json_result = analyzer.export_to_json()
print(json_result)
```

## Error Handling

### Common Exceptions

#### FileNotFoundError
Raised when a file doesn't exist.

```python
try:
    analyzer.add_file("nonexistent.txt")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

#### ImportError
Raised when required dependencies for a file format are not installed.

```python
try:
    analyzer.add_file("document.pdf")
except ImportError as e:
    print(f"PDF support not available: {e}")
    print("Install PyPDF2: pip install PyPDF2")
```

#### ValueError
Raised when invalid parameters are provided or insufficient files are added.

```python
try:
    result = analyzer.analyze()
except ValueError as e:
    print(f"Analysis failed: {e}")
    print("Add at least 2 files before analysis")
```

### Error Recovery

```python
from file_diff_analyzer import FileDiffAnalyzer, AnalysisConfig

def safe_analyze(file_paths):
    """Safely analyze files with error handling."""
    analyzer = FileDiffAnalyzer()
    
    for file_path in file_paths:
        try:
            analyzer.add_file(file_path)
            print(f"✓ Added: {file_path}")
        except FileNotFoundError:
            print(f"✗ File not found: {file_path}")
        except ImportError as e:
            print(f"✗ Format not supported: {file_path} ({e})")
        except Exception as e:
            print(f"✗ Unexpected error: {file_path} ({e})")
    
    if analyzer.get_file_count() >= 2:
        try:
            result = analyzer.analyze()
            return result
        except Exception as e:
            print(f"Analysis failed: {e}")
            return None
    else:
        print("Insufficient files for analysis")
        return None

# Usage
result = safe_analyze(["file1.txt", "file2.txt", "file3.pdf"])
if result:
    print("Analysis completed successfully")
```

## Performance Considerations

### Time Complexity
- **Individual file processing**: O(n) where n is the file size
- **Pairwise comparisons**: O(n²) where n is the number of files
- **Word extraction**: O(n) where n is the text length

### Memory Usage
- **Text storage**: Proportional to file sizes
- **Word sets**: Proportional to unique word count
- **Comparison matrix**: O(n²) where n is the number of files

### Optimization Tips
1. **Use appropriate tolerance**: Higher tolerance reduces unnecessary detailed analysis
2. **Limit file sizes**: Use `max_file_size_mb` to prevent memory issues
3. **Clear files**: Use `clear_files()` between analyses to free memory
4. **Batch processing**: Process files in groups rather than all at once

## Extending the Library

### Adding New File Formats

```python
from file_diff_analyzer.extractors import TextExtractor

class CustomTextExtractor(TextExtractor):
    def _extract_custom_format(self, file_path: str) -> str:
        """Extract text from custom format."""
        # Implementation here
        pass
    
    def extract_text(self, file_path: str) -> Tuple[str, FileType]:
        """Override to add custom format support."""
        if file_path.endswith('.custom'):
            return self._extract_custom_format(file_path), FileType.TEXT_SEGMENT
        return super().extract_text(file_path)
```

### Adding New Analysis Types

```python
from file_diff_analyzer import UniversalFileDiffAnalyzer

class CustomAnalyzer(UniversalFileDiffAnalyzer):
    def _detect_custom_patterns(self, old_line: str, new_line: str):
        """Detect custom pattern changes."""
        # Implementation here
        pass
    
    def _detect_pattern_changes(self, old_line: str, new_line: str):
        """Override to add custom pattern detection."""
        custom_change = self._detect_custom_patterns(old_line, new_line)
        if custom_change:
            return custom_change
        return super()._detect_pattern_changes(old_line, new_line)
```

---

For more examples and advanced usage patterns, see the [examples directory](../examples/) and [README](../README.md).
