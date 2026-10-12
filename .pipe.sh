#!/usr/bin/env bash
set -Eeuo pipefail

# Ensure we are inside a Git repository
git rev-parse --is-inside-work-tree >/dev/null

# Require a clean working tree before switching branches
if ! git diff --quiet ||
   ! git diff --cached --quiet ||
   [[ -n "$(git ls-files --others --exclude-standard)" ]]; then
    echo "Error: Commit or stash existing changes first."
    exit 1
fi

ORIGINAL_BRANCH=$(git branch --show-current)

if [[ -z "$ORIGINAL_BRANCH" ]]; then
    echo "Error: Detached HEAD; cannot restore original branch."
    exit 1
fi

# Restore original branch when the script exits
restore_branch() {
    local status=$?
    trap - EXIT

    if [[ "$(git branch --show-current)" != "$ORIGINAL_BRANCH" ]]; then
        git switch "$ORIGINAL_BRANCH" || {
            echo "Warning: Could not restore branch $ORIGINAL_BRANCH."
        }
    fi

    exit "$status"
}
trap restore_branch EXIT

# Ensure origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "Error: Remote 'origin' is not configured."
    exit 1
fi

echo "Fetching from GitHub..."
git fetch origin

# Switch to or create backup branch
if git show-ref --verify --quiet refs/heads/backup; then
    git switch backup
elif git show-ref --verify --quiet refs/remotes/origin/backup; then
    git switch --track -c backup origin/backup
else
    git switch -c backup
fi

# Check whether the remote backup branch exists
if git show-ref --verify --quiet refs/remotes/origin/backup; then
    # Refuse to merge or rebase unrelated histories
    if ! git merge-base backup origin/backup >/dev/null 2>&1; then
        echo "Error: Local and remote backup histories differ."
        echo "Inspect with: git log --oneline --left-right backup...origin/backup"
        echo "Resolve the history mismatch before pushing."
        exit 1
    fi

    # Rebase only if the histories are related
    git rebase origin/backup
fi

# Stage changes
git add -A

# Commit only if changes exist
if ! git diff --cached --quiet; then
    git commit -m "Daily backup $(date +%F)"
else
    echo "No changes to commit."
fi

# Push changes
# Push to GitHub and wait for completion
echo "Pushing changes to GitHub..."

if git push -u origin backup; then
    echo "Push completed successfully!"
else
    echo "Error: Failed to push changes to GitHub."
    exit 1
fi

# Continue only after the push succeeds
git switch "$ORIGINAL_BRANCH"

printf '\nDaily backup completed successfully!\n'

echo "Daily backup completed successfully!"