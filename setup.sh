#!/bin/bash

# install poetry if it doesn't exist
if ! command -v poetry; then 
    if ! command -v pipx; then 
        brew install pipx
    fi
    pipx install poetry
fi

# install sqlx-cli if it doesn't exist.
if ! command -v sqlx; then
    brew install sqlx-cli
fi


# create a virtualenv if one does not exist
if ! test -d .venv; then 
    python -m venv .venv
    source .venv/bin/activate
    poetry install
else 
    source .venv/bin/activate
fi


# setup database
docker compose up -d
source .env

python -m app database reset