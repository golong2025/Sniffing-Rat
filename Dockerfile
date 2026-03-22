FROM mitmproxy/mitmproxy:10.2.4

# Switch to root to install python packages
USER root

# Install iptables and Python dependencies
RUN apt-get update -qq && apt-get install -y --no-install-recommends iptables && \
    pip3 install --no-cache-dir flask flask-cors pillow pillow-heif && \
    rm -rf /var/lib/apt/lists/*

# Set up the application directory
WORKDIR /app
COPY . /app

# Install Universal CA Certificates
COPY certs /root/.mitmproxy/

# Expose Web Dashboard (5000) and Mitmproxy (8080)
EXPOSE 5000
EXPOSE 8080

# Configure default database path to be mapped via volume
ENV DB_PATH=/app/db/monitor.db

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
