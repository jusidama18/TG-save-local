FROM ubuntu:latest

# Set working directory
WORKDIR /app

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip git

# Copy app files to container
COPY . .

# Install app dependencies
RUN pip3 install --no-cache-dir -U -r requirements.txt

# Start app
CMD ["python3", "-m", "src"]