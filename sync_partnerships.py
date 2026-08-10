#!/usr/bin/env python3
"""
Syncs the Wix CMS `partnerships-feed` collection into partnerships-data.json,
the file the live ticker and partnership feed both read from on GitHub Pages.

Requires two environment variables (set as GitHub Actions secrets):
  WIX_API_KEY  - API key generated at https://manage.wix.com/account/api-keys
  WIX_SITE_ID  - 2943c483-2e95-4e71-b9f0-fd32698a7934 (GcTechAllies site)

Exits with code 0 and leaves the file untouched if nothing changed, so the
GitHub Action step that follows can skip the commit cleanly.
"""

import json
import os
import sys
import urllib.request
import urllib.error

WIX_API_KEY = os.environ["WIX_API_KEY"]
WIX_SITE_ID = os.environ["WIX_SITE_ID"]
COLLECTION_ID = "partnerships-feed"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "partnerships-data.json")
QUERY_URL = "https://www.wixapis.com/wix-data/v2/items/query"

FIELDS = [
    "title", "companies", "summary", "category", "region",
    "macroRegion", "announcedDate", "sourceUrl", "sourceName", "euTech",
]


def wix_request(body):
    req = urllib.request.Request(
        QUERY_URL,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": WIX_API_KEY,
            "wix-site-id": WIX_SITE_ID,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Wix API error {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
        raise


def fetch_all_items():
    items = []
    cursor = None
    while True:
        body = {
            "dataCollectionId": COLLECTION_ID,
            "query": {
                "sort": [{"fieldName": "announcedDate", "order": "DESC"}],
                "cursorPaging": {"limit": 100, **({"cursor": cursor} if cursor else {})},
            },
        }
        data = wix_request(body)
        batch = data.get("dataItems", data.get("items", []))
        items.extend(batch)
        cursor = data.get("pagingMetadata", {}).get("cursors", {}).get("next")
        if not cursor or not batch:
            break
    return items


def main():
    raw_items = fetch_all_items()
    print(f"Fetched {len(raw_items)} items from Wix CMS collection '{COLLECTION_ID}'")

    deals = []
    for item in raw_items:
        d = item.get("data", {})
        deal = {field: d.get(field, "" if field != "euTech" else False) for field in FIELDS}
        deals.append(deal)

    # De-dupe by title (defensive — CMS should already be unique) and sort DESC
    seen = {}
    for d in deals:
        seen[d["title"]] = d
    deals = sorted(seen.values(), key=lambda d: d["announcedDate"], reverse=True)

    new_content = json.dumps(deals, indent=2, ensure_ascii=False)

    old_content = ""
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            old_content = f.read()

    if new_content.strip() == old_content.strip():
        print("No changes — partnerships-data.json is already up to date.")
        gh_output = os.environ.get("GITHUB_OUTPUT")
        if gh_output:
            with open(gh_output, "a") as f:
                f.write("changed=false\n")
        return

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(new_content + "\n")

    print(f"Updated partnerships-data.json — {len(deals)} total deals.")
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write("changed=true\n")


if __name__ == "__main__":
    main()
