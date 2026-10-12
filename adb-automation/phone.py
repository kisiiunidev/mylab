
import subprocess
import sys
import time


def adb(*args, timeout=30):
    """Execute an ADB command."""
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
    """Verify that a phone is connected and authorized."""
    output = adb("devices")

    devices = [
        line.split()[0]
        for line in output.splitlines()[1:]
        if len(line.split()) >= 2
        and line.split()[1] == "device"
    ]

    if not devices:
        print("No authorized ADB device found.")
        print("Check: adb devices")
        return False

    print(f"Connected device: {devices[0]}")
    return True


def device_info():
    print("Model:", adb("shell", "getprop", "ro.product.model"))
    print("Android:", adb("shell", "getprop",
                         "ro.build.version.release"))
    print("\nBattery:")
    print(adb("shell", "dumpsys", "battery"))


def take_screenshot():
    remote = "/sdcard/adb-automation-screen.png"
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, "screenshot.png")
    print("Screenshot saved as screenshot.png")


def wake_screen():
    adb("shell", "input", "keyevent", "224")
    print("Wake command sent.")


def lock_screen():
    adb("shell", "input", "keyevent", "223")
    print("Sleep command sent. Device behavior may vary.")


def launch_app():
    package = input("Enter Android package name: ").strip()

    if not package or any(c.isspace() for c in package):
        print("Invalid package name.")
        return

    adb("shell", "monkey", "-p", package,
        "-c", "android.intent.category.LAUNCHER", "1")
    print("Launch command sent.")


def list_apps():
    print(adb("shell", "pm", "list", "packages", "-3"))


def send_text():
    message = input("Text to type on phone: ")

    # Android input text treats spaces specially.
    safe_message = message.replace("%", "%25").replace(" ", "%s")

    adb("shell", "input", "text", safe_message)
    print("Text command sent to the focused field.")


def main():
    if not check_device():
        sys.exit(1)

    actions = {
        "1": ("Device information", device_info),
        "2": ("Take screenshot", take_screenshot),
        "3": ("Wake screen", wake_screen),
        "4": ("Lock/sleep screen", lock_screen),
        "5": ("List third-party apps", list_apps),
        "6": ("Launch an app", launch_app),
        "7": ("Type text into focused field", send_text),
    }

    while True:
        print("\n=== Android Automation ===")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("0. Exit")

        choice = input("\nChoose an action: ").strip()

        if choice == "0":
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid choice.")
            continue

        try:
            action[1]()
        except (RuntimeError, subprocess.TimeoutExpired) as error:
            print("ADB error:", error)


if __name__ == "__main__":
    main()
