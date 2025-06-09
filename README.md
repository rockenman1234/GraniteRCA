# GraniteRCA

A powerful Root Cause Analysis (RCA) tool that leverages IBM Granite via the BeeAI framework to analyze system errors and provide detailed diagnostics. This tool can analyze various types of system issues, from kernel panics to application errors, and provide actionable solutions.

## Features

- Multi-mode operation (file-based, system-wide scan, or quick analysis)
- Automatic error classification
- System context gathering
- Progress indication during analysis
- Specialized analysis based on error type
- Support for various error types:
  - Linux kernel errors and panics
  - SELinux policy violations
  - Java/JVM exceptions
  - systemd service failures
  - Network connectivity issues
  - Boot and initialization problems
  - Application-level errors
  - Hardware-related issues

## Dependencies

### Python Dependencies
The tool requires the following Python packages (automatically installed via pip):
- `beeai-framework>=1.0.0`: Framework for AI model interaction
- `tqdm>=4.65.0`: Progress bar functionality

### System Dependencies
The following system-level dependencies must be installed separately:

1. **Python Environment**
   - Python 3.8 or higher
   - pip package manager

2. **Ollama**
   - Ollama installed and running
   - Granite model available: `granite3.3:8b-beeai`

3. **System Access**
   - Read access to system log directories (typically `/var/log/`)
   - Permission to execute system commands for context gathering
   - SELinux status checking capability (if analyzing SELinux issues)

### Installing Dependencies

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Ollama (if not already installed):
```bash
# For Linux/macOS
curl https://ollama.ai/install.sh | sh
```
- For Windows - Download from https://ollama.ai/download


3. Install the BeeAI framework from [Homebrew](https://brew.sh/) (Ollama only for now), and setup your LLM provider.
```bash
brew install i-am-bee/beeai/beeai
beeai platform start
beeai env setup
```

4. Verify system access:
```bash
# Test log directory access
ls -l /var/log/

# Test system command execution
uname -a
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GraniteRCA.git
cd GraniteRCA
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```


## Usage

### Basic Mode (Analyze Specific Log File)

```bash
python rca_agent.py --error "Service failed to start" --logfile /var/log/service.log
```

### System Scan Mode (Automatic Log Scanning)

```bash
python rca_agent.py --error "System is running slowly" --scan-system
```

### Quick Analysis Mode (Error Description Only)

```bash
python rca_agent.py --error "Database connection timeout"
```

### Advanced Options

- Scan logs from a specific time period:
```bash
python rca_agent.py --error "Service failure" --scan-system --hours 48
```

- Combine log file with system scan:
```bash
python rca_agent.py --error "Application crash" --logfile app.log --scan-system
```

## Example Output

```
=== Enhanced System Diagnostic RCA Report ===
Mode: SYSTEM_SCAN
Timestamp: 2024-03-14 15:30:45
==================================================

Scanning system logs for errors in the last 24 hours...
Found errors in: journal, system, application

Error classified as: SYSTEMD

## Root Cause Analysis
The service failure is caused by a dependency issue with the database service.

## Technical Evidence
- systemd[1234]: Failed to start database.service
- systemd[1234]: database.service: Main process exited, code=exited, status=1/FAILURE
- systemd[1234]: database.service: Failed with result 'exit-code'

## Impact Assessment
- Database service is down
- Applications depending on the database are affected
- Severity: High

## Immediate Fix
1. Check database configuration:
   sudo systemctl status database.service
2. Verify database credentials
3. Restart the service:
   sudo systemctl restart database.service

## Long-term Prevention
- Implement service monitoring
- Set up automatic recovery
- Regular configuration audits

## Advanced Diagnostics
If the issue persists:
1. Check database logs:
   sudo journalctl -u database.service
2. Verify disk space:
   df -h
3. Check system resources:
   top

## Security Considerations
- Review database access permissions
- Ensure proper credential management
- Monitor for unauthorized access attempts
```

## Supported Error Types

### Kernel Errors
- Memory management issues
- Hardware compatibility problems
- Driver conflicts
- Kernel module issues
- System resource exhaustion

### SELinux Issues
- Permission denials
- Policy rule violations
- File context labeling problems
- Service access restrictions
- Boolean policy settings

### Java/JVM Problems
- ClassPath and dependency issues
- Memory heap and garbage collection
- Thread deadlocks
- Library version conflicts
- JVM configuration

### Boot Problems
- Bootloader configuration
- Initramfs and kernel loading
- File system mount failures
- Service startup dependencies
- Hardware initialization

## Troubleshooting

If you encounter issues:

1. Verify log file permissions and paths
2. Check if BeeAI framework and Ollama are properly configured
3. Ensure granite3.3:8b-beeai model is available
4. Check system resource availability
5. Verify network connectivity to Ollama service

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GPLv2 License - see the LICENSE file for details.
