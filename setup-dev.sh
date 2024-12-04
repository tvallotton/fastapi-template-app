#!/bin/bash

# create virtualenv if not exists
if ! test -d .venv; then 
    python -m venv .venv
    
    source .venv/bin/activate
    
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
else 
    source .venv/bin/activate
fi


# setup database
docker compose up -d
source .env

sqlx database reset --database-url $TEST_DATABASE_URL -y
sqlx database reset --database-url $DATABASE_URL -y

