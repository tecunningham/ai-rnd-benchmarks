#!/bin/bash
# SessionStart hook for Claude Code on the web: install Quarto and the Python stack the chapters need.
# Idempotent; only runs in remote sessions. Requires the environment's network policy to allow
# github.com (Quarto release tarball) and pypi.org + files.pythonhosted.org (pip); with 'full' access both work.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

QUARTO_VERSION="1.7.32"
QUARTO_DIR="/opt/quarto/quarto-${QUARTO_VERSION}"

# --- Quarto (GitHub releases) -----------------------------------------------------------------
if [ ! -x "${QUARTO_DIR}/bin/quarto" ]; then
  echo "[session-start] installing Quarto ${QUARTO_VERSION}"
  mkdir -p /opt/quarto
  if curl -sSL --retry 3 --max-time 600 -o /tmp/quarto.tgz \
      "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"; then
    tar xzf /tmp/quarto.tgz -C /opt/quarto && rm -f /tmp/quarto.tgz
  else
    echo "[session-start] WARNING: could not download Quarto (github.com blocked?)"
  fi
fi
if [ -x "${QUARTO_DIR}/bin/quarto" ]; then
  echo "export PATH=\"${QUARTO_DIR}/bin:\$PATH\"" >> "${CLAUDE_ENV_FILE:-/dev/null}"
  export PATH="${QUARTO_DIR}/bin:$PATH"
  echo "[session-start] quarto $(quarto --version)"
fi

# --- Python packages (PyPI) --------------------------------------------------------------------
if python3 -c "import pandas, matplotlib, nbclient, ipykernel" 2>/dev/null; then
  echo "[session-start] python deps already present"
else
  echo "[session-start] pip install -r requirements.txt"
  # The agent proxy's NO_PROXY list sends pypi.org and files.pythonhosted.org direct, and that direct
  # route is denied even when the environment allows the hosts; force pip through the proxy.
  if ! env NO_PROXY="localhost,127.0.0.1,::1" no_proxy="localhost,127.0.0.1,::1" \
      python3 -m pip install -q --disable-pip-version-check -r "${CLAUDE_PROJECT_DIR:-.}/requirements.txt" 2>/tmp/pip.err; then
    echo "[session-start] WARNING: pip install failed; PyPI is probably not allowed by this environment's network policy."
    echo "[session-start] Allow pypi.org and files.pythonhosted.org in the environment settings. pip said:"
    tail -3 /tmp/pip.err
  fi
fi

python3 - <<'PY' || true
import importlib.util
mods = ["numpy", "pandas", "matplotlib", "nbclient", "ipykernel"]
missing = [m for m in mods if importlib.util.find_spec(m) is None]
print("[session-start] python deps missing:", missing or "none")
PY
exit 0
