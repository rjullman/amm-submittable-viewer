#!/bin/bash 

cd "$(dirname "$0")/.."

mkdir -p build
python create_webpage.py > build/index.html
python index.py
