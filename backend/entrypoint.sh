#!/bin/bash
# entrypoint.sh

# Default values of arguments
host="0.0.0.0"
port="8000"

# Substitute environment variables in if provided
if [ ! -z "$SERVER_HOST" ]; then
    host=$SERVER_HOST
fi

if [ ! -z "$SERVER_PORT" ]; then
    port=$SERVER_PORT
fi

# Run uvicorn with the host and port parameters
exec uvicorn app.main:app --host $host --port $port --reload