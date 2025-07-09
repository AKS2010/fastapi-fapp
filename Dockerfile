# Use Azure Functions Python base image
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# Install ODBC dependencies (for pyodbc)
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    msodbcsql17 \
    libpq-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /home/site/wwwroot

# Copy app files into container
COPY . /home/site/wwwroot

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port (for local testing)
EXPOSE 8080
