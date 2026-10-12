
#!/usr/bin/env bash
set -Eeuo pipefail

BASE="/sdcard"
DEST="/mnt/in170482626_google_drive_1791476277/ADB_BACKUP"

# Android source directory -> Linux destination category
declare -A FOLDERS=(
    ["$BASE/Pictures/Screenshots"]="Screenshots"
    ["$BASE/Documents"]="Documents"
    ["$BASE/Download"]="Other"
)

# Safely quote a path for the Android shell.
# This handles spaces and common shell-special characters.
remote_quote() {
    printf '%q' "$1"
}

# Calculate SHA-256 on the Android device.
remote_hash() {
    local path quoted_path
    path="$1"
    quoted_path=$(remote_quote "$path")

    adb -s "$DEVICE" shell "sha256sum $quoted_path" |
        awk 'NR == 1 {print $1}'
}

# Delete a remote file.
remote_delete() {
    local path quoted_path
    path="$1"
    quoted_path=$(remote_quote "$path")

    adb -s "$DEVICE" shell "rm -- $quoted_path"
}

# Require exactly one authorized ADB device.
mapfile -t DEVICES < <(
    adb devices | awk 'NR > 1 && $2 == "device" {print $1}'
)

if (( ${#DEVICES[@]} != 1 )); then
    echo "Error: Connect exactly one authorized ADB device."
    exit 1
fi

DEVICE="${DEVICES[0]}"

echo "Device: $DEVICE"
echo "Backup destination: $DEST"

# Create the main backup directory if missing.
if ! mkdir -p "$DEST"; then
    echo "Error: Cannot create backup destination."
    exit 1
fi

# Process each source directory.
for REMOTE in "${!FOLDERS[@]}"; do
    CATEGORY="${FOLDERS[$REMOTE]}"
    CATEGORY_DEST="$DEST/$CATEGORY"

    echo
    echo "===== $CATEGORY ====="

    # Skip missing source directories.
    if ! adb -s "$DEVICE" shell "test -d '$REMOTE'"; then
        echo "Source directory missing; skipping: $REMOTE"
        continue
    fi

    # Create category destination if missing.
    if ! mkdir -p "$CATEGORY_DEST"; then
        echo "Cannot create destination: $CATEGORY_DEST"
        continue
    fi

    # Find files recursively.
    while IFS= read -r REMOTE_FILE; do
        REMOTE_FILE="${REMOTE_FILE%$'\r'}"
        [[ -z "$REMOTE_FILE" ]] && continue

        # Preserve the relative directory structure.
        RELATIVE="${REMOTE_FILE#"$REMOTE"/}"
        LOCAL_FILE="$CATEGORY_DEST/$RELATIVE"
        LOCAL_DIR="$(dirname "$LOCAL_FILE")"

        if ! mkdir -p "$LOCAL_DIR"; then
            echo "Cannot create directory: $LOCAL_DIR"
            continue
        fi

        # If a local file exists, delete the phone copy
        # ONLY if its contents are identical.
        if [[ -e "$LOCAL_FILE" ]]; then
            if [[ ! -f "$LOCAL_FILE" ]]; then
                echo "Destination is not a regular file; keeping phone copy."
                continue
            fi

            echo "Already exists; checking: $CATEGORY/$RELATIVE"

            LOCAL_HASH=$(sha256sum "$LOCAL_FILE" | awk '{print $1}')

            if ! REMOTE_HASH=$(remote_hash "$REMOTE_FILE"); then
                echo "Could not verify; keeping phone copy."
                continue
            fi

            if [[ -z "$REMOTE_HASH" ]]; then
                echo "Remote hash unavailable; keeping phone copy."
                continue
            fi

            if [[ "$LOCAL_HASH" == "$REMOTE_HASH" ]]; then
                echo "Identical verified copy exists."

                if remote_delete "$REMOTE_FILE"; then
                    echo "Deleted phone copy: $RELATIVE"
                else
                    echo "WARNING: Could not delete phone copy."
                fi
            else
                echo "Files differ; keeping phone copy."
            fi

            continue
        fi

        # Create a temporary file in the destination directory.
        TEMP_FILE=$(mktemp "$LOCAL_DIR/.transfer.XXXXXX") || {
            echo "Cannot create temporary file."
            continue
        }

        echo "Copying: $CATEGORY/$RELATIVE"

        # Pull the file from Android.
        if ! adb -s "$DEVICE" pull \
            "$REMOTE_FILE" "$TEMP_FILE"; then
            echo "Copy failed; keeping phone file."
            rm -f -- "$TEMP_FILE"
            continue
        fi

        # Hash the downloaded copy.
        LOCAL_HASH=$(sha256sum "$TEMP_FILE" | awk '{print $1}')

        # Hash the original on Android.
        if ! REMOTE_HASH=$(remote_hash "$REMOTE_FILE"); then
            echo "Could not verify; keeping phone file."
            rm -f -- "$TEMP_FILE"
            continue
        fi

        # Do not proceed if hashes differ or are unavailable.
        if [[ -z "$REMOTE_HASH" || "$LOCAL_HASH" != "$REMOTE_HASH" ]]; then
            echo "Verification failed; keeping phone file."
            rm -f -- "$TEMP_FILE"
            continue
        fi

        # Recheck the destination before saving.
        if [[ -e "$LOCAL_FILE" ]]; then
            echo "Destination appeared during transfer; skipping."
            rm -f -- "$TEMP_FILE"
            continue
        fi

        # Do not overwrite a destination file.
        mv -n -- "$TEMP_FILE" "$LOCAL_FILE"

        # If mv -n refused to move the file, keep the phone copy.
        if [[ -e "$TEMP_FILE" ]]; then
            echo "Destination conflict; keeping phone file."
            rm -f -- "$TEMP_FILE"
            continue
        fi

        echo "Copied and verified: $CATEGORY/$RELATIVE"

        # Delete the phone file only after verified local storage.
        if remote_delete "$REMOTE_FILE"; then
            echo "Deleted phone copy: $RELATIVE"
        else
            echo "WARNING: Phone deletion failed: $RELATIVE"
            echo "Verified Linux copy remains safe."
        fi

    done < <(
        adb -s "$DEVICE" shell "find '$REMOTE' -type f"
    )
done

echo
echo "===== BACKUP FINISHED ====="
echo "Destination: $DEST"
