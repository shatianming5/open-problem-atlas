#!/usr/bin/env bash
# Create GitHub labels from .github/labels.yml
# Usage: REPO=owner/repo ./scripts/setup_labels.sh

set -euo pipefail

REPO="${REPO:?Set REPO=owner/repo}"

echo "Setting up labels for $REPO..."

# Type labels
gh label create "type:problem"    -R "$REPO" -d "New verified problem submission" -c "0e8a16" --force
gh label create "type:lead"       -R "$REPO" -d "Radar lead / candidate problem" -c "c5def5" --force
gh label create "type:attempt"    -R "$REPO" -d "AI or human attempt record" -c "d4c5f9" --force
gh label create "type:source"     -R "$REPO" -d "New source for ingestion" -c "bfdadc" --force

# Domain labels
gh label create "domain:math"     -R "$REPO" -d "Mathematics" -c "1d76db" --force
gh label create "domain:tcs"      -R "$REPO" -d "Theoretical Computer Science" -c "5319e7" --force
gh label create "domain:physics"  -R "$REPO" -d "Mathematical Physics" -c "006b75" --force

# Workflow labels
gh label create "needs-review"        -R "$REPO" -d "Needs human review" -c "fbca04" --force
gh label create "good-first-entry"    -R "$REPO" -d "Good for new contributors" -c "7057ff" --force
gh label create "status-change"       -R "$REPO" -d "Reports a status change" -c "e11d48" --force
gh label create "formalization-wanted" -R "$REPO" -d "Seeking formalization in Lean/Coq/Isabelle" -c "f9d0c4" --force
gh label create "solver-ready"        -R "$REPO" -d "Amenable to computational approaches" -c "c2e0c6" --force

# Priority labels
gh label create "priority:high"   -R "$REPO" -d "High priority" -c "b60205" --force
gh label create "priority:low"    -R "$REPO" -d "Low priority" -c "e4e669" --force

echo "Done! Labels created for $REPO"
