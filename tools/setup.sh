#!/bin/bash
"""
GraniteRCA Installation and Setup Script

This script helps set up GraniteRCA with Docling integration.
Run with: bash setup.sh

Copyright (C) 2024 Kenneth (Alex) Jenkins
Licensed under LGPLv3

SPDX-License-Identifier: LGPL-3.0-only
"""

set -e  # Exit on any error

echo "🚀 Setting up GraniteRCA with Docling integration..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d" " -f2 | cut -d"." -f1,2)
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r ../requirements.txt

# Check if Docling was installed successfully
if python3 -c "import docling" 2>/dev/null; then
    echo "✅ Docling installed successfully"
else
    echo "⚠️  Docling installation may have failed - will use fallback parsing"
fi

# Check system dependencies
echo "🔍 Checking system dependencies..."

# Check for poppler (PDF support)
if command -v pdfinfo >/dev/null 2>&1; then
    echo "✅ Poppler utilities found (PDF support available)"
else
    echo "⚠️  Poppler utilities not found - PDF parsing may be limited"
    echo "   Install with: brew install poppler (macOS) or apt-get install poppler-utils (Ubuntu)"
fi

# Check for tesseract (OCR support)
if command -v tesseract >/dev/null 2>&1; then
    echo "✅ Tesseract OCR found"
else
    echo "⚠️  Tesseract OCR not found - OCR capabilities will be limited"
    echo "   Install with: brew install tesseract (macOS) or apt-get install tesseract-ocr (Ubuntu)"
fi

# Check for Ollama
if command -v ollama >/dev/null 2>&1; then
    echo "✅ Ollama found"
    
    # Check if granite model is available
    if ollama list | grep -q "granite3.3:8b-beeai"; then
        echo "✅ Granite model available"
    else
        echo "⚠️  Granite model not found. Install with:"
        echo "   ollama pull granite3.3:8b-beeai"
    fi
else
    echo "⚠️  Ollama not found - install from https://ollama.ai/"
fi

# Check for BeeAI
if command -v beeai >/dev/null 2>&1; then
    echo "✅ BeeAI CLI found"
else
    echo "⚠️  BeeAI CLI not found. Install with:"
    echo "   brew install i-am-bee/beeai/beeai"
fi

# Test basic functionality
echo "🧪 Testing basic functionality..."
if python3 -c "import sys; sys.path.append('../src'); from docling_utils import DoclingLogParser; parser = DoclingLogParser(); print('✅ Docling utils import successful')" 2>/dev/null; then
    echo "✅ Docling utils working"
else
    echo "⚠️  Docling utils test failed - check dependencies"
fi

# Test Docling parsing
echo "🔬 Testing Docling configuration..."
python3 docling_test.py --test-parsing

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start Ollama: ollama serve"
echo "2. Pull Granite model: ollama pull granite3.3:8b-beeai"
echo "3. Setup BeeAI: beeai platform start && beeai env setup"
echo "4. Test with: python3 ../main.py --error 'Test error' --scan-system"
echo ""
echo "For enhanced parsing, consider installing system dependencies:"
echo "- macOS: brew install poppler tesseract"
echo "- Ubuntu: sudo apt-get install poppler-utils tesseract-ocr"
echo ""
echo "Documentation: ../README.md"
echo "Configuration test utility: python3 docling_test.py --help"
