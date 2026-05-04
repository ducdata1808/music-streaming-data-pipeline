#!/bin/bash
# Note: To correctly activate the virtual environment in your current shell session,
# you MUST run this script via the 'source' command (or '.').
# Example: source ~/eventsim_project/setup/activate_venv.sh

VENV_PATH="$HOME/eventsim_project/venv/bin/activate"

if [ -f "$VENV_PATH" ]; then
    echo "Activating virtual environment..."
    source "$VENV_PATH"
else
    echo "Virtual environment not found at $VENV_PATH."
    echo "Please create it first using: python3 -m venv ~/eventsim_project/venv"
fi
