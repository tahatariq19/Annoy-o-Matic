# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create a volume for the database to persist data
VOLUME ["/app/data"]

# Environment variable to override for the database path if needed
# The code expects the db in the current dir by default, so we might need a small tweak or just mount /app
# For simplicity in this PR, we assume the user mounts /app or we just let it be ephemeral if not mounted.

# Command to run the bot
CMD ["python", "main.py"]
