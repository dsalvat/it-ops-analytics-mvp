#!/bin/sh

# Wait for MySQL to be ready
until nc -z mysql 3306;
do
  echo "Waiting for MySQL..."
  sleep 1
done

echo "MySQL is up - executing command"

# Execute the main command (e.g., uvicorn)
exec "$@"