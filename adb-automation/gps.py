
import subprocess
import sys
import urllib.parse


def adb(*args):
    result = subprocess.run(
        ["adb", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or result.stdout.strip()
        )

    return result.stdout.strip()


def main():
    devices = adb("devices")
    connected = [
        line.split()[0]
        for line in devices.splitlines()[1:]
        if len(line.split()) >= 2
        and line.split()[1] == "device"
    ]

    if not connected:
        print("No authorized ADB device. Check: adb devices")
        sys.exit(1)

    print("Connected:", connected[0])
    print("\nChecking Android location settings...")

    mode = adb("shell", "settings", "get", "secure", "location_mode")
    print("Location mode:", mode)

    print("\nOpening Android location settings...")
    adb(
        "shell", "am", "start",
        "-a", "android.settings.LOCATION_SOURCE_SETTINGS"
    )

    print(
        "\nEnable Location if needed, then open Google Maps "
        "on the phone to verify the current position."
    )

    print("\nAvailable location diagnostics:")
    output = adb("shell", "dumpsys", "location")

    for line in output.splitlines():
        lower = line.lower()
        if any(term in lower for term in (
            "last location", "lastlocation",
            "gps provider", "location enabled"
        )):
            print(line.strip()[:300])


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired,
            FileNotFoundError) as error:
        print("Error:", error)
        sys.exit(1)
