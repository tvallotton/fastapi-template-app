#!/bin/bash

port=${PORT:-8050}

exec uvicorn src.main:app --host 0.0.0.0 --port $port