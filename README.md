# Todos-FastAPI

FastAPI Learning

# The below instructions is to setup postgresql db - command notes

# Install the PostgreSQL Python driver

pip install "psycopg[binary]"

# Open PostgreSQL as the postgres superuser

sudo -u postgres psql

-- Create a new database
CREATE DATABASE todoapp;

-- List all databases
\l

-- Create a PostgreSQL user (role)
CREATE USER sanjay WITH PASSWORD 'your_password';

-- List all PostgreSQL users (roles)
\du

-- Grant the user access to the database
GRANT ALL PRIVILEGES ON DATABASE todoapp TO sanjay;

-- Exit psql
\q

# Check PostgreSQL service status

sudo systemctl status postgresql

# List PostgreSQL clusters and their ports/status

pg_lsclusters

# Show the PostgreSQL server port

sudo -u postgres psql -c "SHOW port;"

# Edit PostgreSQL configuration

sudo nano /etc/postgresql/18/main/postgresql.conf

# Restart PostgreSQL after configuration changes

sudo systemctl restart postgresql

# Connect as a specific PostgreSQL user to a specific database

psql -U sanjay -d todoapp -h localhost

# psql options

-U -> PostgreSQL user
-d -> Database name
-h -> Host (localhost)
