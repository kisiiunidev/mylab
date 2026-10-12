
import getpass
import subprocess
import sys
import time


def adb(*args, timeout=15):
    result = subprocess.run(
        ["adb", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or result.stdout.strip()
        )

    return result.stdout.strip()


def check_device():
    output = adb("devices")

    for line in output.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return parts[0]

    raise RuntimeError(
        "No authorized ADB device. Check: adb devices"
    )


def main():
    try:
        device = check_device()
        print(f"Connected to: {device}")

        pin = getpass.getpass(
            "Enter your phone PIN (input hidden): "
        )

        if not pin.isdigit() or not 4 <= len(pin) <= 16:
            print("Enter a numeric PIN of 4–16 digits.")
            sys.exit(1)

        confirm = getpass.getpass("Confirm PIN: ")
        if pin != confirm:
            print("PINs do not match.")
            sys.exit(1)

        # Wake the display.
        adb("shell", "input", "keyevent", "224")
        time.sleep(1)

        # Swipe upward to reveal the PIN screen.
        adb("shell", "input", "swipe",
            "500", "1400", "500", "400", "300")
        time.sleep(1)

        # Send the PIN to the lock-screen input.
        adb("shell", "input", "text", pin)
        time.sleep(0.5)

        # Submit the PIN using Enter.
        adb("shell", "input", "keyevent", "66")

        print("PIN submission attempted.")
        print("Check your phone to confirm whether it unlocked.")

    except (RuntimeError, subprocess.TimeoutExpired,
            FileNotFoundError) as error:
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
