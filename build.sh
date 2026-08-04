#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

BUILD_DIR="build"
ZIP_NAME="lambda.zip"
PYTHON_VERSION="3.12"
PIP="./.venv/bin/pip"

rm -rf "$BUILD_DIR" "$ZIP_NAME"
mkdir -p "$BUILD_DIR"

"$PIP" install \
    -r requirements.txt \
    --target "$BUILD_DIR" \
    --platform manylinux2014_x86_64 \
    --implementation cp \
    --python-version "$PYTHON_VERSION" \
    --only-binary=:all: \
    --upgrade

cp handler.py "$BUILD_DIR/"

find "$BUILD_DIR" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "$BUILD_DIR" -type d -name '*.dist-info' -prune -exec rm -rf {} +
find "$BUILD_DIR" -type d -name 'tests' -prune -exec rm -rf {} +
rm -rf "$BUILD_DIR/bin"

(cd "$BUILD_DIR" && zip -rq "../$ZIP_NAME" .)

rm -rf "$BUILD_DIR"

echo "Built $ZIP_NAME"
