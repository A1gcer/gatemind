#!/bin/bash
set -e
ROOT="$(pwd)"
HOOK_DIR="$ROOT/.git/hooks"
mkdir -p "$HOOK_DIR"

cat > "$HOOK_DIR/pre-commit" << 'HOOK'
#!/bin/bash
set -e

# GateMind CLI 优先路径
GATEMIND_BIN="$HOME/.local/bin/gatemind"
if [ ! -x "$GATEMIND_BIN" ]; then
    GATEMIND_BIN="$(command -v gatemind 2>/dev/null)"
fi
if [ -z "$GATEMIND_BIN" ] || [ ! -x "$GATEMIND_BIN" ]; then
    echo "⚠️  GateMind CLI not found (gatemind). Install: pip install -e ."
    echo "    Skipping GateMind pre-commit gate."
    exit 0
fi

echo "🔍 GateMind pre-commit gate running..."
"$GATEMIND_BIN" run --phase pre_commit --from-git --enforce-exit 2>/dev/null || {
    echo "⛔ GateMind blocked this commit. Run 'gatemind run --phase pre_commit --from-git' to see details."
    exit 1
}
echo "✅ GateMind pre-commit passed"
HOOK
chmod +x "$HOOK_DIR/pre-commit"

# Optional: pre-push for public repos
cat > "$HOOK_DIR/pre-push" << 'HOOK2'
#!/bin/bash
set -e
REMOTE_URL="$2"

# If it's a private repo, skip public-specific checks
if echo "$REMOTE_URL" | grep -q "gatemind-private-ops"; then
    exit 0
fi

GATEMIND_BIN="$HOME/.local/bin/gatemind"
if [ ! -x "$GATEMIND_BIN" ]; then
    GATEMIND_BIN="$(command -v gatemind 2>/dev/null)"
fi
if [ -z "$GATEMIND_BIN" ] || [ ! -x "$GATEMIND_BIN" ]; then
    exit 0
fi

echo "🔍 GateMind pre-push gate (public repo check)..."
"$GATEMIND_BIN" run --phase pre_commit --from-git --enforce-exit 2>/dev/null || {
    echo "⛔ GateMind blocked this push. Check your staged files."
    exit 1
}
echo "✅ GateMind pre-push passed"
HOOK2
chmod +x "$HOOK_DIR/pre-push"

echo "✅ GateMind hooks installed: pre-commit + pre-push"
