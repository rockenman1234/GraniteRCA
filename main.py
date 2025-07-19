#!/usr/bin/env python3
"""
GraniteRCA - Main Entry Point

Enhanced System Diagnostic RCA Tool with Docling integration.
This is the main entry point for the GraniteRCA system.

Usage:
    python main.py --error "Error description" [options]

Copyright (C) 2024 Kenneth (Alex) Jenkins
Licensed under LGPLv3

SPDX-License-Identifier: LGPL-3.0-only
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == '__main__':
    from rca_agent import main
    main()
