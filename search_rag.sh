#!/bin/bash
#
# PDF RAG Knowledge Base Search Helper (Portable Version)
#
# This script provides a convenient way to search the indexed PDF knowledge base
# from the command line or from GitHub Copilot Agent Skills.
#
# Usage:
#   ./search_rag.sh "your search query"
#   ./search_rag.sh "STM32F4 GPIO configuration"
#

set -e

# Get the script directory (skill directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if query is provided
if [ -z "$1" ]; then
    echo "Error: No search query provided"
    echo "Usage: $0 \"your search query\""
    exit 1
fi

QUERY="$1"
TOP_K="${2:-5}"  # Default to 5 results

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3."
    exit 1
fi

# Check if requests library is available
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Error: Python 'requests' library not installed."
    echo "Install it with: pip install requests PyPDF2"
    exit 1
fi

# Check if knowledge base has any documents
STATS=$(python3 "$SCRIPT_DIR/rag_search.py" --stats 2>&1)

if echo "$STATS" | grep -q "total_documents: 0"; then
    echo ""
    echo "⚠️  Warning: Knowledge base is empty!"
    echo "Please index some PDFs first:"
    echo "  python3 $SCRIPT_DIR/rag_search.py --index path/to/datasheet.pdf"
    echo ""
    exit 1
fi

echo ""
echo "🔍 Searching for: \"$QUERY\""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Perform the search using the portable script
python3 "$SCRIPT_DIR/rag_search.py" --search "$QUERY" --top-k "$TOP_K"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Search complete"
