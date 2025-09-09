# Use Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing pyc files & buffer logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the backend code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose Django port
EXPOSE 8000

# Run Gunicorn server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
