# Install uv.
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure uv is on path.
source $HOME/.local/bin/env

# Install dependencies.
uv sync --all-extras --dev
