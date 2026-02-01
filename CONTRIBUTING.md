# Contributing to Satellite Data Acquisition

Thank you for your interest in contributing to this project! This is a portfolio project designed to demonstrate clean code practices, and contributions are welcome.

## Code Quality Standards

To maintain high code quality, we follow these principles:

- **Type Safety**: Use type hints throughout the codebase.
- **Validation**: Use Pydantic models for data validation.
- **Error Handling**: Implement comprehensive error handling and clear exception messages.
- **Documentation**: Keep documentation up-to-date with any code changes.
- **Testing**: Ensure all new features or bug fixes include corresponding tests.

## Development Setup

We recommend using `uv` for development:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Workflow

1. **Format and Lint**: Run `make format` and `make lint` before committing.
2. **Test**: Run `make test` to ensure all tests pass.
3. **Pull Requests**: Open a pull request with a clear description of your changes.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
