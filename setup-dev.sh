#!/bin/bash

# create virtualenv if not exists
if ! test -d .venv; then 
    python -m venv .venv
    
    source .venv/bin/activate
    
    pip install -r requirements.txt
else 
    source .venv/bin/activate
fi


# setup database
docker compose up -d
source .env

sqlx database setup --database-url $TEST_DATABASE_URL
sqlx database setup --database-url $DATABASE_URL

