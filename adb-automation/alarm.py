
import subprocess
import sys
from datetime import datetime


def adb(*args):
    result = subprocess.run(
        ["adb", *args],
        capture_output=True,
        text=True,
        timeout=20,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or result.stdout.strip()
        )

    return result.stdout.strip()


def main():
    devices = adb("devices")

    connected = any(
        len(parts := line.split()) >= 2
        and parts[1] == "device"
        for line in devices.splitlines()[1:]
    )

    if not connected:
        print("No authorized phone. Run: adb devices")
        sys.exit(1)

    time_text = input("Alarm time (HH:MM, 24-hour format): ").strip()

    try:
        alarm_time = datetime.strptime(time_text, "%H:%M")
    except ValueError:
        print("Invalid time. Example: 06:30 or 18:45.")
        sys.exit(1)

    hour = alarm_time.hour
    minute = alarm_time.minute

    label = input("Alarm label (optional): ").strip()

    # Open the Android Clock app's alarm creation screen.
    command = [
        "shell", "am", "start",
        "-a", "android.intent.action.SET_ALARM",
        "--ei", "android.intent.extra.alarm.HOUR", str(hour),
        "--ei", "android.intent.extra.alarm.MINUTES", str(minute),
        "--ez", "android.intent.extra.alarm.SKIP_UI", "false",
    ]

    if label:
        command.extend([
            "--es", "android.intent.extra.alarm.MESSAGE", label
        ])

    adb(*command)

    print(f"Requested alarm: {hour:02d}:{minute:02d}")
    if label:
        print(f"Label: {label}")

    print("Check your phone and confirm/save the alarm if prompted.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired,
            FileNotFoundError) as error:
        print(f"Error: {error}")
        sys.exit(1)
