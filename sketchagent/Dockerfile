FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.0

# Copy dependency files
COPY pyproject.toml ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi || \
    (poetry lock --no-update && poetry install --no-dev --no-interaction --no-ansi)

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

