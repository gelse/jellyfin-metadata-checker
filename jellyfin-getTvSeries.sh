#!/bin/bash

source .venv/bin/activate
export $(grep -v '^#'  .env | xargs)

python jellyfin-getTvSeries.py
deactivate
