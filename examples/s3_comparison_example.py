#!/usr/bin/env python3
"""
Example: S3 File Comparison using File Difference Analyzer

This example demonstrates how to compare files stored in S3 using the
enhanced file difference analyzer with S3 integration.
"""

import os
import json
from file_diff_analyzer import S3Client, S3FileDiffAnalyzer, S3DownloadConfig

def main():
    """Main example function"""
    print("🚀 S3 File Comparison Example")
    print("=" * 50)
    
    # Configuration for S3 client (MinIO in this case)
    s3_config = {
        "aws_access_key_id": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        "aws_secret_access_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        "region_name": "us-east-1"  # Default region for MinIO
    }
    
    # Download configuration
    download_config = S3DownloadConfig(
        chunk_size=8192,
        max_retries=3,
        timeout_seconds=300,
        use_temp_files=True
    )
    
    try:
        # Initialize S3 client
        print("📡 Initializing S3 client...")
        s3_client = S3Client(**s3_config, download_config=download_config)
        print("✅ S3 client initialized successfully")
        
        # Initialize S3 analyzer
        print("🔍 Initializing S3 file analyzer...")
        analyzer = S3FileDiffAnalyzer(
            s3_client=s3_client,
            download_config=download_config
        )
        print("✅ S3 analyzer initialized successfully")
        
        # Example S3 file paths (adjust these to your actual files)
        left_file = "s3://raw/upload/legal/ROADMAP_v1.1.en.pdf"
        right_file = "s3://raw/upload/legal/ROADMAP_v1.2.en.pdf"
        
        print(f"\n📁 Comparing files:")
        print(f"   Left:  {left_file}")
        print(f"   Right: {right_file}")
        
        # Perform comparison
        print("\n🔄 Starting file comparison...")
        result = analyzer.compare_s3_files_simple(left_file, right_file)
        
        # Display results
        print("\n📊 Comparison Results:")
        print("-" * 30)
        
        if "error" in result.get("comparison_result", {}):
            print(f"❌ Error: {result['comparison_result']['error']}")
        else:
            basic = result["comparison_result"]["basic_analysis"]
            print(f"Similarity: {basic['similarity_percentage']:.1f}%")
            print(f"Difference: {basic['difference_percentage']:.1f}%")
            print(f"Significantly different: {basic['is_significantly_different']}")
            print(f"Common words: {basic['common_words']}")
            print(f"Unique words (left): {basic['unique_words_file1']}")
            print(f"Unique words (right): {basic['unique_words_file2']}")
            
            # File metadata
            print(f"\n📋 File Information:")
            print(f"Left file: {result['left_file']['file_name']} ({result['left_file']['size_bytes']} bytes)")
            print(f"Right file: {result['right_file']['file_name']} ({result['right_file']['size_bytes']} bytes)")
            
            # Download status
            print(f"\n⬇️ Download Status:")
            for file_type, status in result["download_status"].items():
                if status["status"] == "success":
                    print(f"   {file_type}: ✅ Downloaded successfully")
                else:
                    print(f"   {file_type}: ❌ {status.get('error', 'Unknown error')}")
        
        # Save detailed results to file
        output_file = "s3_comparison_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Detailed results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error during S3 comparison: {e}")
        print(f"Error type: {type(e).__name__}")
        
    finally:
        # Clean up temporary files
        if 'analyzer' in locals():
            analyzer.cleanup()
            print("🧹 Temporary files cleaned up")


if __name__ == "__main__":
    main()
