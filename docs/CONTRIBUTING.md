# Contributing to GraniteRCA

Thank you for your interest in contributing to GraniteRCA! 🎉🤘

This document provides guidelines and information for contributing to the project.

## Project Structure

```
GraniteRCA/
├── main.py                    # Main entry point wrapper
├── requirements.txt           # Python package dependencies
├── LICENSE.md                 # Apache 2.0 License
├── README.md                  # Project documentation and usage guide
├── src/                       # Source code directory
│   ├── __init__.py            # Package initialization
│   ├── rca_agent.py           # CLI interface and argument parsing
│   ├── rca_core.py            # Core RCA functionality and analysis logic
│   ├── rca_utils.py           # Utility functions and helper methods
│   ├── docling_utils.py       # Docling-based document parsing utilities
│   ├── container_monitor.py   # Container health monitoring (Docker/Podman)
│   ├── resource_monitor.py    # Resource monitoring and log bundling
│   └── spinner_utils.py       # Progress indicators and UI utilities
├── docs/                      # Documentation
│   ├── CONTRIBUTING.md        # This file
│   └── logo.png               # Project logo
└── tools/                     # Development and testing utilities
    ├── setup.sh               # Automated setup script
    ├── docling_test.py        # Docling configuration testing
    └── sample.log             # Sample log file for testing
```

### Key Components

1. **main.py**
   - Entry point wrapper that sets up Python path
   - Imports and calls rca_agent.main()
   - Simple runner for the application

2. **rca_agent.py**
   - Main CLI interface and command-line argument parsing
   - User interaction and coordination layer
   - License information display
   - Enhanced argument parsing for multiple operation modes
   - Error handling and user feedback

3. **rca_core.py**
   - Core RCA (Root Cause Analysis) functionality
   - SystemLogScanner class with Docling integration
   - Error classification and impact assessment
   - System-wide log scanning capabilities
   - Integration with BeeAI framework and Granite model
   - Progress tracking with visual indicators
   - Multiple operation modes (file-based, system scan, quick analysis)

4. **rca_utils.py**
   - Utility functions for system context gathering
   - Enhanced prompt building for AI analysis
   - Output formatting with improved readability
   - Error handling helpers
   - System information collection methods

5. **docling_utils.py**
   - DoclingLogParser class for enhanced document parsing
   - Support for multiple document formats (PDF, DOCX, HTML, MD, etc.)
   - Intelligent text extraction with structure preservation
   - Error pattern detection and extraction
   - Graceful fallback to basic parsing when Docling unavailable
   - Offline mode support with artifacts path

6. **container_monitor.py**
   - ContainerMonitor class for Docker and Podman support
   - Container health monitoring and status checking
   - Resource usage tracking for containers
   - Container log collection and analysis

7. **resource_monitor.py**
   - ResourceMonitor class for system resource monitoring
   - Log bundling with Docling-enhanced parsing
   - CPU, memory, and process information gathering
   - Comprehensive system report generation
   - Temporary file management for analysis

8. **spinner_utils.py**
   - ASCIISpinner class for visual progress indicators
   - Multiple spinner styles and animations
   - Background processing feedback
   - User experience enhancements during analysis

## Dependencies

### Python Packages
```
beeai-framework>=0.1.0  # Framework for AI model interaction
tqdm>=4.65.0           # Progress bar functionality
python-dateutil>=2.8.2 # Date parsing utilities
psutil>=5.9.0          # System resource monitoring
docker>=6.1.3          # Container monitoring support
podman>=0.1.0          # Podman container support
docling>=2.0.0         # Document parsing and text extraction
```

### System Requirements
- Python 3.8 or higher
- Ollama with granite3.3:8b-beeai model
- BeeAI framework (installed via package manager)
- System access to /var/log and other system directories

### Optional Dependencies (for enhanced parsing)
- poppler-utils (for PDF support)
- tesseract-ocr (for OCR capabilities)
- Various system log files with appropriate read permissions

## Development Setup

### Quick Setup (Recommended)
1. Clone the repository:
   ```bash
   git clone https://github.com/rockenman1234/GraniteRCA.git
   cd GraniteRCA
   ```

2. Run the automated setup script:
   ```bash
   cd tools
   bash setup.sh
   ```

### Manual Setup
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install system dependencies:
   ```bash
   # Install BeeAI framework
   # For Homebrew (macOS):
   brew install i-am-bee/beeai/beeai
   
   # For other systems, use uv:
   uv tool install beeai-cli
   
   # Install Ollama
   # Visit https://ollama.ai/ for installation instructions
   
   # Install optional Docling dependencies
   # For Ubuntu/Debian:
   sudo apt-get install poppler-utils tesseract-ocr
   
   # For macOS:
   brew install poppler tesseract
   ```

3. Setup AI framework:
   ```bash
   # Start BeeAI platform
   beeai platform start
   
   # Setup environment
   beeai env setup
   
   # Start Ollama
   ollama serve
   
   # Pull Granite model
   ollama pull granite3.3:8b-beeai
   ```

### Testing Your Setup
Run the Docling configuration test:
```bash
cd tools
python docling_test.py --test-parsing
```

Test basic functionality:
```bash
python main.py --error "Test error" --scan-system
```

## Code Style Guidelines

1. **Documentation**
   - All functions and classes should have comprehensive docstrings
   - Use clear type hints where possible
   - Include SPDX license identifiers in all source files
   - Document complex logic and algorithms
   - Keep README.md and this file updated with changes

2. **Code Formatting**
   - Follow PEP 8 guidelines for Python code
   - Use meaningful variable and function names
   - Keep functions focused and under 50 lines when possible
   - Use f-strings for string formatting
   - Add type hints for function parameters and return values

3. **Error Handling**
   - Use try-except blocks appropriately with specific exceptions
   - Provide meaningful error messages to users
   - Log errors at appropriate levels
   - Include graceful fallbacks (like Docling → basic parsing)
   - Handle file permissions and access issues gracefully

4. **Project Organization**
   - Keep source code in the `src/` directory
   - Place utilities and tools in the `tools/` directory
   - Update `src/__init__.py` when adding new modules
   - Maintain clear separation between CLI, core logic, and utilities

## Development Tips & Tricks

### Working with Docling
- Set `DOCLING_ARTIFACTS_PATH` environment variable for offline usage
- Test parsing with `tools/docling_test.py` before integrating new features
- Always provide fallback parsing when Docling is unavailable
- Use the DoclingLogParser class for consistent parsing behavior

### Debugging and Testing
- Use the `--triage` mode for testing live outage scenarios
- Test with various log file sizes and formats
- Verify container monitoring works with both Docker and Podman
- Test system scanning with different `--hours` values
- Use `tools/sample.log` for consistent testing

### Performance Considerations
- Limit log content to reasonable sizes (10KB chunks)
- Use progress bars for long-running operations
- Implement spinner animations for background tasks
- Cache system information when possible
- Clean up temporary files properly

### AI Model Integration
- Ensure Granite model is available before running analysis
- Handle model connection failures gracefully
- Provide meaningful feedback during model analysis
- Test both online and offline scenarios

## Testing

### Automated Testing
Run the setup script to validate your environment:
```bash
cd tools
bash setup.sh
```

### Manual Testing Scenarios

1. **Basic Functionality Tests**
   - Test with specific log files: `python main.py --logfile /path/to/log --error "description"`
   - Test system scanning: `python main.py --error "test error" --scan-system`
   - Test triage mode: `python main.py --error "critical issue" --triage`
   - Test quick analysis: `python main.py --error "simple test"`

2. **Docling Integration Tests**
   - Test with various document formats (PDF, DOCX, HTML)
   - Test offline mode with `DOCLING_ARTIFACTS_PATH` set
   - Test fallback behavior when Docling is unavailable
   - Verify error pattern extraction works correctly

3. **Container Monitoring Tests**
   - Test with Docker containers running
   - Test with Podman containers running
   - Test container health monitoring accuracy
   - Verify container log collection

4. **Resource Monitoring Tests**
   - Test system resource collection
   - Verify log bundling functionality
   - Test with high system load
   - Check temporary file cleanup

### Error Cases to Test
- Invalid log files and unsupported formats
- Missing file permissions and access denied scenarios
- Network connectivity issues during model interaction
- Invalid error descriptions and edge cases
- System resource constraints and memory limitations
- Large document processing (>10MB files)
- Offline model usage scenarios
- Container runtime failures
- Missing system dependencies

### Development Tools
- Use `tools/docling_test.py` for Docling-specific testing
- Monitor temporary file creation in `/tmp/granite_rca_*`
- Check progress indicators and spinner animations
- Validate output formatting and readability

## Pull Request Process

1. **Fork and Branch**
   - Fork the repository on GitHub
   - Create a feature branch: `git checkout -b feature/your-feature-name`
   - Use descriptive branch names (e.g., `feature/enhance-docling-parsing`)

2. **Development**
   - Make your changes following the code style guidelines
   - Add appropriate documentation and comments
   - Update type hints and docstrings
   - Test your changes thoroughly

3. **Testing**
   - Run the automated setup script: `cd tools && bash setup.sh`
   - Test with various scenarios and edge cases
   - Verify backward compatibility
   - Ensure no regressions in existing functionality

4. **Documentation**
   - Update this CONTRIBUTING.md if you add new components
   - Update README.md if you change user-facing functionality
   - Add inline documentation for complex code
   - Update the project structure diagram if needed

5. **Commit and Push**
   - Use clear, descriptive commit messages
   - Include relevant issue numbers if applicable
   - Push to your fork: `git push origin feature/your-feature-name`

6. **Submit Pull Request**
   - Create a pull request with a clear title and description
   - Reference any related issues
   - Include screenshots for UI changes
   - Be prepared to address code review feedback

## Common Development Tasks

### Adding a New Error Type
1. Add the error type to `SystemErrorTypes` in `rca_core.py`
2. Add corresponding patterns to `SystemLogScanner.__init__()`
3. Update error classification logic if needed
4. Test with relevant log samples

### Enhancing Docling Integration
1. Modify `DoclingLogParser` in `docling_utils.py`
2. Test with `tools/docling_test.py`
3. Ensure fallback behavior still works
4. Update supported formats documentation

### Adding Container Support
1. Extend `ContainerMonitor` in `container_monitor.py`
2. Add new runtime detection logic
3. Test with actual container environments
4. Update documentation for new runtimes

## License

This project is licensed under the Apache 2.0 License. By contributing, you agree to license your contributions under the same license.

## Contact

For questions or concerns, please open an issue in the GitHub repository.

## Troubleshooting Common Issues

### Docling Installation Issues
```bash
# Install with specific versions if needed
pip install docling==2.0.0

# For Apple Silicon Macs, ensure proper dependencies
pip install --upgrade torch torchvision
```

### BeeAI Connection Issues
```bash
# Restart BeeAI platform
beeai platform stop
beeai platform start
beeai env setup
```
> [!NOTE]
> This project is not affiliated with BeeAI, for BeeAI Framework bugs or errors - [please see their GitHub repo.](https://github.com/i-am-bee/beeai-framework)

### Container Monitoring Issues
```bash
# Ensure Docker is running
docker ps
# or check if Podman is running
podman ps
# Next check SystemD for errors
sudo systemctl status docker
sudo systemctl status podman
```

---

## Additional Resources

- [Project Repository](https://github.com/rockenman1234/GraniteRCA)
- [Apache 2.0 License](https://spdx.org/licenses/Apache-2.0.html)
- [BeeAI Framework Documentation](https://github.com/i-am-bee/beeai)
- [Ollama Documentation](https://ollama.ai/docs)
- [Docling Documentation](https://github.com/DS4SD/docling)
- [Python Type Hints Guide](https://docs.python.org/3/library/typing.html)
