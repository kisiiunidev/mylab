import argparse
import csv
from urllib.parse import quote_plus

def generate_dorks(domain):

    dorks = [
        f"site:{domain}",
        f"site:{domain} filetype:pdf",
        f"site:{domain} filetype:docx",
        f"site:{domain} inurl:login",
        f"site:{domain} inurl:help",
        f"site:{domain} intitle:documentation",
        f'site:{domain} "privacy policy"',
        f"site:{domain} (api OR developer OR documentation)",
        f"site:{domain} (swagger OR openapi)",
    ]

    return dorks


def save_results(dorks):

    with open("dorks.csv", "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(["Search Query", "Google Search URL"])

        for dork in dorks:

            url = "https://www.google.com/search?q=" + quote_plus(dork)

            writer.writerow([dork, url])


def main():

    parser = argparse.ArgumentParser(
        description="Google Dork Query Generator"
    )

    parser.add_argument(
        "domain",
        help="Authorised target domain"
    )

    args = parser.parse_args()

    dorks = generate_dorks(args.domain)

    save_results(dorks)

    print("\nGenerated Google Dorks:\n")

    for dork in dorks:
        print("[+] " + dork)

    print("\n[+] Saved results to dorks.csv")


if __name__ == "__main__":
    main()
