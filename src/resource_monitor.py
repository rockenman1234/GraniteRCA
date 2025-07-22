"""
Resource monitoring and log bundling module for GraniteRCA.

This module provides functionality to monitor system resources and bundle logs
for analysis using Docling for enhanced document parsing, including CPU, memory, 
and process information.

SPDX-License-Identifier: Apache-2.0
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import glob
import shutil
import tempfile
from docling_utils import DoclingLogParser

class ResourceMonitor:
    def __init__(self, artifacts_path: Optional[str] = None):
        self.temp_dir = tempfile.mkdtemp(prefix="granite_rca_")
        self.docling_parser = DoclingLogParser(artifacts_path=artifacts_path)
        
    def __del__(self):
        """Clean up temporary directory on object destruction."""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
            
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get detailed CPU information from /proc/cpuinfo."""
        cpu_info = {
            "timestamp": datetime.now().isoformat(),
            "processors": []
        }
        
        try:
            with open('/proc/cpuinfo', 'r') as f:
                current_processor = {}
                for line in f:
                    line = line.strip()
                    if not line:
                        if current_processor:
                            cpu_info["processors"].append(current_processor)
                            current_processor = {}
                        continue
                        
                    if ':' in line:
                        key, value = line.split(':', 1)
                        current_processor[key.strip()] = value.strip()
                        
                if current_processor:
                    cpu_info["processors"].append(current_processor)
                    
        except Exception as e:
            cpu_info["error"] = f"Failed to read CPU info: {str(e)}"
            
        return cpu_info
        
    def get_top_info(self) -> Dict[str, Any]:
        """Get system resource usage information using top."""
        top_info = {
            "timestamp": datetime.now().isoformat(),
            "processes": []
        }
        
        try:
            # Run top in batch mode for one iteration
            cmd = ['top', '-b', '-n', '1']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the output
            lines = result.stdout.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('top') and not line.startswith('Tasks'):
                    parts = line.split()
                    if len(parts) >= 12:
                        process = {
                            "pid": parts[0],
                            "user": parts[1],
                            "pr": parts[2],
                            "ni": parts[3],
                            "virt": parts[4],
                            "res": parts[5],
                            "shr": parts[6],
                            "s": parts[7],
                            "cpu": parts[8],
                            "mem": parts[9],
                            "time": parts[10],
                            "command": ' '.join(parts[11:])
                        }
                        top_info["processes"].append(process)
                        
        except Exception as e:
            top_info["error"] = f"Failed to get top info: {str(e)}"
            
        return top_info
        
    def bundle_logs(self, hours_back: int = 24) -> Dict[str, Any]:
        """Bundle relevant system logs for analysis using Docling for enhanced parsing."""
        log_bundle = {
            "timestamp": datetime.now().isoformat(),
            "logs": {},
            "docling_metadata": {},
            "parsing_methods": {},
            "error_patterns": {}
        }
        
        # Common log locations
        log_paths = [
            '/var/log/syslog',
            '/var/log/messages',
            '/var/log/kern.log',
            '/var/log/dmesg',
            '/var/log/auth.log',
            '/var/log/audit/audit.log'
        ]
        
        # Add application logs
        app_log_patterns = [
            '/var/log/*.log',
            '/opt/*/logs/*.log',
            '~/.local/share/logs/*.log'
        ]
        
        for pattern in app_log_patterns:
            log_paths.extend(glob.glob(os.path.expanduser(pattern)))
            
        # Collect logs with Docling parsing
        for log_path in log_paths:
            if os.path.exists(log_path) and os.access(log_path, os.R_OK):
                try:
                    # Use Docling to parse the log file
                    parsed_log = self.docling_parser.parse_log_file(log_path)
                    
                    if 'error' not in parsed_log:
                        # Store content (truncated for memory efficiency)
                        content = parsed_log['content']
                        if len(content) > 10000:  # Limit to ~10KB per file
                            content = content[-10000:]  # Keep last 10KB
                        
                        log_bundle["logs"][log_path] = content
                        log_bundle["docling_metadata"][log_path] = parsed_log['metadata']
                        log_bundle["parsing_methods"][log_path] = parsed_log['parsing_method']
                        
                        # Extract error patterns
                        error_patterns = self.docling_parser.extract_error_patterns(parsed_log)
                        if error_patterns:
                            log_bundle["error_patterns"][log_path] = error_patterns[:10]  # Limit to 10 patterns
                    else:
                        # Fallback to basic reading if Docling fails
                        with open(log_path, 'r', errors='ignore') as f:
                            lines = f.readlines()[-1000:]  # Read last 1000 lines
                            log_bundle["logs"][log_path] = ''.join(lines)
                            log_bundle["parsing_methods"][log_path] = "basic_fallback"
                            
                except Exception as e:
                    log_bundle["logs"][log_path] = f"Error reading/parsing log: {str(e)}"
                    log_bundle["parsing_methods"][log_path] = "error"
                    
        return log_bundle
        
    def save_report(self, report_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save a report to a temporary file."""
        if filename is None:
            filename = f"rca_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        filepath = os.path.join(self.temp_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            return filepath
        except Exception as e:
            raise Exception(f"Failed to save report: {str(e)}")
            
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive system report with Docling-enhanced log parsing."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "cpu_info": self.get_cpu_info(),
            "resource_usage": self.get_top_info(),
            "log_bundle": self.bundle_logs(),
            "docling_status": {
                "available": self.docling_parser.is_docling_available(),
                "supported_formats": self.docling_parser.get_supported_formats()
            }
        }
        
        # Save the report
        self.save_report(report)
        
        return report 
