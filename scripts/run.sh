#!/bin/bash

port=${PORT:-8040}

source .venv/bin/activate
python -m src & npx tailwindcss -i ./static/styles/input.css -o ./static/styles/output.css --watch 
