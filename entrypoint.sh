#!/bin/sh

# Ensure the database directory exists before starting
mkdir -p $(dirname $DB_PATH)

# Start the Flask web dashboard in the background
echo "Starting OpenWrt Traffic Web Dashboard on port 5000..."
python3 web/app.py &

# Start the mitmproxy sniffer in the foreground
echo "Starting Mitmproxy on port 8080..."
exec mitmdump -q --mode transparent --ssl-insecure --no-http2 -s sniffer/proxy_addon.py
