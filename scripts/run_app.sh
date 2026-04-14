#!/bin/bash
echo "=================================="
echo "      Starting Streamlit App"
echo "=================================="

# Kích hoạt môi trường ảo (virtual environment)
source "$HOME/eventsim_project/venv/bin/activate"

# Khởi chạy giao diện Streamlit
streamlit run "$HOME/eventsim_project/app/app.py"
