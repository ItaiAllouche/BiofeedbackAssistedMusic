#!/usr/bin/env bash
set -a
source .env
set +a

source env/bin/activate
python -m biofeedback.run_all