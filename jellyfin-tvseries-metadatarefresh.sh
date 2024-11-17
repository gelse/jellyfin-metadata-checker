#!/bin/bash

source .venv/bin/activate
export $(grep -v '^#'  .env | xargs)

python jellyfin-tvseries-metadatarefresh.py
deactivate
