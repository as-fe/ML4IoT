# Use official TensorFlow base image with Python 3.11
FROM tensorflow/tensorflow:latest

# Set work directory
WORKDIR /app

# Install system dependencies (optional)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy your code
COPY . /app

# Create uploads directory
RUN mkdir -p /app/uploads

# Install Python dependencies
RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
RUN pip install --no-cache-dir --upgrade --ignore-installed -r requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
