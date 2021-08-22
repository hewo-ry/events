export BUILD="$(cat /app/.build)"

# Wait for Postgres befor starting the container
until PGPASSWORD=$DB_PASS psql -h "db" -U "$DB_USER" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

# Update database
alembic upgrade heads

# Install
python3.8 install.py
