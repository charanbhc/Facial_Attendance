# Use an official Python runtime as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python code file, images folder, and attendance.csv file
COPY attendance.py .
COPY images/ images/
COPY Attendance.csv .

# Set the entry point command for running the Python script
CMD [ "python", "attendance.py" ]
