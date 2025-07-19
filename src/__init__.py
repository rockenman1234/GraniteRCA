"""
GraniteRCA - Enhanced System Diagnostic RCA Tool

A comprehensive root cause analysis tool for system administrators and DevOps
engineers, enhanced with Docling document parsing capabilities.

Copyright (C) 2024 Kenneth (Alex) Jenkins
Licensed under LGPLv3

SPDX-License-Identifier: LGPL-3.0-only
"""

__version__ = "1.0.0"
__author__ = "Kenneth (Alex) Jenkins"

# Main exports
from .rca_agent import main as rca_main
from .rca_core import perform_enhanced_rca
from .rca_utils import format_output
from .docling_utils import DoclingLogParser

__all__ = [
    'rca_main',
    'perform_enhanced_rca', 
    'format_output',
    'DoclingLogParser'
]
