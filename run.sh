#!/bin/bash

port=${PORT:-8040}

uvicorn src.main:app --host 0.0.0.0 --port $port --reload & npx tailwindcss -i ./static/styles/input.css -o ./static/styles/output.css --watch 