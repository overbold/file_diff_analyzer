#!/usr/bin/env python3
"""
Setup script for File Difference Analyzer library
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="file-diff-analyzer",
    version="1.0.0",
    author="Docus-AI Team",
    author_email="team@docus-ai.com",
    description="A universal library for analyzing differences between files of various formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/docus-ai/file-diff-analyzer",
    project_urls={
        "Bug Reports": "https://github.com/docus-ai/file-diff-analyzer/issues",
        "Source": "https://github.com/docus-ai/file-diff-analyzer",
        "Documentation": "https://github.com/docus-ai/file-diff-analyzer/blob/main/README.md",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
    ],
    extras_require={
        "pdf": ["PyPDF2>=3.0.0"],
        "docx": ["python-docx>=0.8.11"],
        "excel": ["openpyxl>=3.0.0"],
        "csv": ["pandas>=1.3.0"],
        "all": [
            "PyPDF2>=3.0.0",
            "python-docx>=0.8.11",
            "openpyxl>=3.0.0",
            "pandas>=1.3.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="file-analysis, text-comparison, diff-analysis, document-analysis, pdf, docx, excel, csv",
)
