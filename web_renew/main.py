import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# env

env_file = Path(__file__).parent / ".env"
for line in env_file.read_text().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k] = v.strip()

# CONFIGURATION

USERNAME, PASSWORD = os.environ.get("PYANYWHERE_USERNAME", "elabskenya"), os.environ.get("PYANYWHERE_PASSWORD", "j:%Z%Vq435+Cw^g")
LOGIN_URL, TARGET_URL = "https://www.pythonanywhere.com/login/", f"https://www.pythonanywhere.com/user/{USERNAME}/webapps/#tab_id_{USERNAME}_pythonanywhere_com"

# Run for 30 days
RUN_DURATION = timedelta(days=30)

# VALIDATION
if not USERNAME:
    raise RuntimeError("PYANYWHERE_USERNAME environment variable is not set")

if not PASSWORD:
    raise RuntimeError("PYANYWHERE_PASSWORD environment variable is not set")

# LOGIN
def login(page):
    print("Opening PythonAnywhere login page...")

    page.goto(
        LOGIN_URL,
        wait_until="domcontentloaded",
        timeout=60_000
    )

    print("Login page loaded:", page.url)

    username_selectors = [
        'input[name="auth-username"]',
        'input[name="username"]',
        'input[type="text"]',
        '#id_auth-username',
    ]

    password_selectors = [
        'input[name="auth-password"]',
        'input[name="password"]',
        'input[type="password"]',
        '#id_auth-password',
    ]

    username_field = None
    password_field = None

    for selector in username_selectors:
        try:
            locator = page.locator(selector).first
            if locator.is_visible(timeout=3000):
                username_field = locator
                break
        except Exception:
            pass

    for selector in password_selectors:
        try:
            locator = page.locator(selector).first
            if locator.is_visible(timeout=3000):
                password_field = locator
                break
        except Exception:
            pass

    if not username_field:
        raise RuntimeError("Could not find username field")

    if not password_field:
        raise RuntimeError("Could not find password field")

    print("Filling credentials...")
    username_field.fill(USERNAME)
    password_field.fill(PASSWORD)

    login_selectors = [
        'input[type="submit"]',
        'button[type="submit"]',
        'button:has-text("Log in")',
        'button:has-text("Login")',
        'input[value="Log in"]',
    ]

    clicked = False
    for selector in login_selectors:
        try:
            button = page.locator(selector).first
            if button.is_visible(timeout=2000):
                button.click()
                clicked = True
                break
        except Exception:
            pass

    if not clicked:
        raise RuntimeError("Could not find login button")

    page.wait_for_load_state("domcontentloaded", timeout=60_000)
    page.wait_for_timeout(2000)

    print("Login submitted.")
    print("Current URL:", page.url)

    if "login" in page.url.lower():
        raise RuntimeError("Login appears to have failed (still on login page)")


# FIND AND CLICK THE RUN BUTTON

def click_run(page):
    print("Looking for 'Run until 1 month from today' button...")

    run_selectors = [
        # Most specific based on the exact HTML you provided
        'input.btn.btn-warning.webapp_extend[value="Run until 1 month from today"]',
        'input[type="submit"][value="Run until 1 month from today"]',
        'input[value="Run until 1 month from today"]',
        'button:has-text("Run until 1 month from today")',
        'a:has-text("Run until 1 month from today")',
    ]

    for selector in run_selectors:
        try:
            buttons = page.locator(selector)
            count = buttons.count()

            if count == 0:
                continue

            for i in range(count):
                button = buttons.nth(i)
                try:
                    if button.is_visible(timeout=4000):
                        print(f"Found button using selector: {selector}")
                        button.click()
                        print("Button clicked successfully!")
                        page.wait_for_timeout(5000)
                        return True
                except Exception:
                    continue
        except Exception:
            continue

    print("Run button was NOT found on the page.")
    return False


# CHECK AND RUN

def check_and_run(page):
    print()
    print("=" * 60)
    print("Checking PythonAnywhere Web Apps page...")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    try:
        page.goto(
            TARGET_URL,
            wait_until="domcontentloaded",
            timeout=60_000
        )

        # Wait for the page (and possible JavaScript) to fully load
        page.wait_for_timeout(4000)

        success = click_run(page)

        if success:
            print("Run button clicked successfully.")
        else:
            print("WARNING: Run button not found.")

    except PlaywrightTimeoutError:
        print("Page loading timed out.")
    except Exception as e:
        print(f"Error while checking: {e}")


# MAIN

def main():
    start_time = datetime.now()
    end_time = start_time + RUN_DURATION

    print()
    print("PythonAnywhere Playwright Runner")
    print("-----------------------------------")
    print("Started :", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    print("Ends    :", end_time.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Username     : {USERNAME}")
    print(f"Target page  : {TARGET_URL}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        page = context.new_page()

        try:
            # Login once
            login(page)
            try:
                check_and_run(page)
            except Exception as e:
                print(f"Check failed: {e}")

            print()
        finally:
            context.close()
            browser.close()
            print("Chromium closed.")
            print()


if __name__ == "__main__":
    main()
