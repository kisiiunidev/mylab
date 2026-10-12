#!/usr/bin/env bash
set -Eeuo pipefail

# Ensure we are inside a Git repository
git rev-parse --is-inside-work-tree >/dev/null

# Ensure the working tree and index are clean
if ! git diff --quiet ||
   ! git diff --cached --quiet ||
   [[ -n "$(git ls-files --others --exclude-standard)" ]]; then
    echo "Error: Commit or stash existing changes first."
    exit 1
fi

ORIGINAL_BRANCH=$(git branch --show-current)

if [[ -z "$ORIGINAL_BRANCH" ]]; then
    echo "Error: Detached HEAD; cannot restore the original branch."
    exit 1
fi

# Ensure origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "Error: Remote 'origin' is not configured."
    exit 1
fi

# Fetch remote references
git fetch origin

# Switch to backup, creating it if necessary
if git show-ref --verify --quiet refs/heads/backup; then
    git switch backup
elif git show-ref --verify --quiet refs/remotes/origin/backup; then
    git switch --track -c backup origin/backup
else
    git switch -c backup
fi

# Only rebase when histories are related and the remote
# has no commits that would reintroduce unwanted history.
if git show-ref --verify --quiet refs/remotes/origin/backup; then
    if git merge-base backup origin/backup >/dev/null 2>&1; then
        git rebase origin/backup
    else
        echo "Error: Local and remote backup histories are unrelated."
        echo "Resolve the history mismatch manually; refusing to pull."
        git switch "$ORIGINAL_BRANCH"
        exit 1
    fi
fi

# Stage and commit changes
git add -A

if ! git diff --cached --quiet; then
    git commit -m "Daily backup $(date +%F)"
else
    echo "No changes to commit."
fi

# Push without force
git push -u origin backup

# Return to the original branch
git switch "$ORIGINAL_BRANCH"

printf '\nDaily backup completed successfully!\n'