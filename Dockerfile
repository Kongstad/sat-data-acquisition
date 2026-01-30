FROM python:3.12-slim

# Install system dependencies for geospatial libraries
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency file
COPY pyproject.toml ./

# Install UV for faster package installation
RUN pip install --no-cache-dir uv

# Install dependencies from pyproject.toml
RUN uv pip install --system -e .

# Copy application code
COPY sat_data_acquisition/ ./sat_data_acquisition/
COPY data/ ./data/
COPY examples/ ./examples/

# Set Python path
ENV PYTHONPATH=/app

# Default command
CMD ["python"]
