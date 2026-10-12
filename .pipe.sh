
#!/usr/bin/env bash
set -euo pipefail

# Ensure we are inside a Git repository
git rev-parse --is-inside-work-tree >/dev/null

# Ensure the current working tree has no existing changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Error: Commit or stash existing changes first."
    exit 1
fi

# Remember the branch we started on
ORIGINAL_BRANCH=$(git branch --show-current)

git fetch origin

# Switch to the backup branch, creating it if necessary
if git show-ref --verify --quiet refs/heads/backup; then
    git switch backup
else
    if git ls-remote --exit-code --heads origin backup >/dev/null 2>&1; then
        git switch --track origin/backup
    else
        git switch -c backup
    fi
fi

# Synchronize with the remote backup branch
git pull --rebase origin backup

# Stage changes and commit only when necessary
git add -A

if ! git diff --cached --quiet; then
    git commit -m "Daily backup $(date +%F)"
else
    echo "No changes to commit."
fi

# Push the backup branch
if git push -u origin backup; then
    echo "Backup branch pushed successfully."
else
    echo "Failed to push the backup branch."
    exit 1
fi

# Return to the original branch
git switch "$ORIGINAL_BRANCH"

printf "\nBackup sync completed successfully!\n%s\n"