# Use the official Python image from the Docker Hub
FROM python:3.12.0-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PEGASUS_MEDIA_ROOT=$PEGASUS_MEDIA_ROOT
ENV PEGASUS_MEDIA_URL=$PEGASUS_MEDIA_URL
ENV PEGASUS_DATABASE_URL=$PEGASUS_DATABASE_URL
ENV PEGASUS_SOCIAL_AUTH_REDIRECT_IS_HTTPS=0
ENV PEGASUS_SOCIAL_AUTH_GITHUB_KEY=$PEGASUS_SOCIAL_AUTH_GITHUB_KEY
ENV PEGASUS_SOCIAL_AUTH_GITHUB_SECRET=$PEGASUS_SOCIAL_AUTH_GITHUB_SECRET
ENV PEGASUS_SOCIAL_AUTH_GITHUB_REDIRECT_URI=$PEGASUS_SOCIAL_AUTH_GITHUB_REDIRECT_URI

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gettext-base \
    libgconf-2-4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    libnss3-dev \
    libxss-dev \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Set the working directory
WORKDIR /app
COPY uv.lock README.md pyproject.toml /app/
# Copy the project
COPY src /app/src/
#COPY src /app/

# Install Python dependencies
RUN cd /app  \
    && uv sync --no-dev

ENV PATH=/app/.venv/bin:/usr/local/bin:/usr/bin:/bin \
    DJANGO_SETTINGS_MODULE=albdif.config.settings \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src/__pypackages__/3.12/lib/:/app/src/ \
    VIRTUAL_ENV=/app/.venv \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Expose the port on which Django will run
EXPOSE 8000

# Run the application
CMD ["django-admin", "runserver", "0.0.0.0:8000"]
