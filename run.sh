#!/usr/bin/env bash
# ==============================================================================
# MovieGraph RAG - Launch Script
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================================"
echo "🎬 Starting MovieGraph AI (Stitch Pastel Design System)"
echo "========================================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Run fast test suite verification
echo "Running test suite validation..."
python3 -m pytest tests/ -q

echo "Launching Streamlit application on http://localhost:8501..."
python3 -m streamlit run app.py --server.port 8501 --server.headless false
