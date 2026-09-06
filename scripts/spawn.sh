#!/usr/bin/env bash
# Spawn an AO session from a committed prompt file.
#   scripts/spawn.sh orch                 -> orchestrator from prompts/00-ORCHESTRATOR.md
#   scripts/spawn.sh w01                  -> worker from prompts/01-w01-world.md (any wNN)
#   scripts/spawn.sh list                 -> show sessions incl. terminated (never run `ao session cleanup`)
# Requires the AO desktop app running (`ao status`) and the project added (`ao project add .`).
set -euo pipefail
cd "$(dirname "$0")/.."
PROJECT=${AO_PROJECT:-unbilled}
AGENT=${AO_AGENT:-claude-code}
case "${1:-}" in
  orch)
    exec ao spawn --name unbilled-orch --project "$PROJECT" --harness "$AGENT" --kind orchestrator --mode chat --prompt 'Read prompts/00-ORCHESTRATOR.md in the project worktree and follow it as the complete orchestrator brief.' ;;
  w[0-9][0-9])
    f=$(ls prompts/*-"$1"-*.md | head -1)
    name=$(basename "$f" .md | sed 's/^[0-9]*-//')
    exec ao spawn --name "$name" --project "$PROJECT" --harness "$AGENT" --kind worker --mode chat --prompt "Read $f in the project worktree and follow it as the complete worker brief." ;;
  list)
    ao session ls --all --include-terminated; echo; ao orchestrator ls ;;
  *)
    echo "usage: $0 orch | wNN | list"; exit 1 ;;
esac
