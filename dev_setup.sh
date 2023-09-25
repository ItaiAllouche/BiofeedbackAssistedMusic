#!/bin/bash
set -euo pipefail

handle_env() {
    if [[ ! -d './env/' ]]; then
        echo "Creating python virtual environment"
        python -m venv env
    fi
    source ./env/bin/activate
    pip install -r requirements.txt
}

run_editable_install() {
    echo "Installing an editable install..."
    pip install --editable .
}

handle_env
run_editable_install

echo "Activate environment:"
echo "  'source ./env/bin/activate'"
