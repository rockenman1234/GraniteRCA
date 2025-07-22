"""
Utility functions and helpers for the RCA system.

This module provides supporting functionality for the RCA system, including
system context gathering, prompt building, and output formatting utilities.
These functions are used by the core RCA functionality to enhance its capabilities.

SPDX-License-Identifier: Apache-2.0
"""

import re
import subprocess
from datetime import datetime
from rca_core import SystemErrorTypes, ImpactLevel

def get_system_context():
    """Gather relevant system context information."""
    context = {}
    
    # Get system info
    try:
        context['os_info'] = subprocess.run(['uname', '-a'], capture_output=True, text=True, timeout=5).stdout.strip()
    except:
        context['os_info'] = "Unable to determine OS info"
    
    # Get SELinux status
    try:
        context['selinux_status'] = subprocess.run(['getenforce'], capture_output=True, text=True, timeout=5).stdout.strip()
    except:
        context['selinux_status'] = "SELinux status unknown"
    
    # Get memory info
    try:
        with open('/proc/meminfo', 'r') as f:
            mem_lines = f.readlines()[:5]  # First 5 lines contain key info
            context['memory_info'] = ''.join(mem_lines)
    except:
        context['memory_info'] = "Memory info unavailable"
    
    # Get disk space
    try:
        context['disk_space'] = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5).stdout
    except:
        context['disk_space'] = "Disk space info unavailable"
    
    # Get system load
    try:
        with open('/proc/loadavg', 'r') as f:
            context['system_load'] = f.read().strip()
    except:
        context['system_load'] = "System load unavailable"
    
    return "\n".join([f"{k}: {v}" for k, v in context.items()])

def build_enhanced_prompt(error_desc, log_lines, error_type, system_context, impact_level, additional_context=None, triage_mode=False):
    """
    Constructs an enhanced prompt for comprehensive system diagnostics.
    """
    
    type_specific_guidance = {
        SystemErrorTypes.KERNEL: """
Focus on kernel-level issues:
- Memory management problems
- Hardware compatibility issues
- Driver conflicts
- Kernel module problems
- System resource exhaustion
""",
        SystemErrorTypes.SELINUX: """
Focus on SELinux security policy issues:
- Permission denials and context mismatches
- Policy rule violations
- File context labeling problems
- Service access restrictions
- Boolean policy settings
""",
        SystemErrorTypes.JAVA: """
Focus on JVM and Java application issues:
- ClassPath and dependency problems
- Memory heap and garbage collection issues
- Thread deadlocks and concurrency problems
- Library version conflicts
- JVM configuration issues
""",
        SystemErrorTypes.BOOT: """
Focus on system boot and initialization issues:
- Bootloader configuration problems
- Initramfs and kernel loading issues
- File system mount failures
- Service startup dependencies
- Hardware initialization problems
""",
        SystemErrorTypes.CONTAINER: """
Focus on container-related issues:
- Container runtime problems
- Resource constraints and limits
- Network connectivity issues
- Volume mount problems
- Container orchestration issues
"""
    }
    
    impact_guidance = {
        ImpactLevel.CRITICAL: """
CRITICAL IMPACT - System-wide outage or data loss risk:
- Focus on immediate service restoration
- Prioritize data integrity and recovery
- Consider system-wide implications
- Plan for failover if available
""",
        ImpactLevel.HIGH: """
HIGH IMPACT - Major service disruption:
- Focus on core service functionality
- Check dependent services
- Monitor resource usage
- Consider service dependencies
""",
        ImpactLevel.MEDIUM: """
MEDIUM IMPACT - Partial service degradation:
- Focus on performance optimization
- Check resource utilization
- Monitor error rates
- Consider scaling options
""",
        ImpactLevel.LOW: """
LOW IMPACT - Minor issues:
- Focus on service improvements
- Check configuration settings
- Monitor for escalation
- Consider preventive measures
"""
    }
    
    guidance = type_specific_guidance.get(error_type, "Focus on application-level debugging strategies.")
    impact = impact_guidance.get(impact_level, "Assess impact based on service criticality.")
    
    # Add triage mode guidance if enabled
    triage_guidance = """
TRIAGE MODE - Live outage in progress:
- Focus on immediate service restoration
- Prioritize critical systems
- Gather essential diagnostics
- Document actions taken
- Plan for post-incident review
""" if triage_mode else ""
    
    # Add Docling parsing information if available
    docling_info = ""
    if additional_context and "docling_metadata" in additional_context:
        metadata = additional_context["docling_metadata"]
        error_patterns = additional_context.get("error_patterns", [])
        docling_available = additional_context.get("docling_available", False)
        
        docling_info = f"""
DOCUMENT PARSING INFORMATION:
- Parsing engine: {"Docling (enhanced)" if docling_available else "Basic text parser"}
- Document type: {metadata.get('document_type', 'unknown')}
- Structure elements: {metadata.get('structure_elements', 0)}
- Error patterns detected: {len(error_patterns)}
"""
        
        if error_patterns:
            docling_info += "\nKEY ERROR PATTERNS DETECTED:\n"
            for i, pattern in enumerate(error_patterns[:5], 1):  # Show first 5 patterns
                category = pattern.get('category', 'unknown')
                match = pattern.get('match', '')
                docling_info += f"{i}. {category.upper()}: {match}\n"
    
    # Add container health info if available
    container_info = ""
    if additional_context and "container_health" in additional_context:
        container_info = "\nCONTAINER HEALTH INFORMATION:\n" + str(additional_context["container_health"])
    
    # Add resource usage info if available
    resource_info = ""
    if additional_context and ("resource_usage" in additional_context or "cpu_info" in additional_context):
        resource_info = "\nRESOURCE USAGE INFORMATION:\n"
        if "resource_usage" in additional_context:
            resource_info += str(additional_context["resource_usage"])
        if "cpu_info" in additional_context:
            resource_info += "\nCPU INFORMATION:\n" + str(additional_context["cpu_info"])
    
    return f"""You are an expert system administrator and diagnostic specialist with deep knowledge of Linux systems, security policies, application frameworks, and hardware troubleshooting.

ERROR CLASSIFICATION: {error_type.upper()}
IMPACT LEVEL: {impact_level.upper()}

The user is reporting the following error:
"{error_desc}"

SYSTEM CONTEXT:
{system_context}

LOG ANALYSIS DATA:
{log_lines}

{docling_info}
{container_info}
{resource_info}

SPECIALIZED GUIDANCE:
{guidance}

IMPACT ASSESSMENT:
{impact}

{triage_guidance}

Provide a comprehensive diagnostic analysis with the following structure:

## Root Cause Analysis
Identify the primary cause and any contributing factors.

## Technical Evidence
Point to specific log entries, error codes, or system indicators that support your analysis.

## Impact Assessment
Describe what systems/services are affected and the severity level.

## Immediate Fix
Provide step-by-step instructions for immediate resolution.

## Long-term Prevention
Suggest monitoring, configuration changes, or best practices to prevent recurrence.

## Advanced Diagnostics
If the issue persists, provide additional diagnostic commands and investigation steps.

## Security Considerations
Highlight any security implications and recommended security measures.

## Lessons Learned
Suggest improvements to prevent similar issues in the future.

Be specific with command examples, file paths, and configuration snippets where applicable.
"""

def format_output(analysis):
    """Enhanced output formatting with better readability."""
    if not isinstance(analysis, str):
        return str(analysis)
    
    # Apply text formatting
    formatted = analysis.replace('\\n', '\n')
    
    # Bold headers (## pattern)
    formatted = re.sub(r'^##\s*(.*?)$', r'\033[1;4m\1\033[0m', formatted, flags=re.MULTILINE)
    
    # Bold important text (**pattern**)
    formatted = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', formatted)
    
    # Highlight commands with backticks
    formatted = re.sub(r'`([^`]+)`', r'\033[93m\1\033[0m', formatted)
    
    # Color code blocks
    formatted = re.sub(r'```(.*?)```', r'\033[96m\1\033[0m', formatted, flags=re.DOTALL)
    
    return formatted 
