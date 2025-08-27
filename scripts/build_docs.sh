#!/bin/bash

# Build FlowerCare documentation
# Usage: ./scripts/build_docs.sh [serve|build]

set -e

COMMAND=${1:-build}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🏗️  Building FlowerCare Documentation"
echo "========================================"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first."
    exit 1
fi

# Install documentation dependencies
echo "📦 Installing dependencies..."
cd "$PROJECT_DIR"
poetry install --with docs

# Check command
case $COMMAND in
    "serve")
        echo "🚀 Starting development server..."
        echo "📖 Documentation will be available at http://localhost:8000"
        echo "   Press Ctrl+C to stop"
        poetry run mkdocs serve
        ;;
    "build")
        echo "🔨 Building documentation..."
        poetry run mkdocs build --clean
        echo "✅ Documentation built successfully!"
        echo "📁 Output directory: $(pwd)/site"
        ;;
    "clean")
        echo "🧹 Cleaning build artifacts..."
        rm -rf site/
        echo "✅ Clean complete!"
        ;;
    "help")
        echo "Usage: $0 [serve|build|clean|help]"
        echo ""
        echo "Commands:"
        echo "  serve  - Start development server with live reload"
        echo "  build  - Build static documentation site"  
        echo "  clean  - Remove build artifacts"
        echo "  help   - Show this help message"
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac