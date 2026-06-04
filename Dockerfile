FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV HERMES_HOME=/root/.hermes

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Hermes Agent
RUN curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Create app directory
WORKDIR /app

# Copy project files
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose port for dashboard
EXPOSE 8080

# Start Hermes and dashboard
CMD ["./start.sh"]