# Project Structure

## Essential Files for Docker

```
sat-data-acquisition/
├── pyproject.toml          # Package definition & dependencies (REQUIRED)
├── Dockerfile              # Docker build instructions
├── docker-compose.yml      # Docker orchestration
├── .dockerignore          # Exclude files from Docker build
├── .env.example           # Template for environment variables
├── sat_data_acquisition/  # Main package code (REQUIRED)
└── examples/              # Usage examples
```

## Files by Purpose

### Required for Both Docker & Local Dev
- `pyproject.toml` - Defines package, dependencies, Python version
- `sat_data_acquisition/` - The actual Python package
- `.env.example` - Template for configuration

### Docker Only
- `Dockerfile` - Container definition
- `docker-compose.yml` - Easy container management
- `.dockerignore` - Optimize build context

### Local Development Only
- `.venv/` or `venv/` - Virtual environment (ignored by Docker)
- `.python-version` - Auto-detects Python 3.12 for tools like pyenv/uv
- `.pre-commit-config.yaml` - Git hooks for code quality
- `Makefile` - Development shortcuts
- `.gitignore` - Git exclusions

### Data & Config (Runtime)
- `.env` - Your actual config (copy from .env.example, gitignored)
- `data/` - Image downloads and logs

## Quick Reference

### Local Development
```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .
```

### Docker
```bash
docker-compose up -d
docker-compose exec sat-data-acquisition python
```

### Why .env.example?
- `.env.example` is a template committed to git
- You copy it to `.env` and add your secrets
- `.env` is gitignored to protect credentials
- Standard practice for all projects with config
