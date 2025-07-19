#!/usr/bin/env python3
"""
Docling Configuration Test Utility for GraniteRCA

This utility helps you test and validate your current Docling configuration
for enhanced document parsing in the GraniteRCA system. Use this tool to
verify that Docling is properly installed and functioning with your system
logs and documents.

Usage:
    python docling_test.py --file path/to/logfile
    python docling_test.py --url https://example.com/document.pdf
    python docling_test.py --test-parsing

Copyright (C) 2024 Kenneth (Alex) Jenkins
Licensed under LGPLv3

SPDX-License-Identifier: LGPL-3.0-only
"""

import sys
import os
import argparse
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from docling_utils import DoclingLogParser

def test_file_parsing(file_path: str):
    """Test Docling parsing of a local file."""
    print(f"=== Testing file: {file_path} ===")
    
    parser = DoclingLogParser()
    
    if not parser.is_docling_available():
        print("⚠️  Docling not available - using fallback parsing")
    else:
        print("✅ Docling available - using enhanced parsing")
    
    result = parser.parse_log_file(file_path)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"📄 Parsing method: {result['parsing_method']}")
    print(f"📊 Metadata: {result['metadata']}")
    print(f"🔍 Error patterns found: {len(result.get('error_patterns', []))}")
    
    # Show content preview
    content = result['content']
    if len(content) > 500:
        print(f"📝 Content preview (first 500 chars):\n{content[:500]}...")
    else:
        print(f"📝 Full content:\n{content}")
    
    # Show error patterns
    error_patterns = parser.extract_error_patterns(result)
    if error_patterns:
        print(f"\n🚨 Error patterns detected:")
        for i, pattern in enumerate(error_patterns[:5], 1):
            print(f"  {i}. {pattern.get('category', 'unknown').upper()}: {pattern.get('match', '')}")

def test_url_parsing(url: str):
    """Test Docling parsing of a remote document."""
    print(f"=== Testing URL: {url} ===")
    
    parser = DoclingLogParser()
    
    if not parser.is_docling_available():
        print("❌ Docling not available - URL parsing requires Docling")
        return
    
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(url)
        content = result.document.export_to_markdown()
        
        print(f"✅ Successfully parsed URL")
        print(f"📄 Document type: URL document")
        
        # Show content preview
        if len(content) > 500:
            print(f"📝 Content preview (first 500 chars):\n{content[:500]}...")
        else:
            print(f"📝 Full content:\n{content}")
            
    except Exception as e:
        print(f"❌ Error parsing URL: {e}")

def run_comprehensive_tests():
    """Run comprehensive parsing tests with sample data to validate Docling configuration."""
    print("=== Running Docling Configuration Tests ===")
    
    parser = DoclingLogParser()
    
    print(f"Docling available: {parser.is_docling_available()}")
    print(f"Supported formats: {parser.get_supported_formats()}")
    print(f"Note: Docling excels at structured documents (PDF, DOCX, etc.)")
    print(f"      Plain text/log files will use enhanced basic parsing")
    
    # Test with sample log content
    sample_log = """
2024-07-19 10:30:15 kernel: [12345.678] ERROR: Failed to mount /dev/sda1
2024-07-19 10:30:16 systemd[1]: Failed to start apache2.service
2024-07-19 10:30:17 SELinux: avc: denied { read } for pid=1234 comm="httpd"
2024-07-19 10:30:18 java.lang.OutOfMemoryError: Java heap space
2024-07-19 10:30:19 WARNING: Connection timeout to database server
"""
    
    # Create temporary file with .txt extension (plain text - will use basic parsing)
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_log)
        temp_file = f.name
    
    try:
        print(f"\n📄 Testing with sample log file (plain text): {temp_file}")
        result = parser.parse_log_file(temp_file)
        
        print(f"Parsing method: {result['parsing_method']}")
        print(f"Document type: {result['metadata'].get('document_type', 'unknown')}")
        
        error_patterns = parser.extract_error_patterns(result)
        print(f"Error patterns found: {len(error_patterns)}")
        
        for pattern in error_patterns:
            print(f"  - {pattern.get('category', 'unknown')}: {pattern.get('match', '')}")
            
    finally:
        # Clean up
        os.unlink(temp_file)
    
    # Test with a markdown file (Docling supported format)
    sample_md = """
# System Error Report

## Critical Issues
- **ERROR**: Failed to mount /dev/sda1
- **FAILED**: systemd apache2.service startup failure

## Security Alerts
- SELinux access denied for httpd process

## Memory Issues
- Java OutOfMemoryError detected in heap space
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(sample_md)
        temp_md_file = f.name
    
    try:
        print(f"\n📄 Testing with sample markdown file (Docling supported): {temp_md_file}")
        result = parser.parse_log_file(temp_md_file)
        
        print(f"Parsing method: {result['parsing_method']}")
        print(f"Document type: {result['metadata'].get('document_type', 'unknown')}")
        
        error_patterns = parser.extract_error_patterns(result)
        print(f"Error patterns found: {len(error_patterns)}")
        
        for pattern in error_patterns:
            print(f"  - {pattern.get('category', 'unknown')}: {pattern.get('match', '')}")
            
    finally:
        # Clean up
        os.unlink(temp_md_file)
    
    print("\n✅ Configuration test completed")
    print("💡 For best results with Docling:")
    print("   - Use PDF files for document analysis")
    print("   - Use DOCX/PPTX for Office documents")
    print("   - Use HTML/MD for web content")
    print("   - Plain text/log files get enhanced basic parsing")

def main():
    parser = argparse.ArgumentParser(
        description="Docling Configuration Test Utility for GraniteRCA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python docling_test.py --file /var/log/syslog
  python docling_test.py --url https://arxiv.org/pdf/2408.09869
  python docling_test.py --test-parsing
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', help='Test parsing a local file')
    group.add_argument('--url', '-u', help='Test parsing a remote document URL')
    group.add_argument('--test-parsing', '-t', action='store_true', 
                      help='Run comprehensive configuration tests with sample data')
    
    args = parser.parse_args()
    
    try:
        if args.file:
            if not os.path.exists(args.file):
                print(f"❌ File not found: {args.file}")
                sys.exit(1)
            test_file_parsing(args.file)
        elif args.url:
            test_url_parsing(args.url)
        elif args.test_parsing:
            run_comprehensive_tests()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Configuration test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during configuration test: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
