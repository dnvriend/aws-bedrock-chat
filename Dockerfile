# Use Python 3.12 slim image
FROM python:3.12-slim

ENV STREAMLIT_SERVER_PORT=8080

ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app into the container
COPY app.py .

# Expose the port that Streamlit runs on
EXPOSE 8050

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]