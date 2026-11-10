#!/bin/bash
# Deploys THOR on tristanserver. Run by .github/workflows/deploy.yml on every push to main.
#
# Her data (Data/) is NOT in git and is never moved or stashed. Before touching anything the script
# snapshots it; afterwards it checks that every data file still exists and that the seizure, pain and
# Apple Watch logs only grew (old content unchanged). Any surprise stops the deploy and keeps the snapshot.
# Uncommitted code changes on the server also stop it (commit them first) instead of being stashed away.
#
# Test overrides: THOR_REPO, THOR_DOCKER_DIR, THOR_DEPLOY_LOG, THOR_SNAP_DIR, THOR_SKIP_DOCKER=1
set -euo pipefail
REPO="${THOR_REPO:-/home/tristan/API/API_Repoed/THOR_API}"
DOCKER_DIR="${THOR_DOCKER_DIR:-/home/tristan/Docker}"
LOG="${THOR_DEPLOY_LOG:-/home/tristan/API/API_Repoed/deploy.log}"
SNAP_ROOT="${THOR_SNAP_DIR:-/home/tristan/backups/thor/deploy}"
SKIP_DOCKER="${THOR_SKIP_DOCKER:-0}"
DATA="$REPO/Data"
APPEND_ONLY="seizures.csv pain.csv appleWatchData.csv"

say()  { printf '%s\n' "$*"; }
fail() { trap - ERR; say "DEPLOY STOPPED: $*"; printf '%s - Deployment FAILED: %s\n' "$(date -u)" "$*" >> "$LOG"; exit 1; }
trap 'fail "unexpected error on line $LINENO: $BASH_COMMAND"' ERR   # e.g. a failed container build

check_data() {   # $1 = snapshot dir, $2 = live data dir
  local snap=$1 live=$2 f
  (cd "$snap" && find . -type f) | while read -r f; do
    [ -f "$live/$f" ] || { say "missing after deploy: $f"; return 1; }
  done || return 1
  for f in $APPEND_ONLY; do
    [ -f "$snap/$f" ] || continue
    local old_size; old_size=$(stat -c %s "$snap/$f")
    [ "$(stat -c %s "$live/$f")" -ge "$old_size" ] || { say "$f got smaller"; return 1; }
    cmp -s -n "$old_size" "$snap/$f" "$live/$f" || { say "$f: existing entries changed"; return 1; }
  done
}
[ "${1:-}" = "--check-data" ] && { trap - ERR; check_data "$2" "$3" && exit 0 || exit 1; }

say "== THOR deploy $(date -u) =="
[ -d "$DATA" ] && [ -f "$DATA/seizures.csv" ] || fail "data folder not found at $DATA"

# 1. Snapshot her data first
SNAP="$SNAP_ROOT/$(date -u +%Y%m%d-%H%M%S)"
mkdir -p "$SNAP" && cp -a "$DATA/." "$SNAP/"
say "data snapshot: $SNAP ($(wc -l < "$SNAP/seizures.csv") seizure lines)"

cd "$REPO"
git fetch -q origin main

# 2. Refuse anything that could make git touch the data folder
[ -z "$(git ls-files -- Data)" ] || fail "Data/ is tracked by git on the server; untrack it first (git rm -r --cached Data)"
[ -z "$(git ls-tree -r --name-only origin/main -- Data)" ] || fail "Data/ is tracked in GitHub main; a deploy could overwrite her data"

# 3. Refuse to throw away server-side work
[ -z "$(git status --porcelain --untracked-files=no)" ] || fail "uncommitted code changes on the server: $(git status --porcelain --untracked-files=no | tr '\n' ' ')"
before=$(git rev-parse --short HEAD)
git merge -q --ff-only origin/main || fail "server has commits GitHub doesn't (push them first)"
say "code: $before -> $(git rev-parse --short HEAD)"

check_data "$SNAP" "$DATA" || fail "data check failed after code update; snapshot kept at $SNAP"

# 4. Rebuild and restart
if [ "$SKIP_DOCKER" != 1 ]; then
  cd "$DOCKER_DIR"
  docker compose up -d --build thor-api thor-webpage thor-scheduler
  ok=0
  for i in $(seq 1 40); do
    a=$(curl -s -o /dev/null -w '%{http_code}' -m 5 http://127.0.0.1:5000/prediction || true)
    w=$(curl -s -o /dev/null -w '%{http_code}' -m 5 http://127.0.0.1:5001/ || true)
    [ "$a" = 200 ] && [ "$w" = 200 ] && { ok=1; break; }
    sleep 5
  done
  [ $ok = 1 ] || fail "after restart: API answered $a, website answered $w"
  say "API and website answering"
fi

# 5. Final checks
[ "$(git -C "$REPO" rev-parse HEAD)" = "$(git -C "$REPO" rev-parse origin/main)" ] || fail "server code doesn't match GitHub main"
check_data "$SNAP" "$DATA" || fail "data check failed after restart; snapshot kept at $SNAP"
find "$SNAP_ROOT" -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf {} +   # deploy snapshots: keep 30 days (hourly backups keep the rest)
printf '%s - Deployment succeeded (%s)\n' "$(date -u)" "$(git -C "$REPO" rev-parse --short HEAD)" >> "$LOG"
say "== deploy OK =="
