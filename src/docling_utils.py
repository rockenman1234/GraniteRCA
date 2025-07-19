"""
Docling-based document parsing utilities for GraniteRCA.

This module provides document parsing functionality using Docling for enhanced
log file analysis, including support for various document formats and intelligent
text extraction with structure preservation.

SPDX-License-Identifier: LGPL-3.0-only
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from io import BytesIO

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat, DocumentStream
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import PdfFormatOption
    from docling.chunking import HybridChunker
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("Warning: Docling not available. Falling back to basic text parsing.")

class DoclingLogParser:
    """Enhanced log parser using Docling for intelligent document processing."""
    
    # Class variable to track if the note has been shown
    _note_shown = False
    
    def __init__(self, artifacts_path: Optional[str] = None):
        """
        Initialize the Docling log parser.
        
        Args:
            artifacts_path: Optional path to Docling model artifacts for offline usage
        """
        self.artifacts_path = artifacts_path
        self.converter = None
        self.chunker = None
        
        if DOCLING_AVAILABLE:
            self._initialize_converter()
            self._initialize_chunker()
    
    def _initialize_converter(self):
        """Initialize the Docling document converter with optimal settings for log analysis."""
        if not DOCLING_AVAILABLE:
            return
            
        try:
            # Create converter with all available formats
            # Note: Docling primarily supports structured documents, not plain text
            self.converter = DocumentConverter()
            
            # For now, we'll rely on fallback parsing for .txt and .log files
            # since Docling doesn't natively support plain text files
            # Only show the note once across all instances
            if not DoclingLogParser._note_shown:
                print("Note: Docling optimized for structured documents (PDF, DOCX, etc.). Plain text files will use fallback parsing.")
                DoclingLogParser._note_shown = True
            
        except Exception as e:
            print(f"Warning: Failed to initialize Docling converter: {e}")
            self.converter = None
    
    def _initialize_chunker(self):
        """Initialize the hybrid chunker for intelligent text segmentation."""
        if not DOCLING_AVAILABLE:
            return
            
        try:
            # Initialize chunker for log analysis (no specific tokenizer needed for logs)
            self.chunker = HybridChunker()
        except Exception as e:
            print(f"Warning: Failed to initialize Docling chunker: {e}")
            self.chunker = None
    
    def parse_log_file(self, file_path: str, max_file_size: int = 20971520) -> Dict[str, Any]:
        """
        Parse a log file using Docling for enhanced text extraction.
        
        Args:
            file_path: Path to the log file
            max_file_size: Maximum file size to process (default: 20MB)
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "content": "",
            "metadata": {},
            "chunks": [],
            "parsing_method": "fallback"
        }
        
        if not os.path.exists(file_path):
            result["error"] = f"File not found: {file_path}"
            return result
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > max_file_size:
            result["error"] = f"File too large: {file_size} bytes (max: {max_file_size})"
            return result
        
        # Try Docling parsing first (only for supported formats)
        if DOCLING_AVAILABLE and self.converter and self._is_docling_supported_format(file_path):
            try:
                result.update(self._parse_with_docling(file_path))
                result["parsing_method"] = "docling"
                return result
            except Exception as e:
                print(f"Docling parsing failed for {file_path}: {e}")
                # Fall back to basic parsing
        
        # Fallback to basic text parsing
        try:
            result.update(self._parse_basic_text(file_path))
            result["parsing_method"] = "basic"
        except Exception as e:
            result["error"] = f"Failed to parse file: {e}"
        
        return result
    
    def _is_docling_supported_format(self, file_path: str) -> bool:
        """Check if the file format is supported by Docling."""
        if not DOCLING_AVAILABLE:
            return False
            
        supported_extensions = {'.pdf', '.docx', '.pptx', '.html', '.md', '.csv', '.xlsx'}
        file_ext = Path(file_path).suffix.lower()
        return file_ext in supported_extensions
    
    def _parse_with_docling(self, file_path: str) -> Dict[str, Any]:
        """Parse file using Docling with enhanced structure recognition."""
        try:
            # Convert document using Docling (for supported formats only)
            conv_result = self.converter.convert(file_path)
            document = conv_result.document
            
            # Extract content as markdown for better structure preservation
            content = document.export_to_markdown()
            
            # Extract metadata
            metadata = {
                "pages": getattr(document, 'page_count', 1) if hasattr(document, 'page_count') else 1,
                "document_type": self._detect_log_type(content),
                "structure_elements": len(document.texts) if hasattr(document, 'texts') else 0,
                "original_format": Path(file_path).suffix.lower().lstrip('.')
            }
            
            # Chunk the document if chunker is available
            chunks = []
            if self.chunker:
                try:
                    chunk_iter = self.chunker.chunk(document)
                    chunks = []
                    for chunk in list(chunk_iter)[:50]:  # Limit to first 50 chunks
                        if hasattr(chunk, 'text') and hasattr(chunk, 'meta'):
                            chunks.append({
                                "text": chunk.text,
                                "metadata": chunk.meta
                            })
                        elif isinstance(chunk, dict):
                            chunks.append({
                                "text": chunk.get("text", ""),
                                "metadata": chunk.get("meta", {})
                            })
                        else:
                            # Fallback for other chunk types
                            chunks.append({
                                "text": str(chunk),
                                "metadata": {}
                            })
                except Exception as e:
                    print(f"Chunking failed: {e}")
                    chunks = []
            
            return {
                "content": content,
                "metadata": metadata,
                "chunks": chunks
            }
            
        except Exception as e:
            raise Exception(f"Docling parsing error: {e}")
    
    def _parse_basic_text(self, file_path: str) -> Dict[str, Any]:
        """Fallback basic text parsing for when Docling is not available."""
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()
        
        # Basic metadata extraction
        lines = content.split('\n')
        metadata = {
            "line_count": len(lines),
            "character_count": len(content),
            "document_type": self._detect_log_type(content),
            "estimated_size": len(content.encode('utf-8'))
        }
        
        # Simple chunking - split by lines for log files
        chunk_size = 1000  # lines per chunk
        chunks = []
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i+chunk_size]
            chunks.append({
                "text": '\n'.join(chunk_lines),
                "metadata": {
                    "start_line": i + 1,
                    "end_line": min(i + chunk_size, len(lines)),
                    "chunk_index": len(chunks)
                }
            })
        
        return {
            "content": content,
            "metadata": metadata,
            "chunks": chunks[:20]  # Limit chunks for memory
        }
    
    def _detect_log_type(self, content: str) -> str:
        """Detect the type of log based on content patterns."""
        content_lower = content.lower()
        
        if 'kernel:' in content_lower or 'dmesg' in content_lower:
            return 'kernel_log'
        elif 'selinux' in content_lower or 'avc:' in content_lower:
            return 'selinux_log'
        elif 'systemd' in content_lower or 'journalctl' in content_lower:
            return 'systemd_log'
        elif 'java' in content_lower or 'exception' in content_lower:
            return 'application_log'
        elif 'audit' in content_lower:
            return 'audit_log'
        elif 'auth' in content_lower:
            return 'auth_log'
        else:
            return 'general_log'
    
    def parse_log_stream(self, stream_data: bytes, filename: str = "log_stream") -> Dict[str, Any]:
        """
        Parse log data from a binary stream using Docling.
        
        Args:
            stream_data: Binary log data
            filename: Name for the stream (for identification)
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "stream_name": filename,
            "content": "",
            "metadata": {},
            "chunks": [],
            "parsing_method": "fallback"
        }
        
        if DOCLING_AVAILABLE and self.converter and self._is_stream_docling_supported(filename):
            try:
                # For supported formats, ensure proper extension
                if not any(filename.endswith(ext) for ext in ['.pdf', '.docx', '.pptx', '.html', '.md']):
                    filename = filename + '.md'  # Default to markdown for text content
                
                # Create document stream
                buf = BytesIO(stream_data)
                source = DocumentStream(name=filename, stream=buf)
                
                # Convert document
                conv_result = self.converter.convert(source)
                document = conv_result.document
                
                # Extract content
                content = document.export_to_markdown()
                
                result.update({
                    "content": content,
                    "metadata": {
                        "stream_size": len(stream_data),
                        "document_type": self._detect_log_type(content),
                        "original_format": "log_stream"
                    },
                    "parsing_method": "docling"
                })
                
                return result
                
            except Exception as e:
                print(f"Docling stream parsing failed: {e}")
        
        # Fallback to basic text parsing
        try:
            content = stream_data.decode('utf-8', errors='ignore')
            result.update({
                "content": content,
                "metadata": {
                    "stream_size": len(stream_data),
                    "document_type": self._detect_log_type(content),
                    "original_format": "log_stream"
                },
                "parsing_method": "basic"
            })
        except Exception as e:
            result["error"] = f"Failed to parse stream: {e}"
        
        return result
    
    def extract_error_patterns(self, parsed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract error patterns from parsed content using intelligent text analysis.
        
        Args:
            parsed_content: Result from parse_log_file or parse_log_stream
            
        Returns:
            List of detected error patterns with context
        """
        errors = []
        content = parsed_content.get("content", "")
        chunks = parsed_content.get("chunks", [])
        
        # Define error patterns
        error_patterns = [
            (r'error|failed|exception|panic|fault|crash', 'error'),
            (r'warning|warn', 'warning'),
            (r'critical|fatal|severe', 'critical'),
            (r'denied|refused|unauthorized', 'security'),
            (r'timeout|unreachable|connection.*refused', 'network'),
            (r'out of memory|memory.*error', 'memory'),
            (r'disk.*full|no space', 'storage')
        ]
        
        # Search in full content
        for pattern, category in error_patterns:
            import re
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 200)
                end = min(len(content), match.end() + 200)
                context = content[start:end]
                
                errors.append({
                    "pattern": pattern,
                    "category": category,
                    "match": match.group(),
                    "context": context,
                    "position": match.start()
                })
        
        # Also search in chunks for better context
        for chunk_idx, chunk in enumerate(chunks):
            chunk_text = chunk.get("text", "")
            for pattern, category in error_patterns:
                import re
                if re.search(pattern, chunk_text, re.IGNORECASE):
                    errors.append({
                        "pattern": pattern,
                        "category": category,
                        "context": chunk_text[:500],  # First 500 chars
                        "chunk_index": chunk_idx,
                        "chunk_metadata": chunk.get("metadata", {})
                    })
        
        return errors[:100]  # Limit to first 100 errors
    
    def _is_stream_docling_supported(self, filename: str) -> bool:
        """Check if the stream format is supported by Docling."""
        supported_extensions = {'.pdf', '.docx', '.pptx', '.html', '.md'}
        return any(filename.endswith(ext) for ext in supported_extensions)
    
    @staticmethod
    def is_docling_available() -> bool:
        """Check if Docling is available for use."""
        return DOCLING_AVAILABLE
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported document formats."""
        if DOCLING_AVAILABLE:
            return ['txt', 'log', 'pdf', 'docx', 'pptx', 'html', 'md', 'csv', 'xlsx']
        else:
            return ['txt', 'log']
