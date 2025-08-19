"""
Pytest configuration and fixtures for File Difference Analyzer tests
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_text_files(temp_dir):
    """Create sample text files for testing"""
    files = {}
    
    # File 1: Simple text
    file1_path = os.path.join(temp_dir, "file1.txt")
    with open(file1_path, 'w', encoding='utf-8') as f:
        f.write("Hello world\nThis is a test file")
    files['file1'] = file1_path
    
    # File 2: Similar but different text
    file2_path = os.path.join(temp_dir, "file2.txt")
    with open(file2_path, 'w', encoding='utf-8') as f:
        f.write("Hello universe\nThis is a different test file")
    files['file2'] = file2_path
    
    # File 3: Identical to file 1
    file3_path = os.path.join(temp_dir, "file3.txt")
    with open(file3_path, 'w', encoding='utf-8') as f:
        f.write("Hello world\nThis is a test file")
    files['file3'] = file3_path
    
    return files


@pytest.fixture
def sample_large_text():
    """Generate sample large text for performance testing"""
    base_text = "This is a sample text with repeated content. " * 1000
    return base_text


@pytest.fixture
def sample_structured_content():
    """Generate sample structured content for testing"""
    return {
        'old': """# Document v1.0
Last updated: 2024-01-01
Contact: old@example.com
Website: http://example.com

## Features
1. Basic functionality
2. User authentication

## Performance
- Response time: 100ms
- Throughput: 1000 requests/second""",
        
        'new': """# Document v2.0
Last updated: 2025-01-01
Contact: new@example.com
Website: https://example.com

## Features
1. Basic functionality
2. User authentication
3. Advanced analytics

## Performance
- Response time: 80ms
- Throughput: 1500 requests/second"""
    }
