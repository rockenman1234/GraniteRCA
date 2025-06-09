"""
Core Root Cause Analysis (RCA) functionality for system diagnostics.

This module contains the core classes and functionality for performing system-wide
root cause analysis, including error classification, log scanning, and system context
gathering. It provides the foundation for the RCA agent's diagnostic capabilities.
"""

import os
import re
import subprocess
import glob
from datetime import datetime, timedelta
from tqdm import tqdm
from beeai_framework.backend.chat import ChatModel
from beeai_framework.backend.message import UserMessage, AssistantMessage

class SystemErrorTypes:
    """Classification of different system error types for specialized analysis."""
    
    KERNEL = "kernel"
    SELINUX = "selinux"
    JAVA = "java"
    SYSTEMD = "systemd"
    NETWORK = "network"
    APPLICATION = "application"
    BOOT = "boot"
    HARDWARE = "hardware"
    SECURITY = "security"

class SystemLogScanner:
    """Scans various system logs and identifies error patterns."""
    
    def __init__(self):
        self.log_paths = {
            'kernel': ['/var/log/kern.log', '/var/log/dmesg', '/var/log/messages'],
            'system': ['/var/log/syslog', '/var/log/messages', '/var/log/system.log'],
            'selinux': ['/var/log/audit/audit.log', '/var/log/audit.log'],
            'boot': ['/var/log/boot.log', '/var/log/boot', '/var/log/dmesg'],
            'journal': ['journalctl'],
            'application': ['/var/log/*.log', '/opt/*/logs/*.log', '~/.local/share/logs/*.log']
        }
        
        self.error_patterns = {
            SystemErrorTypes.KERNEL: [
                r'kernel:.*error|panic|oops|bug|fault',
                r'Call Trace:',
                r'segfault',
                r'unable to handle kernel paging request',
                r'kernel NULL pointer dereference'
            ],
            SystemErrorTypes.SELINUX: [
                r'avc:.*denied',
                r'SELinux.*denied',
                r'type=AVC.*denied',
                r'scontext=.*tcontext=.*denied'
            ],
            SystemErrorTypes.JAVA: [
                r'java\..*Exception',
                r'Exception in thread',
                r'OutOfMemoryError',
                r'StackOverflowError',
                r'ClassNotFoundException',
                r'NoClassDefFoundError'
            ],
            SystemErrorTypes.SYSTEMD: [
                r'systemd.*failed',
                r'Failed to start',
                r'Unit.*failed',
                r'Service.*failed'
            ],
            SystemErrorTypes.NETWORK: [
                r'connection.*refused|timeout|reset',
                r'network.*unreachable',
                r'DNS.*failed',
                r'socket.*error'
            ],
            SystemErrorTypes.BOOT: [
                r'failed to mount',
                r'boot.*error|failed',
                r'initramfs.*error',
                r'grub.*error'
            ]
        }
    
    def scan_system_logs(self, hours_back=24):
        """Scan system logs for recent errors."""
        errors_found = {}
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Check journalctl first (most comprehensive on systemd systems)
        try:
            cmd = f"journalctl --since '{cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}' --priority=err"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout:
                errors_found['journal'] = result.stdout
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        # Check individual log files
        for log_type, paths in self.log_paths.items():
            if log_type == 'journal':
                continue
                
            for path_pattern in paths:
                try:
                    if '*' in path_pattern:
                        files = glob.glob(path_pattern)
                    else:
                        files = [path_pattern] if os.path.exists(path_pattern) else []
                    
                    for file_path in files:
                        if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                            try:
                                with open(file_path, 'r', errors='ignore') as f:
                                    # Read last 1000 lines to avoid memory issues
                                    lines = f.readlines()[-1000:]
                                    content = ''.join(lines)
                                    if self._contains_recent_errors(content, cutoff_time):
                                        if log_type not in errors_found:
                                            errors_found[log_type] = ""
                                        errors_found[log_type] += f"\n--- {file_path} ---\n{content}"
                            except (IOError, OSError):
                                continue
                except (OSError, PermissionError):
                    continue
        
        return errors_found
    
    def _contains_recent_errors(self, content, cutoff_time):
        """Check if content contains recent errors."""
        # Simple heuristic: look for error keywords
        error_keywords = ['error', 'failed', 'exception', 'panic', 'fault', 'denied', 'timeout']
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in error_keywords)
    
    def classify_error_type(self, error_desc, log_content):
        """Classify the type of error based on description and log content."""
        combined_text = f"{error_desc} {log_content}".lower()
        
        scores = {}
        for error_type, patterns in self.error_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, combined_text, re.IGNORECASE))
                score += matches
            scores[error_type] = score
        
        # Return the error type with highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return SystemErrorTypes.APPLICATION

async def perform_enhanced_rca(error_desc, logfile_path=None, scan_system=False, hours_back=24):
    """
    Performs comprehensive Root Cause Analysis with system-wide scanning capabilities.
    
    This enhanced RCA function provides:
    1. Multi-mode operation (file-based, system scan, or quick analysis)
    2. Automatic error classification
    3. System context gathering
    4. Progress indication during analysis
    5. Specialized analysis based on error type
    
    Args:
        error_desc (str): Description of the error to analyze
        logfile_path (str, optional): Path to specific log file for analysis
        scan_system (bool): Whether to perform system-wide log scanning
        hours_back (int): Number of hours to look back in logs when scanning
        
    Returns:
        str: Comprehensive analysis report with root cause and recommendations
        
    Raises:
        FileNotFoundError: If specified log file doesn't exist
        Exception: For other analysis or model-related errors
    """
    from rca_utils import get_system_context, build_enhanced_prompt
    
    log_content = ""
    system_context = get_system_context()
    scanner = SystemLogScanner()
    
    # Create progress bar for overall analysis
    with tqdm(total=100, desc="Performing RCA", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
        # Handle different input modes
        if logfile_path and os.path.exists(logfile_path):
            # Traditional mode: analyze specific log file
            with open(logfile_path, 'r', errors='ignore') as f:
                log_content = f.read()
            pbar.update(20)  # 20% complete after reading log file
        elif scan_system:
            # Enhanced mode: scan system logs automatically
            print(f"\nScanning system logs for errors in the last {hours_back} hours...")
            system_errors = scanner.scan_system_logs(hours_back)
            
            if system_errors:
                log_content = "\n\n".join([f"=== {source.upper()} LOGS ===\n{content}" 
                                         for source, content in system_errors.items()])
                print(f"Found errors in: {', '.join(system_errors.keys())}")
            else:
                print("No recent system errors found in accessible logs.")
                log_content = "No recent system errors detected in standard log locations."
            pbar.update(30)  # 30% complete after system scan
        elif logfile_path:
            raise FileNotFoundError(f"Log file not found: {logfile_path}")
        else:
            # Interactive mode: minimal analysis with system context only
            log_content = "No specific log file provided - analysis based on error description and system context."
            pbar.update(10)  # 10% complete for quick analysis
        
        # Classify error type for specialized analysis
        error_type = scanner.classify_error_type(error_desc, log_content)
        print(f"Error classified as: {error_type.upper()}")
        pbar.update(20)  # 20% more complete after classification
        
        # Build enhanced prompt
        prompt = build_enhanced_prompt(error_desc, log_content, error_type, system_context)
        pbar.update(10)  # 10% more complete after prompt building
        
        # Initialize the Granite model via BeeAI
        model = ChatModel.from_name("ollama:granite3.3:8b-beeai")
        user_msg = UserMessage(prompt)
        
        try:
            # Show progress during model analysis
            pbar.set_description("Analyzing with Granite model")
            response = await model.create(messages=[user_msg])
            pbar.update(30)  # 30% more complete after model analysis
            
            # Extract text content from response
            if isinstance(response, list) and len(response) > 0:
                if hasattr(response[0], "text"):
                    return response[0].text
                return str(response[0])
            elif hasattr(response, "messages"):
                messages = response.messages
                if isinstance(messages, list) and len(messages) > 0 and hasattr(messages[0], "text"):
                    return messages[0].text
                return str(messages)
            elif hasattr(response, "text"):
                return response.text
            else:
                return str(response)
        except Exception as e:
            raise Exception(f"Failed to get response from model: {e}") 