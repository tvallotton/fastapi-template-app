#!/bin/bash

# create virtualenv if not exists
if test -d .venv; then 
    python -m venv .venv
    
    source .venv/bin/activate
    
    pip install -r requirements.txt
fi

source .venv/bin/activate