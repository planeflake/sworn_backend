# Use an official Python runtime as a base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY . .

# Set the environment variable to enable Flask development mode
ENV FLASK_ENV=development

# Expose port 5000 (or whichever port your Flask app uses)
EXPOSE 5000

# Define the default command to run your Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
