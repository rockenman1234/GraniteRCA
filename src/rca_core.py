"""
Core Root Cause Analysis (RCA) functionality for system diagnostics.

This module contains the core classes and functionality for performing system-wide
root cause analysis, including error classification, log scanning, and system context
gathering. It provides the foundation for the RCA agent's diagnostic capabilities.

SPDX-License-Identifier: Apache-2.0
"""

import os
import re
import subprocess
import glob
import json
from datetime import datetime, timedelta
from tqdm import tqdm
from beeai_framework.backend.chat import ChatModel
from beeai_framework.backend.message import UserMessage, AssistantMessage
from container_monitor import ContainerMonitor
from resource_monitor import ResourceMonitor
from docling_utils import DoclingLogParser
from spinner_utils import ASCIISpinner

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
    CONTAINER = "container"

class ImpactLevel:
    """Impact severity levels for context-aware scoring."""
    
    CRITICAL = "critical"  # System-wide outage, data loss risk
    HIGH = "high"         # Major service disruption
    MEDIUM = "medium"     # Partial service degradation
    LOW = "low"          # Minor issues, non-critical services
    INFO = "info"        # Informational, no impact

class SystemLogScanner:
    """Scans various system logs and identifies error patterns using Docling."""
    
    def __init__(self, artifacts_path: str = None):
        self.docling_parser = DoclingLogParser(artifacts_path=artifacts_path)
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
            ],
            SystemErrorTypes.CONTAINER: [
                r'container.*failed|error|crash',
                r'pod.*failed|error|crash',
                r'docker.*error|failed',
                r'podman.*error|failed'
            ]
        }
        
        self.impact_indicators = {
            ImpactLevel.CRITICAL: [
                r'panic|fatal|crash|segfault',
                r'data.*loss|corrupt',
                r'system.*halt|shutdown',
                r'kernel.*panic',
                r'out of memory',
                r'disk.*full'
            ],
            ImpactLevel.HIGH: [
                r'failed to start',
                r'service.*down',
                r'connection.*refused',
                r'authentication.*failed',
                r'permission.*denied'
            ],
            ImpactLevel.MEDIUM: [
                r'warning',
                r'degraded',
                r'slow',
                r'timeout',
                r'retry'
            ],
            ImpactLevel.LOW: [
                r'notice',
                r'info',
                r'debug'
            ]
        }
    
    def scan_system_logs(self, hours_back=24):
        """Scan system logs for recent errors using Docling for enhanced parsing."""
        errors_found = {}
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Check journalctl first (most comprehensive on systemd systems)
        try:
            cmd = f"journalctl --since '{cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}' --priority=err"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout:
                # Parse journalctl output with Docling
                journal_content = self.docling_parser.parse_log_stream(
                    result.stdout.encode('utf-8'), 
                    "journalctl_errors"
                )
                errors_found['journal'] = {
                    'content': journal_content['content'],
                    'metadata': journal_content['metadata'],
                    'error_patterns': self.docling_parser.extract_error_patterns(journal_content)
                }
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        # Check individual log files with Docling
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
                                # Use Docling to parse the log file
                                parsed_log = self.docling_parser.parse_log_file(file_path)
                                
                                if 'error' not in parsed_log and self._contains_recent_errors(
                                    parsed_log['content'], cutoff_time
                                ):
                                    if log_type not in errors_found:
                                        errors_found[log_type] = {
                                            'content': '',
                                            'metadata': {},
                                            'error_patterns': [],
                                            'parsed_files': []
                                        }
                                    
                                    # Extract error patterns using Docling
                                    error_patterns = self.docling_parser.extract_error_patterns(parsed_log)
                                    
                                    errors_found[log_type]['content'] += f"\n--- {file_path} ---\n{parsed_log['content']}"
                                    errors_found[log_type]['error_patterns'].extend(error_patterns)
                                    errors_found[log_type]['parsed_files'].append({
                                        'path': file_path,
                                        'metadata': parsed_log['metadata'],
                                        'parsing_method': parsed_log['parsing_method']
                                    })
                                    
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
        
    def assess_impact(self, error_desc, log_content):
        """Assess the impact level of an error based on its description and logs."""
        combined_text = f"{error_desc} {log_content}".lower()
        
        # Check for impact indicators in order of severity
        for level in [ImpactLevel.CRITICAL, ImpactLevel.HIGH, ImpactLevel.MEDIUM, ImpactLevel.LOW]:
            for pattern in self.impact_indicators[level]:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return level
                    
        return ImpactLevel.INFO

async def perform_enhanced_rca(error_desc, logfile_path=None, scan_system=False, hours_back=24, triage_mode=False):
    """
    Performs comprehensive Root Cause Analysis with system-wide scanning capabilities using Docling.
    
    This enhanced RCA function provides:
    1. Multi-mode operation (file-based, system scan, or quick analysis)
    2. Automatic error classification using Docling's intelligent parsing
    3. System context gathering
    4. Progress indication during analysis
    5. Specialized analysis based on error type
    6. Context-aware impact scoring
    7. Triage mode for live outages
    8. Container health monitoring
    9. Resource monitoring and log bundling
    10. Enhanced document parsing with Docling for better text extraction
    
    Args:
        error_desc (str): Description of the error to analyze
        logfile_path (str, optional): Path to specific log file for analysis
        scan_system (bool): Whether to perform system-wide log scanning
        hours_back (int): Number of hours to look back in logs when scanning
        triage_mode (bool): Whether to run in triage mode for live outages
        
    Returns:
        str: Comprehensive analysis report with root cause and recommendations
        
    Raises:
        FileNotFoundError: If specified log file doesn't exist
        Exception: For other analysis or model-related errors
    """
    from rca_utils import get_system_context, build_enhanced_prompt
    
    log_content = ""
    parsed_log_metadata = {}
    error_patterns = []
    system_context = get_system_context()
    
    # Initialize components with Docling support
    artifacts_path = os.getenv('DOCLING_ARTIFACTS_PATH')
    scanner = SystemLogScanner(artifacts_path=artifacts_path)
    resource_monitor = ResourceMonitor()
    container_monitor = ContainerMonitor()
    
    # Create progress bar for overall analysis with spinner
    with tqdm(total=100, desc="Performing RCA", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
        # Start spinner to show activity during progress
        spinner = ASCIISpinner(style='dots', speed=0.15, prefix="Processing... ")
        spinner.start()
        
        try:
            # Handle different input modes with Docling
            if logfile_path and os.path.exists(logfile_path):
                # Traditional mode: analyze specific log file with Docling
                print(f"\nParsing log file with Docling: {logfile_path}")
                parsed_log = scanner.docling_parser.parse_log_file(logfile_path)
                
                if 'error' in parsed_log:
                    raise FileNotFoundError(f"Failed to parse log file: {parsed_log['error']}")
                
                log_content = parsed_log['content']
                parsed_log_metadata = parsed_log['metadata']
                error_patterns = scanner.docling_parser.extract_error_patterns(parsed_log)
                
                print(f"Parsing method: {parsed_log['parsing_method']}")
                print(f"Document type detected: {parsed_log_metadata.get('document_type', 'unknown')}")
                if error_patterns:
                    print(f"Found {len(error_patterns)} error patterns")
                
                pbar.update(25)  # 25% complete after parsing log file
            elif scan_system:
                # Enhanced mode: scan system logs automatically with Docling
                print(f"\nScanning system logs for errors in the last {hours_back} hours...")
                if scanner.docling_parser.is_docling_available():
                    print("Using Docling for enhanced log parsing")
                else:
                    print("Using fallback parsing (Docling not available)")
                    
                system_errors = scanner.scan_system_logs(hours_back)
                
                if system_errors:
                    # Combine content from all sources
                    content_parts = []
                    all_error_patterns = []
                    
                    for source, error_data in system_errors.items():
                        if isinstance(error_data, dict):
                            content_parts.append(f"=== {source.upper()} LOGS ===\n{error_data.get('content', '')}")
                            all_error_patterns.extend(error_data.get('error_patterns', []))
                            if 'parsed_files' in error_data:
                                print(f"  {source}: {len(error_data['parsed_files'])} files processed")
                        else:
                            # Fallback for old format
                            content_parts.append(f"=== {source.upper()} LOGS ===\n{error_data}")
                    
                    log_content = "\n\n".join(content_parts)
                    error_patterns = all_error_patterns
                    
                    print(f"Found errors in: {', '.join(system_errors.keys())}")
                    if error_patterns:
                        print(f"Extracted {len(error_patterns)} error patterns")
                else:
                    print("No recent system errors found in accessible logs.")
                    log_content = "No recent system errors detected in standard log locations."
                pbar.update(35)  # 35% complete after system scan
            elif logfile_path:
                raise FileNotFoundError(f"Log file not found: {logfile_path}")
            else:
                # Interactive mode: minimal analysis with system context only
                log_content = "No specific log file provided - analysis based on error description and system context."
                pbar.update(15)  # 15% complete for quick analysis
            
            # Classify error type for specialized analysis (enhanced with error patterns)
            error_type = scanner.classify_error_type(error_desc, log_content)
            print(f"Error classified as: {error_type.upper()}")
            pbar.update(15)  # 15% more complete after classification
        
            # Assess impact level (enhanced with error patterns)
            impact_level = scanner.assess_impact(error_desc, log_content)
            print(f"Impact level: {impact_level.upper()}")
            pbar.update(10)  # 10% more complete after impact assessment
            
            # Gather additional context based on error type and impact
            additional_context = {
                'docling_metadata': parsed_log_metadata,
                'error_patterns': error_patterns[:20],  # Limit to first 20 patterns
                'docling_available': scanner.docling_parser.is_docling_available()
            }
            
            if error_type == SystemErrorTypes.CONTAINER:
                additional_context["container_health"] = container_monitor.get_container_health()
                
            if impact_level in [ImpactLevel.CRITICAL, ImpactLevel.HIGH] or triage_mode:
                additional_context["resource_usage"] = resource_monitor.get_top_info()
                additional_context["cpu_info"] = resource_monitor.get_cpu_info()
                
            # Build enhanced prompt with Docling insights
            prompt = build_enhanced_prompt(error_desc, log_content, error_type, system_context, 
                                         impact_level, additional_context, triage_mode)
            pbar.update(10)  # 10% more complete after prompt building
            
            # Initialize the Granite model via BeeAI
            model = ChatModel.from_name("ollama:granite3.3:8b-beeai")
            user_msg = UserMessage(prompt)
            
            # Show progress during model analysis with enhanced spinner
            pbar.set_description("Analyzing with Granite model")
            spinner.stop()  # Stop the initial spinner
            
            # Start a new spinner specifically for model analysis
            with ASCIISpinner(style='braille', speed=0.08, prefix="AI Analysis... ") as model_spinner:
                response = await model.create(messages=[user_msg])
            
            pbar.update(30)  # 30% more complete after model analysis
            
            # Extract text content from response
            if isinstance(response, list) and len(response) > 0:
                if hasattr(response[0], "text"):
                    analysis = response[0].text
                else:
                    analysis = str(response[0])
            elif hasattr(response, "messages"):
                messages = response.messages
                if isinstance(messages, list) and len(messages) > 0 and hasattr(messages[0], "text"):
                    analysis = messages[0].text
                else:
                    analysis = str(messages)
            elif hasattr(response, "text"):
                analysis = response.text
            else:
                analysis = str(response)
                
            # Save report with lessons learned and Docling metadata
            report = {
                "timestamp": datetime.now().isoformat(),
                "error_description": error_desc,
                "error_type": error_type,
                "impact_level": impact_level,
                "analysis": analysis,
                "system_context": system_context,
                "additional_context": additional_context,
                "docling_parsing": {
                    "available": scanner.docling_parser.is_docling_available(),
                    "metadata": parsed_log_metadata,
                    "error_patterns_found": len(error_patterns)
                },
                "lessons_learned": {
                    "root_cause": "To be filled after resolution",
                    "preventive_measures": "To be filled after resolution",
                    "improvement_areas": "To be filled after resolution"
                }
            }
            
            # Save report to temporary directory
            report_path = resource_monitor.save_report(report)
            print(f"\nReport saved to: {report_path}")
            
            return analysis
            
        except Exception as e:
            raise Exception(f"Failed to get response from model: {e}")
        finally:
            # Always stop the spinner, even if an exception occurs
            spinner.stop() 
