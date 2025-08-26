#!/usr/bin/env bash
set -euo pipefail

ROOT=$(dirname "$(realpath "$0")")/..
echo "Migration helper: moving monolith-template -> service-template"

if [ ! -d "$ROOT/monolith-template" ]; then
  echo "monolith-template not found; aborting"
  exit 1
fi

read -p "This will git-move files from monolith-template to service-template (must run in a Git branch). Continue? [y/N] " ans
if [ "${ans,,}" != "y" ]; then
  echo "Aborting"
  exit 0
fi

cd "$ROOT"
mkdir -p service-template

# Move files with git mv where possible
for f in $(ls monolith-template); do
  if [ -e "service-template/$f" ]; then
    echo "Skipping existing: $f"
  else
    git mv "monolith-template/$f" "service-template/$f" || cp -a "monolith-template/$f" "service-template/"
  fi
done

echo "Files moved. Please inspect, run tests, and commit the branch."
