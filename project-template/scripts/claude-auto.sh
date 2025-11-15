#!/bin/bash
# claude-auto.sh - Auto-compression CLI wrapper for Claude Code
# Version: 1.0
# Author: Claude Code + zycaskevin
#
# Purpose: Automatically compress context and generate handoff.json when token threshold is reached
#
# Usage:
#   ./claude-auto.sh --from research --to product
#   ./claude-auto.sh --from tdd.red --to tdd.green --threshold 80

set -e  # Exit on error

# ============================================================
# Configuration
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default settings
TOKEN_THRESHOLD=70  # 70% of context window
CONTEXT_WINDOW=200000
HANDOFF_OUTPUT="handoff.json"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# Helper Functions
# ============================================================
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Claude Auto-Compression & Handoff CLI${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Auto-compress context and generate handoff.json when token threshold is reached.

OPTIONS:
    --from AGENT        Source agent ID (required)
    --to AGENT          Target agent ID (required)
    --threshold PCT     Token threshold percentage (default: 70)
    --output FILE       Output handoff file (default: handoff.json)
    --force             Force compression even if threshold not reached
    --help              Show this help message

EXAMPLES:
    # Basic usage
    $0 --from research --to product

    # Custom threshold (80%)
    $0 --from tdd.red --to tdd.green --threshold 80

    # Force compression
    $0 --from architect --to developer --force

AGENT IDS:
    research, marketing, product, architect, developer, qa,
    tdd.red, tdd.green, tdd.refactor, delivery

For more information, see: project-template/README.md
EOF
}

# ============================================================
# Parse Arguments
# ============================================================
FROM_AGENT=""
TO_AGENT=""
FORCE_COMPRESSION=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --from)
            FROM_AGENT="$2"
            shift 2
            ;;
        --to)
            TO_AGENT="$2"
            shift 2
            ;;
        --threshold)
            TOKEN_THRESHOLD="$2"
            shift 2
            ;;
        --output)
            HANDOFF_OUTPUT="$2"
            shift 2
            ;;
        --force)
            FORCE_COMPRESSION=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$FROM_AGENT" ]] || [[ -z "$TO_AGENT" ]]; then
    print_error "Both --from and --to are required"
    usage
    exit 1
fi

# ============================================================
# Main Logic
# ============================================================
print_header

print_info "Configuration:"
echo "  From Agent: $FROM_AGENT"
echo "  To Agent: $TO_AGENT"
echo "  Token Threshold: ${TOKEN_THRESHOLD}%"
echo "  Output File: $HANDOFF_OUTPUT"
echo ""

# Step 1: Check if Python is available
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        print_error "Python is not installed. Please install Python 3.7+ to use this tool."
        exit 1
    fi
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

print_success "Python found: $PYTHON_CMD"

# Step 2: Estimate current token usage (using compress_context.py)
print_info "Estimating current token usage..."

CURRENT_TOKENS=$($PYTHON_CMD "$SCRIPT_DIR/compress_context.py" --estimate-only 2>/dev/null || echo "0")

if [[ "$CURRENT_TOKENS" == "0" ]]; then
    print_warning "Could not estimate token usage. Proceeding with compression..."
    SHOULD_COMPRESS=true
else
    THRESHOLD_TOKENS=$((CONTEXT_WINDOW * TOKEN_THRESHOLD / 100))
    USAGE_PCT=$((CURRENT_TOKENS * 100 / CONTEXT_WINDOW))

    print_info "Token usage: $CURRENT_TOKENS / $CONTEXT_WINDOW ($USAGE_PCT%)"
    print_info "Threshold: $THRESHOLD_TOKENS tokens (${TOKEN_THRESHOLD}%)"

    if [[ $CURRENT_TOKENS -gt $THRESHOLD_TOKENS ]] || [[ "$FORCE_COMPRESSION" == true ]]; then
        print_warning "Token threshold reached! Starting auto-compression..."
        SHOULD_COMPRESS=true
    else
        print_success "Token usage within limits. No compression needed."
        SHOULD_COMPRESS=false
    fi
fi

# Step 3: Generate handoff.json
if [[ "$SHOULD_COMPRESS" == true ]]; then
    print_info "Generating handoff template..."

    $PYTHON_CMD "$SCRIPT_DIR/generate_handoff_template.py" \
        --from "$FROM_AGENT" \
        --to "$TO_AGENT" \
        --output "$HANDOFF_OUTPUT"

    if [[ $? -eq 0 ]]; then
        print_success "Handoff template generated: $HANDOFF_OUTPUT"
    else
        print_error "Failed to generate handoff template"
        exit 1
    fi

    # Step 4: Auto-fix and validate
    print_info "Validating and auto-fixing handoff..."

    $PYTHON_CMD "$SCRIPT_DIR/validate_handoff.py" \
        "$HANDOFF_OUTPUT" \
        --auto-fix

    if [[ $? -eq 0 ]]; then
        print_success "Handoff validation complete"
    else
        print_error "Handoff validation failed"
        exit 1
    fi

    # Step 5: Compress context (optional - using compress_context.py)
    print_info "Compressing context..."

    $PYTHON_CMD "$SCRIPT_DIR/compress_context.py" \
        --handoff "$HANDOFF_OUTPUT" \
        --from-agent "$FROM_AGENT" \
        --to-agent "$TO_AGENT"

    if [[ $? -eq 0 ]]; then
        print_success "Context compression complete"
    else
        print_warning "Context compression had warnings (non-critical)"
    fi

    # Summary
    echo ""
    print_header
    print_success "Auto-compression workflow complete!"
    echo ""
    echo "📝 Next steps:"
    echo "  1. Review the generated handoff: $HANDOFF_OUTPUT"
    echo "  2. Replace all 'TODO' placeholders with actual content"
    echo "  3. Use the handoff file to brief the next agent"
    echo ""
    echo "🚀 Launch next agent:"
    echo "  claude code --context $HANDOFF_OUTPUT"
    echo ""
else
    print_info "Skipping compression (threshold not reached)"
    echo ""
    echo "💡 To force compression, use: $0 --from $FROM_AGENT --to $TO_AGENT --force"
fi
