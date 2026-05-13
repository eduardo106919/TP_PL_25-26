#!/bin/bash

# run_tests.sh — Test runner script for the PunchCard Fortran 77 compiler
#
# Usage:
#   ./run_tests.sh <file.f>          Run a specific test
#   ./run_tests.sh basic             Run all basic tests
#   ./run_tests.sh custom            Run all custom tests
#   ./run_tests.sh error             Run all error tests
#   ./run_tests.sh all               Run all tests

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
TEST_DIR="$SCRIPT_DIR/test"

# Auto-detect venv, otherwise use system python3
if [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python3"
else
    PYTHON="python3"
fi

# Counters
PASS=0
FAIL=0
TOTAL=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Helper functions ---

run_compiler() {
    # Run the compiler and capture stdout and stderr
    local file="$1"
    cd "$SRC_DIR" && $PYTHON -m punchcard.main "$file" 2>&1
}

run_success_test() {
    # Test that the compiler generates code WITHOUT errors
    local file="$1"
    local name
    name=$(basename "$file")
    TOTAL=$((TOTAL + 1))

    output=$(run_compiler "$file")

    if echo "$output" | grep -qi "error"; then
        echo -e "  ${RED}✗${NC} $name"
        echo "$output" | grep -i "error" | sed 's/^/      /'
        FAIL=$((FAIL + 1))
    else
        echo -e "  ${GREEN}✓${NC} $name"
        PASS=$((PASS + 1))
    fi
}

run_error_test() {
    # Test that the compiler DETECTS errors (should fail)
    local file="$1"
    local name
    name=$(basename "$file")
    TOTAL=$((TOTAL + 1))

    output=$(run_compiler "$file")

    if echo "$output" | grep -qi "error"; then
        # Extract the detected error type
        error_msg=$(echo "$output" | grep -i "error" | head -1 | sed 's/\[//' | sed 's/\].*//')
        echo -e "  ${GREEN}✓${NC} $name  ${YELLOW}(${error_msg})${NC}"
        PASS=$((PASS + 1))
    else
        echo -e "  ${RED}✗${NC} $name  (should have failed but compiled successfully)"
        FAIL=$((FAIL + 1))
    fi
}

run_category() {
    local category="$1"
    local dir="$TEST_DIR/$category"

    if [ ! -d "$dir" ]; then
        echo -e "${RED}Error: directory '$dir' does not exist${NC}"
        exit 1
    fi

    local count
    count=$(find "$dir" -name "*.f" | wc -l)

    if [ "$count" -eq 0 ]; then
        echo -e "${YELLOW}  (no tests)${NC}"
        return
    fi

    for file in "$dir"/*.f; do
        if [ "$category" = "error" ]; then
            run_error_test "$file"
        else
            run_success_test "$file"
        fi
    done
}

print_summary() {
    echo ""
    echo "==============================="
    echo -e "  Total: $TOTAL  ${GREEN}Pass: $PASS${NC}  ${RED}Fail: $FAIL${NC}"
    echo "==============================="

    if [ "$FAIL" -gt 0 ]; then
        exit 1
    fi
}

# --- Main ---

if [ $# -eq 0 ]; then
    echo "Usage: ./run_tests.sh <file.f | basic | custom | error | all>"
    exit 1
fi

ARG="$1"

# Specific test (file)
if [ -f "$ARG" ]; then
    echo -e "${BLUE}Test: $ARG${NC}"
    # Detect if it's an error test by folder
    if echo "$ARG" | grep -q "/error/"; then
        run_error_test "$ARG"
    else
        run_success_test "$ARG"
    fi
    print_summary
    exit $?
fi

# Category or all
case "$ARG" in
    basic)
        echo -e "${BLUE}=== Basic Tests (examples from the assignment) ===${NC}"
        run_category "basic"
        ;;
    custom)
        echo -e "${BLUE}=== Custom Tests (individual features) ===${NC}"
        run_category "custom"
        ;;
    error)
        echo -e "${BLUE}=== Error Tests (should fail) ===${NC}"
        run_category "error"
        ;;
    all)
        echo -e "${BLUE}=== Basic Tests (examples from the assignment) ===${NC}"
        run_category "basic"
        echo ""
        echo -e "${BLUE}=== Custom Tests (individual features) ===${NC}"
        run_category "custom"
        echo ""
        echo -e "${BLUE}=== Error Tests (should fail) ===${NC}"
        run_category "error"
        ;;
    *)
        echo -e "${RED}Error: unrecognized argument '$ARG'${NC}"
        echo "Usage: ./run_tests.sh <file.f | basic | custom | error | all>"
        exit 1
        ;;
esac

print_summary
