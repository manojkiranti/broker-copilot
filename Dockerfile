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

# Ensure .env is accessible inside the container
# COPY ./copilot/.env /app/copilot/.env

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=copilot.settings
ENV PYTHONUNBUFFERED=1


# Configure SSH
RUN mkdir -p /run/sshd && \
    sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config && \
    echo "ListenAddress 0.0.0.0" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "LoginGraceTime 180" >> /etc/ssh/sshd_config && \
    echo "X11Forwarding yes" >> /etc/ssh/sshd_config && \
    echo "Ciphers aes128-cbc,3des-cbc,aes256-cbc,aes128-ctr,aes192-ctr,aes256-ctr" >> /etc/ssh/sshd_config && \
    echo "MACs hmac-sha1,hmac-sha1-96" >> /etc/ssh/sshd_config && \
    echo "StrictModes yes" >> /etc/ssh/sshd_config && \
    echo "root:Docker!" | chpasswd  # Set a root password


# Expose port 8000 for the application and 2222 for SSH
EXPOSE 8000 2222

# Copy the entrypoint script and set execute permissions
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the entrypoint script to run the application and start SSH
ENTRYPOINT ["/entrypoint.sh"]
