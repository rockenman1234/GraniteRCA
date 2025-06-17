# GraniteRCA - Enhanced System Diagnostic Root Cause Analysis

GraniteRCA is a powerful system diagnostic tool that performs comprehensive root cause analysis (RCA) on Linux systems. It combines advanced log analysis, system context gathering, and AI-powered diagnostics to help identify and resolve system issues quickly and effectively.

## Features

- **Multi-mode Operation**
  - Basic mode for analyzing specific log files
  - System scan mode for automatic log scanning
  - Quick analysis mode for rapid diagnostics
  - Triage mode for live outage situations

- **Context-aware Impact Scoring**
  - Automatic impact level assessment (Critical, High, Medium, Low, Info)
  - Impact-based diagnostic prioritization
  - Service dependency analysis
  - Resource usage correlation

- **Smart Resource Monitoring**
  - CPU and memory usage tracking
  - Process-level resource analysis
  - System load monitoring
  - Log bundling and correlation

- **Container Health Monitoring**
  - Support for both Docker and Podman
  - Container resource usage tracking
  - Container log analysis
  - Container state monitoring

- **Enhanced Diagnostics**
  - AI-powered analysis using Granite model
  - Pattern-based error classification
  - System context gathering
  - Security policy analysis

- **Report Generation**
  - JSON-formatted reports
  - Lessons learned tracking
  - Impact assessment
  - Actionable recommendations

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

3. Ensure you have the required system packages:
```bash
# For container monitoring
sudo dnf install podman docker  # Fedora/RHEL
# or
sudo apt install podman docker  # Debian/Ubuntu
```

## Usage

### Basic Mode
```bash
python rca_agent.py --error "Error description" --logfile path/to/logfile
```

### System Scan Mode
```bash
python rca_agent.py --error "Error description" --scan-system [--hours 24]
```

### Quick Analysis Mode
```bash
python rca_agent.py --error "Error description"
```

### Triage Mode (for live outages)
```bash
python rca_agent.py --error "Error description" --triage [--scan-system]
```

## Options

- `--error TEXT`: Description of the error (required)
- `--logfile PATH`: Path to specific log file to analyze
- `--scan-system`: Automatically scan system logs for recent errors
- `--hours N`: Hours back to scan for errors (default: 24)
- `--triage`: Run in triage mode for live outages
- `--help, -h`: Show help message
- `--license, -l`: Show license information

## Supported Error Types

- Linux kernel errors and panics
- SELinux policy violations
- Java/JVM exceptions and errors
- systemd service failures
- Network connectivity issues
- Boot and initialization problems
- Application-level errors
- Hardware-related issues
- Container runtime issues

## Report Structure

Each analysis generates a comprehensive report including:

1. **Root Cause Analysis**
   - Primary cause identification
   - Contributing factors
   - Error classification

2. **Technical Evidence**
   - Log entries
   - Error codes
   - System indicators

3. **Impact Assessment**
   - Affected systems/services
   - Severity level
   - Service dependencies

4. **Immediate Fix**
   - Step-by-step resolution
   - Emergency procedures
   - Service restoration

5. **Long-term Prevention**
   - Monitoring recommendations
   - Configuration changes
   - Best practices

6. **Advanced Diagnostics**
   - Additional commands
   - Investigation steps
   - Debugging procedures

7. **Security Considerations**
   - Security implications
   - Policy violations
   - Recommended measures

8. **Lessons Learned**
   - Root cause analysis
   - Preventive measures
   - Improvement areas

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- BeeAI Framework for AI model integration
- Ollama for Granite model support
- Linux community for system diagnostic tools
