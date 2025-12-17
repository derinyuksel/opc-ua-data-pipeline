FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install asyncua

# Copy server code
COPY server.py .

# Run the server
CMD ["python", "server.py"]