#!/bin/bash
set -e
ROOT="$(pwd)"
HOOK_DIR="$ROOT/.git/hooks"
mkdir -p "$HOOK_DIR"

cat > "$HOOK_DIR/pre-commit" << 'HOOK'
#!/bin/bash
bash gates/git_preflight.sh
HOOK

chmod +x "$HOOK_DIR/pre-commit"
echo "✅ GateMind pre-commit hook installed"
