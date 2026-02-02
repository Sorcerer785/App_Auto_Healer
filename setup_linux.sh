#!/bin/bash

# Update package list
sudo apt-get update

# Install Python3, pip, and venv
sudo apt-get install -y python3 python3-pip python3-venv

# Install Redis
sudo apt-get install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Create DB and User (Interactive or default)
sudo -u postgres psql -c "CREATE USER monitor_user WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE monitor_db OWNER monitor_user;"

# Install Python requirements
pip3 install -r requirements.txt

echo "Setup Complete! Update .env with your DB credentials."
