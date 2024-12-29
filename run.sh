#!/bin/sh
uvicorn src:app --host 0.0.0.0 --port 8085 --reload &
npx tailwindcss -i ./static/styles/input.css -o ./static/styles/output.css --watch 