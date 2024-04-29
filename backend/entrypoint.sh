#!/bin/bash
# entrypoint.sh

# Default values of arguments
host="0.0.0.0"
port="8000"
debug_port="5678" # Debugging port for debugpy

# Substitute environment variables in, if provided
if [ ! -z "$SERVER_HOST" ]; then
    host=$SERVER_HOST
fi

if [ ! -z "$SERVER_PORT" ]; then
    port=$SERVER_PORT
fi

# Debugging setup
if [ "$DEBUG_MODE" = "true" ]; then
    echo "Starting in debug mode on port $debug_port"
    python -m debugpy --listen $host:$debug_port --wait-for-client -m uvicorn app.main:app --host $host --port $port --reload
else
    echo "Starting in normal mode"
    exec uvicorn app.main:app --host $host --port $port --reload
fi