# Ensure uv is on path.
source $HOME/.local/bin/env

# Make output directory.
mkdir public

# Build output.
uv run snapshot.py --output-path ./public/index.html
