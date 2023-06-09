# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set log level. (INFO, DEBUG, WARNING, ERROR, CRITICAL)
ENV LOG_LEVEL INFO

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Set the working directory in the container to /app
WORKDIR /app

# Add the requirements.txt file to the container
ADD ./webapp/requirements.txt ./webapp/

# Install the PostgreSQL client library
RUN apt-get update && apt-get install -y libpq-dev gcc

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r webapp/requirements.txt

# Install Uvicorn
RUN pip install --no-cache-dir uvicorn

# Remove unnecessary packages
RUN apt-get autoremove -y gcc

# Copy the current directory into the container at /app
COPY ./webapp ./webapp

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the application when the container launches
CMD ["uvicorn", "webapp.main:app", "--host", "0.0.0.0", "--port", "80"]
