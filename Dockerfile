# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies
# ffmpeg for audio processing
# libopenblas-dev for scipy/numpy
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
# We use --no-cache-dir to keep the image small
RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create folders for uploads and processed files
RUN mkdir -p uploads processed

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application using Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--timeout", "120"]
