
import re
import subprocess
import sys


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
    # Check that an authorized phone is connected.
    devices = adb("devices")

    connected = any(
        len(parts := line.split()) >= 2
        and parts[1] == "device"
        for line in devices.splitlines()[1:]
    )

    if not connected:
        print("No authorized phone. Check: adb devices")
        sys.exit(1)

    number = input("Enter the phone number to call: ").strip()

    # Permit international numbers, spaces, and common separators.
    if not re.fullmatch(r"\+?[0-9][0-9 ()-]{3,20}", number):
        print("Invalid phone number format.")
        sys.exit(1)

    number = re.sub(r"[ ()-]", "", number)

    print(f"\nNumber: {number}")

    # Open the phone dialer with the number filled in.
    uri = "tel:" + number
    adb(
        "shell", "am", "start",
        "-a", "android.intent.action.DIAL",
        "-d", uri,
    )


    # Initiate the call.
    adb(
            "shell", "am", "start",
            "-a", "android.intent.action.CALL",
            "-d", uri,
        )
    print("Call request sent.")
    

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired,
            FileNotFoundError) as error:
        print(f"Error: {error}")
        sys.exit(1)
