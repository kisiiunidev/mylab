
#!/usr/bin/env bash
set -Eeuo pipefail

REMOTE="/sdcard/Download"
DEST="/mnt/in170482626_google_drive_1791476277/ADB_BACKUP/Other"

mkdir -p "$DEST"

mapfile -t DEVICES < <(
    adb devices | awk 'NR > 1 && $2 == "device" {print $1}'
)

if (( ${#DEVICES[@]} != 1 )); then
    echo "Error: Connect exactly one authorized ADB device."
    exit 1
fi

DEVICE="${DEVICES[0]}"

if ! adb -s "$DEVICE" shell "test -d '$REMOTE'"; then
    echo "Error: Screenshots directory not found."
    exit 1
fi

mapfile -t FILES < <(
    adb -s "$DEVICE" shell \
        "find '$REMOTE' -maxdepth 1 -type f"
)

if (( ${#FILES[@]} == 0 )); then
    echo "No screenshots found."
    exit 0
fi

for REMOTE_FILE in "${FILES[@]}"; do
    NAME="${REMOTE_FILE##*/}"
    LOCAL_FILE="$DEST/$NAME"

    # Existing local file: skip copying, delete phone copy.
    if [[ -f "$LOCAL_FILE" ]]; then
        echo "Already exists; skipping: $NAME"

        if adb -s "$DEVICE" shell rm -- "$REMOTE_FILE"; then
            echo "Deleted phone copy: $NAME"
        else
            echo "Could not delete phone copy: $NAME"
        fi

        continue
    fi

    # Copy to a temporary file first.
    TEMP_FILE=$(mktemp "$DEST/.transfer.XXXXXX")
    trap 'rm -f -- "$TEMP_FILE"' EXIT

    echo "Copying: $NAME"

    if ! adb -s "$DEVICE" pull "$REMOTE_FILE" "$TEMP_FILE"; then
        echo "Copy failed; keeping phone copy."
        rm -f -- "$TEMP_FILE"
        trap - EXIT
        continue
    fi

    LOCAL_HASH=$(sha256sum "$TEMP_FILE" | awk '{print $1}')
    REMOTE_HASH=$(
        adb -s "$DEVICE" shell \
            "sha256sum '$REMOTE_FILE'" |
            awk '{print $1}'
    )

    if [[ -z "$REMOTE_HASH" || "$LOCAL_HASH" != "$REMOTE_HASH" ]]; then
        echo "Verification failed; keeping phone copy."
        rm -f -- "$TEMP_FILE"
        trap - EXIT
        continue
    fi

    # Never overwrite an existing file.
    if [[ -e "$LOCAL_FILE" ]]; then
        echo "Destination appeared during transfer; skipping."
        rm -f -- "$TEMP_FILE"
        trap - EXIT
        continue
    fi

    mv -- "$TEMP_FILE" "$LOCAL_FILE"
    trap - EXIT

    echo "Copied and verified: $NAME"

    if adb -s "$DEVICE" shell rm -- "$REMOTE_FILE"; then
        echo "Deleted phone copy: $NAME"
    else
        echo "Warning: Phone deletion failed: $NAME"
    fi
done

echo "Screenshot sync finished."
