#!/usr/bin/env bash
set -Eeuo pipefail

BASE="/sdcard"
DEST="/mnt/in170482626_google_drive_1791476277/ADB_BACKUP"

# Android source directory -> Linux destination directory
declare -A FOLDERS=(
    ["$BASE/Pictures/Screenshots"]="Screenshots"
    ["$BASE/Documents"]="Documents"
    ["$BASE/Download"]="Other"
)

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

mkdir -p "$DEST"

for REMOTE in "${!FOLDERS[@]}"; do
    CATEGORY="${FOLDERS[$REMOTE]}"
    CATEGORY_DEST="$DEST/$CATEGORY"

    echo
    echo "===== $CATEGORY ====="

    if ! adb -s "$DEVICE" shell test -d "$REMOTE"; then
        echo "Source directory missing; skipping: $REMOTE"
        continue
    fi

    mkdir -p "$CATEGORY_DEST"

    # Process all files recursively, including files in subdirectories.
    while IFS= read -r REMOTE_FILE; do
        REMOTE_FILE="${REMOTE_FILE%$'\r'}"
        [[ -z "$REMOTE_FILE" ]] && continue

        # Preserve the relative directory structure.
        RELATIVE="${REMOTE_FILE#"$REMOTE"/}"
        LOCAL_FILE="$CATEGORY_DEST/$RELATIVE"
        LOCAL_DIR="$(dirname "$LOCAL_FILE")"

        mkdir -p "$LOCAL_DIR"

        # Existing destination file: skip copying and delete phone copy.
        if [[ -e "$LOCAL_FILE" ]]; then
            echo "Already exists; skipping: $CATEGORY/$RELATIVE"

            if adb -s "$DEVICE" shell rm -- "$REMOTE_FILE"; then
                echo "Deleted phone copy: $RELATIVE"
            else
                echo "WARNING: Could not delete phone copy: $RELATIVE"
            fi

            continue
        fi

        TEMP_FILE=$(mktemp "$LOCAL_DIR/.transfer.XXXXXX")

        echo "Copying: $CATEGORY/$RELATIVE"

        if ! adb -s "$DEVICE" pull \
            "$REMOTE_FILE" "$TEMP_FILE"; then
            echo "Copy failed; keeping phone file."
            rm -f -- "$TEMP_FILE"
            continue
        fi

        # Verify copied content against the phone file.
        LOCAL_HASH=$(sha256sum "$TEMP_FILE" | awk '{print $1}')

        if ! REMOTE_HASH=$(
            adb -s "$DEVICE" shell sha256sum "$REMOTE_FILE" |
                awk 'NR == 1 {print $1}'
        ); then
            echo "Could not verify; keeping phone file."
            rm -f -- "$TEMP_FILE"
            continue
        fi

        if [[ -z "$REMOTE_HASH" || "$LOCAL_HASH" != "$REMOTE_HASH" ]]; then
            echo "Verification failed; keeping phone file."
            rm -f -- "$TEMP_FILE"
            continue
        fi

        # Do not overwrite a file that appeared during transfer.
        if [[ -e "$LOCAL_FILE" ]]; then
            echo "Destination appeared; skipping."
            rm -f -- "$TEMP_FILE"
            continue
        fi

        mv -- "$TEMP_FILE" "$LOCAL_FILE"
        echo "Copied and verified: $CATEGORY/$RELATIVE"

        if adb -s "$DEVICE" shell rm -- "$REMOTE_FILE"; then
            echo "Deleted phone copy: $RELATIVE"
        else
            echo "WARNING: Phone deletion failed: $RELATIVE"
        fi

    done < <(
        adb -s "$DEVICE" shell find "$REMOTE" -type f
    )
done

echo
echo "===== BACKUP FINISHED ====="
echo "Destination: $DEST"
