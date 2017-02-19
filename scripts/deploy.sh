#!/bin/bash 

cd "$(dirname "$0")/.."

mkdir -p site
python create_webpage.py > site/index.html
