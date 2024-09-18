# The builder image, used to build the virtual environment
FROM python:3.10-slim AS builder

# A directory to have app data 
WORKDIR /app

# Copy only the necessary files for installing dependencies
# Install system dependencies
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && pip install --no-cache-dir -r requirements.txt

# Define environment variables for the paths
ENV PYTHON_LIB_PATH=/usr/local/lib/python3.10/site-packages
ENV PYTHON_BIN_PATH=/usr/local/bin

# Production stage (final image) - environment
FROM python:3.10-slim

# Copy necessary app files and dependencies from the builder stage
COPY --from=builder ${PYTHON_LIB_PATH} ${PYTHON_LIB_PATH}
COPY --from=builder ${PYTHON_BIN_PATH} ${PYTHON_BIN_PATH}

COPY . .

# Command to run the Streamlit app
CMD ["streamlit", "run", "DoChatBot.py", "--server.port", "8051"]