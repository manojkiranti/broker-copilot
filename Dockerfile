# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install OpenSSH server, wkhtmltopdf, and other dependencies
RUN apt-get update && apt-get install -y \
    openssh-server \
    wkhtmltopdf \
    libxrender1 \
    libfontconfig1 \
    && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=copilot.settings
ENV PYTHONUNBUFFERED=1

# Create SSH directory, set up SSH service, and configure SSH
RUN mkdir -p /run/sshd && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "root:Docker!" | chpasswd  # Set a root password

# Expose port 8000 for the application and 2222 for SSH
EXPOSE 8000 2222

# Copy the entrypoint script and set execute permissions
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the entrypoint script to run the application and start SSH
ENTRYPOINT ["/entrypoint.sh"]
