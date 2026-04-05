FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create non-root user
RUN useradd -m appuser

# Copy application files
COPY . .
RUN chown -R appuser:appuser /app
USER appuser

# Expose Streamlit port
EXPOSE 8501

HEALTHCHECK CMD curl --fail --max-time 5 http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
