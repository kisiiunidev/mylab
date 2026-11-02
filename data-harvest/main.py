
import ast
import json
import re
import sys
from pathlib import Path


class MaigretParser:
    SITE_PATTERN = re.compile(
        r"^\s*\[(\+|\?|-)\]\s+(.+?):\s+(https?://\S+)\s*$"
    )

    FIELD_PATTERN = re.compile(
        r"^\s*[│├└]\s*([├└]─|[│])?\s*([^:]+):\s*(.*)$"
    )

    TREE_VALUE_PATTERN = re.compile(
        r"^\s*[│├└]\s*[├└]─\s*(.*?)\s*$"
    )

    def __init__(self):
        self.accounts = []
        self.current_account = None
        self.current_field = None
        self.summary = {
            "accounts_found": 0,
            "identifiers": [],
            "countries": [],
            "interests": [],
            "search_text": None,
            "extended_info_count": 0,
        }
        self.search_info = {
            "username": None,
            "sites_database": None,
            "sites_checked": None,
            "search_interrupted": False,
        }

    @staticmethod
    def parse_value(value):
        """Convert strings into appropriate Python data types."""
        value = value.strip()

        if not value:
            return ""

        if value.lower() == "true":
            return True

        if value.lower() == "false":
            return False

        if value.lower() in ("none", "null"):
            return None

        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            pass

        return value

    def finish_field(self):
        self.current_field = None

    def finish_account(self):
        if self.current_account:
            self.accounts.append(self.current_account)
            self.current_account = None

        self.current_field = None

    def start_account(self, match):
        self.finish_account()

        symbol, platform, url = match.groups()

        statuses = {
            "+": "found",
            "?": "unknown",
            "-": "not_found",
        }

        self.current_account = {
            "platform": platform.strip(),
            "profile_url": url.strip(),
            "status": statuses[symbol],
            "data": {},
        }

    def parse_field(self, line):
        match = self.FIELD_PATTERN.match(line)

        if not match:
            return False

        prefix, key, value = match.groups()
        key = key.strip().lower()

        # Nested values, for example:
        # └─ https://example.com
        # ├─ https://example.org
        if not value and key.lower() in (
            "links",
            "social_links",
        ):
            self.current_account["data"][key] = []
            self.current_field = key
            return True

        parsed = self.parse_value(value)

        # Handle nested lists.
        if prefix and prefix.strip() in ("├─", "└─"):
            if self.current_field:
                container = self.current_account["data"].get(
                    self.current_field
                )

                if isinstance(container, list):
                    container.append(parsed)
                    return True

        self.current_account["data"][key] = parsed
        self.current_field = key

        return True

    def parse_summary(self, line):
        line = line.strip()

        if "Search by username" in line and "returned" in line:
            self.summary["search_text"] = line

            match = re.search(
                r"Search by username (.+?) returned (\d+) accounts",
                line,
            )

            if match:
                self.search_info["username"] = match.group(1)
                self.summary["accounts_found"] = int(match.group(2))

            return

        if "Extended info extracted from" in line:
            match = re.search(r"from (\d+) accounts", line)

            if match:
                self.summary["extended_info_count"] = int(
                    match.group(1)
                )

            return

        if "Found target's other IDs:" in line:
            values = line.split(":", 1)[1].strip()

            self.summary["identifiers"] = [
                item.strip()
                for item in values.split(",")
                if item.strip()
            ]

            return

        if line.startswith("Countries:"):
            self.summary["countries"] = [
                item.strip()
                for item in line.split(":", 1)[1].split(",")
                if item.strip()
            ]

            return

        if line.startswith("Interests (tags):"):
            self.summary["interests"] = [
                item.strip()
                for item in line.split(":", 1)[1].split(",")
                if item.strip()
            ]

    def parse_line(self, line):
        stripped = line.strip()

        if not stripped:
            # Preserve multiline bios.
            if (
                self.current_account
                and self.current_field == "bio"
            ):
                self.current_account["data"]["bio"] += "\n\n"
            return

        # Detect a new platform/account.
        match = self.SITE_PATTERN.match(line)

        if match:
            self.start_account(match)
            return

        if self.current_account:
            if self.parse_field(line):
                return

            # Handle nested list values.
            nested = self.TREE_VALUE_PATTERN.match(line)

            if nested and self.current_field:
                value = nested.group(1).strip()

                container = self.current_account["data"].get(
                    self.current_field
                )

                if isinstance(container, list):
                    container.append(self.parse_value(value))
                    return

            # Preserve multiline text, particularly YouTube bios.
            if self.current_field:
                previous = self.current_account["data"].get(
                    self.current_field
                )

                if isinstance(previous, str):
                    self.current_account["data"][
                        self.current_field
                    ] = previous + "\n" + stripped

                return

        # Parse general search information and summary.
        if "Using sites database:" in stripped:
            self.search_info["sites_database"] = (
                stripped.split(":", 1)[1].strip()
            )

        elif "Starting a search on top" in stripped:
            match = re.search(
                r"top (\d+) sites",
                stripped,
            )

            if match:
                self.search_info["sites_checked"] = int(
                    match.group(1)
                )

        elif "Search interrupted by user" in stripped:
            self.search_info["search_interrupted"] = True

        elif "Generating partial results" in stripped:
            self.search_info["search_interrupted"] = True

        self.parse_summary(stripped)

    def parse(self, text):
        for line in text.splitlines():
            self.parse_line(line)

        self.finish_account()

        return {
            "search": self.search_info,
            "summary": self.summary,
            "accounts": self.accounts,
            "statistics": {
                "total_parsed": len(self.accounts),
                "found": sum(
                    a["status"] == "found"
                    for a in self.accounts
                ),
                "unknown": sum(
                    a["status"] == "unknown"
                    for a in self.accounts
                ),
                "not_found": sum(
                    a["status"] == "not_found"
                    for a in self.accounts
                ),
            },
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python parser.py maigret_output.txt")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.is_file():
        print(f"File not found: {input_file}")
        sys.exit(1)

    try:
        text = input_file.read_text(encoding="utf-8")

        parser = MaigretParser()
        result = parser.parse(text)

        output_file = input_file.with_suffix(".json")

        output_file.write_text(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print(f"[+] Parsing completed")
        print(f"[+] Accounts parsed: {result['statistics']['total_parsed']}")
        print(f"[+] Found: {result['statistics']['found']}")
        print(f"[+] Unknown: {result['statistics']['unknown']}")
        print(f"[+] Not found: {result['statistics']['not_found']}")
        print(f"[+] JSON saved to: {output_file}")

    except (OSError, UnicodeError) as error:
        print(f"[-] Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
