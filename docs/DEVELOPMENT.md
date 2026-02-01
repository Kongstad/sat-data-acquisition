# Development

## Using the Makefile

The project includes a `Makefile` to simplify common development tasks.

**Linting and Type Checking:**
```bash
make lint
```
This runs `ruff`, `flake8`, and `mypy` to ensure code quality and type safety.

**Code Formatting:**
```bash
make format
```
This automatically formats the code using `black` and `isort`.

**Running Tests:**
```bash
# Run all tests
make test

# Run fast tests only (skips slow integration tests)
make test-fast

# Run tests with coverage report
make test-cov
```

**Cleanup:**
```bash
make clean
```
Removes build artifacts, cache files, and temporary test data.

**Versioning and Releases:**
The project uses `tbump` for version management. To release a new version:
```bash
# Example: bump to 0.2.0
tbump 0.2.0
```
This will automatically:
1. Run linting and tests
2. Update version strings in `pyproject.toml` and `sat_data_acquisition/__version__.py`
3. Create a Git commit and tag
4. Push the changes and tag to the remote repository

## Manual Testing

You can also run pytest directly:
```bash
pytest tests/
```

## Docker Deployment (Optional)

```bash
# Build image
docker build -t sat-data-acquisition .

# Run container
docker run -v $(pwd)/data:/app/data sat-data-acquisition
```

## Environment Variables

```bash
# AWS credentials for S3 (optional)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# Logging level (optional)
export LOG_LEVEL=INFO
```
