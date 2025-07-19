# Contributing to GraniteRCA

Thank you for your interest in contributing to GraniteRCA! This document provides guidelines and information for contributing to the project.

## Project Structure

```
GraniteRCA/
├── rca_agent.py      # Main entry point and CLI interface
├── rca_core.py       # Core RCA functionality and analysis logic
├── rca_utils.py      # Utility functions and helper methods
├── requirements.txt  # Python package dependencies
├── LICENSE.md        # GPLv2 License
└── README.md         # Project documentation and usage guide
```

### Key Components

1. **rca_agent.py**
   - Main entry point for the application
   - Handles command-line argument parsing
   - Implements the CLI interface
   - Coordinates between core functionality and user interaction
   - License and warranty information

2. **rca_core.py**
   - Core RCA (Root Cause Analysis) functionality
   - Error analysis and pattern matching
   - System log scanning capabilities
   - Integration with BeeAI framework
   - Progress tracking and reporting

3. **rca_utils.py**
   - Utility functions for log parsing
   - Output formatting
   - Error handling
   - System information gathering
   - Helper methods for core functionality

## Dependencies

### Python Packages
```
beeai-framework>=1.0.0  # Core AI framework for analysis
tqdm>=4.65.0           # Progress bar functionality
```

### System Requirements
- Python 3.8 or higher
- BeeAI framework (installed via Homebrew)
- Ollama (for local LLM support)
- Granite 3.3 8B model

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/GraniteRCA.git
   cd GraniteRCA
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install system dependencies:
   ```bash
   # Install BeeAI framework
   uv tool install beeai-cli
   
   # Start BeeAI platform
   beeai platform start
   
   # Setup environment
   beeai env setup
   ```

## Code Style Guidelines

1. **Documentation**
   - All functions should have docstrings
   - Complex logic should be commented
   - Keep README.md and this file updated

2. **Code Formatting**
   - Follow PEP 8 guidelines
   - Use meaningful variable names
   - Keep functions focused and small
   - Add type hints where possible

3. **Error Handling**
   - Use try-except blocks appropriately
   - Provide meaningful error messages
   - Log errors when necessary

## Testing

1. **Manual Testing**
   - Test with various error scenarios
   - Verify log file parsing
   - Check system scan functionality
   - Validate output formatting

2. **Error Cases to Test**
   - Invalid log files
   - Missing permissions
   - Network issues
   - Invalid error descriptions
   - System resource constraints

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Update documentation if needed
5. Submit a pull request

## License

This project is licensed under the LGPLv3 License. By contributing, you agree to license your contributions under the same license.

## Contact

For questions or concerns, please open an issue in the GitHub repository.

## Additional Resources

- [LGPLv3 License](https://www.gnu.org/licenses/lgpl-3.0.html)
- [BeeAI Framework Documentation](https://github.com/i-am-bee/beeai)
- [Ollama Documentation](https://ollama.ai/docs) 