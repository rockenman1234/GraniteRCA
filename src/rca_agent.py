"""
Enhanced System Diagnostic RCA Agent

This is the main entry point for the RCA system, providing a command-line interface
for users to perform root cause analysis on system errors. It handles argument parsing,
user interaction, and coordinates the core RCA functionality.

Copyright (C) 2025 Kenneth (Alex) Jenkins

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

SPDX-License-Identifier: Apache-2.0
"""

import sys
import asyncio
from datetime import datetime
from rca_core import perform_enhanced_rca
from rca_utils import format_output

def show_license():
    """Display the license information."""
    print("""
GraniteRCA Agent, Copyright (C) 2025-present Kenneth (Alex) Jenkins, & contributors.

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions;
as described in the Apache Public License Version 2.0.

A copy of this license should have been provided with this software, if not - visit:
https://www.apache.org/licenses/LICENSE-2.0
""")

def parse_enhanced_args():
    """
    Enhanced argument parsing supporting multiple operation modes.
    """
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    # Check for license flag first
    if sys.argv[1] in ['--license', '-l']:
        show_license()
        sys.exit(0)
    
    args = {
        'error': '',
        'logfile': None,
        'scan_system': False,
        'hours_back': 24,
        'mode': 'basic',
        'triage_mode': False,
        'framework': 'beeai'  # Default to BeeAI platform
    }
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--error' and i + 1 < len(sys.argv):
            args['error'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--logfile' and i + 1 < len(sys.argv):
            args['logfile'] = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--scan-system':
            args['scan_system'] = True
            args['mode'] = 'system_scan'
            i += 1
        elif sys.argv[i] == '--hours' and i + 1 < len(sys.argv):
            args['hours_back'] = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--triage':
            args['triage_mode'] = True
            args['mode'] = 'triage'
            i += 1
        elif sys.argv[i] == '--llm-framework' and i + 1 < len(sys.argv):
            framework = sys.argv[i + 1].lower()
            if framework in ['beeai', 'granite-io', 'granite_io']:
                args['framework'] = 'granite-io' if framework in ['granite-io', 'granite_io'] else 'beeai'
            else:
                print(f"Error: Invalid LLM framework '{framework}'. Use 'beeai' or 'granite-io'")
                sys.exit(1)
            i += 2
        elif sys.argv[i] in ['--help', '-h']:
            print_usage()
            sys.exit(0)
        elif sys.argv[i] in ['--license', '-l']:
            show_license()
            sys.exit(0)
        else:
            print(f"Unknown argument: {sys.argv[i]}")
            print_usage()
            sys.exit(1)
    
    if not args['error']:
        print("Error: --error description is required")
        print_usage()
        sys.exit(1)
    
    return args

def print_usage():
    """Print comprehensive usage information."""
    print("""
Enhanced System Diagnostic RCA Agent

USAGE MODES:

1. Basic Mode (original functionality):
   python main.py --error "Error description" --logfile path/to/logfile

2. System Scan Mode (automatic log scanning):
   python main.py --error "Error description" --scan-system [--hours 24]

3. Quick Analysis Mode (error description only):
   python main.py --error "Error description"

4. Triage Mode (for live outages):
   python main.py --error "Error description" --triage [--scan-system]

OPTIONS:
  --error TEXT        Description of the error (required)
  --logfile PATH      Path to specific log file to analyze
  --scan-system       Automatically scan system logs for recent errors
  --hours N           Hours back to scan for errors (default: 24)
  --triage           Run in triage mode for live outages
  --llm-framework NAME    LLM framework: 'granite-io' for enhanced processing (default: beeai)
  --help, -h          Show this help message
  --license, -l       Show license information

LLM FRAMEWORKS:
  beeai              Use BeeAI platform (default, requires ollama:granite3.3:8b-beeai)
  granite-io         Use Granite-IO processing (enhanced, requires granite3.2:8b)

SUPPORTED ERROR TYPES:
  - Linux kernel errors and panics
  - SELinux policy violations
  - Java/JVM exceptions and errors
  - systemd service failures
  - Network connectivity issues
  - Boot and initialization problems
  - Application-level errors
  - Hardware-related issues
  - Container runtime issues

FEATURES:
  - Context-aware impact scoring
  - Triage mode for live outages
  - Container health monitoring
  - Resource usage tracking
  - Log bundling and analysis
  - Lessons learned tracking
  - Enhanced LLM processing with dual framework support
""")

def main():
    """
    Enhanced main function supporting multiple diagnostic modes.
    """
    try:
        args = parse_enhanced_args()
        
        print("=== Enhanced System Diagnostic RCA Report ===")
        print(f"Mode: {args['mode'].upper()}")
        print(f"LLM Framework: {args['framework'].upper()}")
        if args['triage_mode']:
            print("TRIAGE MODE ENABLED - Live outage in progress")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        analysis = asyncio.run(perform_enhanced_rca(
            args['error'], 
            args['logfile'], 
            args['scan_system'], 
            args['hours_back'],
            args['triage_mode'],
            args['framework']
        ))
        
        formatted_analysis = format_output(analysis)
        print(formatted_analysis)
        
        print("\n" + "=" * 50)
        print("Analysis complete. For persistent issues, consider:")
        print("- Running with --scan-system to check broader system logs")
        print("- Increasing --hours value to scan further back in time")
        print("- Using --triage mode for live outage situations")
        print("- Trying --llm-framework granite-io for enhanced processing")
        print("- Checking specific service logs in /var/log/")
        print("- Reviewing security logs if SELinux or permission issues persist")
        print("- Monitoring container health if analyzing container issues")
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        print("\nFor troubleshooting:")
        print("1. Verify log file permissions and paths")
        if 'framework' in locals() and args.get('framework') == 'granite-io':
            print("2. Check if Granite-IO processing and Ollama are properly configured")
            print("3. Ensure granite3.2:8b model is available (ollama pull granite3.2:8b)")
            print("4. Install Granite-IO: pip install granite-io")
        else:
            print("2. Check if BeeAI platform and Ollama are properly configured")
            print("3. Ensure granite3.3:8b-beeai model is available")
        print("5. Check container runtime status if analyzing container issues")
        print("6. Install Docling for enhanced document parsing: pip install docling")
        print("7. For offline Docling usage, set DOCLING_ARTIFACTS_PATH environment variable")
        print("8. Try switching frameworks with --llm-framework granite-io or --llm-framework beeai")
        sys.exit(1)

if __name__ == '__main__':
    main()
