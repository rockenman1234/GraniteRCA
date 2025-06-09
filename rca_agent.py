"""
Enhanced System Diagnostic RCA Agent

This is the main entry point for the RCA system, providing a command-line interface
for users to perform root cause analysis on system errors. It handles argument parsing,
user interaction, and coordinates the core RCA functionality.

Copyright (C) 2024 Kenneth (Alex) Jenkins

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <https://www.gnu.org/licenses/>.
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
This is libre/free software, and you are welcome to redistribute it under certain conditions;
type '--license' for details.

A copy of this license should have been provided with this software, if not - visit:
https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
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
        'mode': 'basic'
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
   python rca_agent.py --error "Error description" --logfile path/to/logfile

2. System Scan Mode (automatic log scanning):
   python rca_agent.py --error "Error description" --scan-system [--hours 24]

3. Quick Analysis Mode (error description only):
   python rca_agent.py --error "Error description"

OPTIONS:
  --error TEXT        Description of the error (required)
  --logfile PATH      Path to specific log file to analyze
  --scan-system       Automatically scan system logs for recent errors
  --hours N           Hours back to scan for errors (default: 24)
  --help, -h          Show this help message
  --license, -l       Show license information

SUPPORTED ERROR TYPES:
  - Linux kernel errors and panics
  - SELinux policy violations
  - Java/JVM exceptions and errors
  - systemd service failures
  - Network connectivity issues
  - Boot and initialization problems
  - Application-level errors
  - Hardware-related issues
""")

def main():
    """
    Enhanced main function supporting multiple diagnostic modes.
    """
    try:
        args = parse_enhanced_args()
        
        print("=== Enhanced System Diagnostic RCA Report ===")
        print(f"Mode: {args['mode'].upper()}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        analysis = asyncio.run(perform_enhanced_rca(
            args['error'], 
            args['logfile'], 
            args['scan_system'], 
            args['hours_back']
        ))
        
        formatted_analysis = format_output(analysis)
        print(formatted_analysis)
        
        print("\n" + "=" * 50)
        print("Analysis complete. For persistent issues, consider:")
        print("- Running with --scan-system to check broader system logs")
        print("- Increasing --hours value to scan further back in time")
        print("- Checking specific service logs in /var/log/")
        print("- Reviewing security logs if SELinux or permission issues persist")
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        print("\nFor troubleshooting:")
        print("1. Verify log file permissions and paths")
        print("2. Check if BeeAI framework and Ollama are properly configured")
        print("3. Ensure granite3.3:8b-beeai model is available")
        sys.exit(1)

if __name__ == '__main__':
    main()