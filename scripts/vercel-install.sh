# Install uv.
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure uv is on path.
source $HOME/.local/bin/env

# Install Python dependencies.
uv sync --all-extras --dev

# Install NPM dependencies.
npm install
