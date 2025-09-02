# Contributing to Benchmark

First off, thank you for considering contributing to Benchmark! It's people like you that make open-source software a great community.

## Code of Conduct

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs
- Ensure the bug was not already reported by searching in [GitHub Issues](https://github.com/Nsfr750/benchmark/issues).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/Nsfr750/benchmark/issues/new).
- Be sure to include a title and clear description, and as much relevant information as possible.

### Suggesting Enhancements
- Open a new issue with a clear title and description.
- Explain why this enhancement would be useful.
- Include any relevant screenshots or mockups.

### Pull Requests
1. Fork the repository and create your branch from `main`.
2. Install development dependencies: `pip install -r requirements-dev.txt`
3. Make your changes following the project's coding style.
4. Add tests if applicable.
5. Ensure all tests pass: `pytest`
6. Update the documentation if needed.
7. Submit a pull request with a clear description of changes.

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `.\venv\Scripts\activate`
   - Unix/macOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

## Coding Standards
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all new code
- Write docstrings following [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Format code with [Black](https://github.com/psf/black)

## Testing
- Write tests for new features and bug fixes
- Run tests with: `pytest`
- Ensure test coverage remains high

## License
By contributing, you agree that your contributions will be licensed under its GPL-3.0 License.
