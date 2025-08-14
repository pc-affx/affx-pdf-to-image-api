FROM python:3.11-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install opencv-python-headless (lighter version)
RUN pip install --no-cache-dir \
    Flask==2.3.3 \
    pdf2image==1.16.3 \
    Pillow==10.0.1 \
    Werkzeug==2.3.7 \
    gunicorn==21.2.0 \
    opencv-python-headless==4.8.1.78 \
    numpy==1.24.3

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]