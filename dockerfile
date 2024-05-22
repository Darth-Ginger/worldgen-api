# Use a lightweight Python image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files into the container
COPY . /app/

# Expose any necessary ports
EXPOSE 5000

# Command to run your application
CMD ["python", "app.py"]
