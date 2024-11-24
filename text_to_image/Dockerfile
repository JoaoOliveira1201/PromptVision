# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .


# Expose the port on which the app runs
EXPOSE 7050


# Set the command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7050"]
