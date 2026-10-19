#!/usr/bin/env python3
"""
Syncs the Wix CMS `partnerships-feed` collection into:
  1. partnerships-data.json   - read by the live feed and the ticker
  2. share/<slug>.html        - one small landing page per deal, with Open Graph / Twitter
                                tags so a shared link unfurls with the deal's card image

Requires two environment variables (GitHub Actions secrets):
  WIX_API_KEY  - API key generated at https://manage.wix.com/account/api-keys
  WIX_SITE_ID  - 2943c483-2e95-4e71-b9f0-fd32698a7934 (GcTechAllies site)

Notes
  * Wix rejects `sort` together with a cursor, so pages are fetched without sort and sorted here.
  * Writes GITHUB_OUTPUT changed=true/false so the workflow can skip an empty commit.
"""

import html
import json
import os
import re
import sys
import unicodedata
import urllib.request
import urllib.error

WIX_API_KEY = os.environ["WIX_API_KEY"]
WIX_SITE_ID = os.environ["WIX_SITE_ID"]
COLLECTION_ID = "partnerships-feed"
OUTPUT_DIR = os.environ.get("OUTPUT_DIR") or os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "partnerships-data.json")
SHARE_DIR = os.path.join(OUTPUT_DIR, "share")
QUERY_URL = "https://www.wixapis.com/wix-data/v2/items/query"
PAGES_BASE = "https://lukedandy-82.github.io/Partnership-cards/"
SITE_URL = "https://www.gctechallies.com/partnerships"

FIELDS = [
    "title", "companies", "summary", "category", "region",
    "macroRegion", "announcedDate", "sourceUrl", "sourceName", "euTech",
    "cardImageUrl",
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
    items, cursor = [], None
    while True:
        paging = {"limit": 100}
        if cursor:
            paging["cursor"] = cursor
        data = wix_request({"dataCollectionId": COLLECTION_ID, "query": {"cursorPaging": paging}})
        batch = data.get("dataItems", data.get("items", []))
        items.extend(batch)
        cursor = data.get("pagingMetadata", {}).get("cursors", {}).get("next")
        if not cursor or not batch:
            break
    return items


def slugify(text):
    # Must match slugify() in partnership-feed.html
    t = unicodedata.normalize("NFD", text or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def share_page(d):
    title = html.escape(d["title"], quote=True)
    desc = d.get("summary", "")
    if len(desc) > 200:
        desc = re.sub(r"\s+\S*$", "", desc[:197]) + "..."
    desc = html.escape(desc, quote=True)
    url = html.escape(d["shareUrl"], quote=True)
    img = d.get("cardImageUrl") or ""
    img = html.escape(img, quote=True) if img.startswith("https://") else ""
    src = d.get("sourceUrl") or ""
    src_html = (f'<a class="b2" href="{html.escape(src, quote=True)}" target="_blank" rel="noopener">Read the source &#8599;</a>'
                if src.startswith(("https://", "http://")) else "")
    og_img = (f'<meta property="og:image" content="{img}"><meta name="twitter:image" content="{img}">' if img else "")
    card = f'<img class="card" src="{img}" alt="{title}">' if img else f"<h1>{title}</h1>"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | GcTechAllies</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:site_name" content="GcTechAllies Partnership Digest">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}">
{og_img}
<style>body{{margin:0;background:#050d28;color:#f2f8ff;font-family:Helvetica,Arial,sans-serif;text-align:center}}
.w{{max-width:760px;margin:0 auto;padding:24px 16px 40px}}.card{{width:100%;height:auto;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.5)}}
p{{color:#b8d4ee;line-height:1.6}}.b{{display:inline-block;margin:6px;padding:11px 20px;border-radius:8px;background:#27a9bb;color:#050d28;font-weight:700;text-decoration:none}}
.b2{{display:inline-block;margin:6px;padding:10px 18px;border-radius:8px;border:1px solid #27a9bb;color:#5bcfde;text-decoration:none}}</style></head>
<body><div class="w">{card}<p>{desc}</p>
<a class="b" href="{SITE_URL}">See all partnerships &rarr;</a>{src_html}</div></body></html>
"""


def main():
    raw_items = fetch_all_items()
    print(f"Fetched {len(raw_items)} items from Wix CMS collection '{COLLECTION_ID}'")

    deals = []
    for item in raw_items:
        d = item.get("data", {})
        deal = {field: d.get(field, "" if field != "euTech" else False) for field in FIELDS}
        deals.append(deal)

    # De-dupe by title (defensive) and sort newest first
    seen = {}
    for d in deals:
        seen[d["title"]] = d
    deals = sorted(seen.values(), key=lambda d: (d["announcedDate"], d["title"]), reverse=True)

    # Share slug + URL (slug must match slugOf() in partnership-feed.html)
    used = set()
    for d in deals:
        slug = slugify(f'{d.get("companies") or d["title"]} {d.get("announcedDate", "")}')
        base, n = slug, 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
        d["slug"] = slug
        d["shareUrl"] = f"{PAGES_BASE}share/{slug}.html"

    new_content = json.dumps(deals, indent=2, ensure_ascii=False)

    old_content = ""
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            old_content = f.read()

    gh_output = os.environ.get("GITHUB_OUTPUT")
    changed = new_content.strip() != old_content.strip()

    os.makedirs(SHARE_DIR, exist_ok=True)
    for d in deals:
        path = os.path.join(SHARE_DIR, d["slug"] + ".html")
        page = share_page(d)
        if not os.path.exists(path) or open(path, encoding="utf-8").read() != page:
            with open(path, "w", encoding="utf-8") as f:
                f.write(page)
            changed = True

    if not changed:
        print("No changes - partnerships-data.json and share pages are already up to date.")
    else:
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(new_content + "\n")
        print(f"Updated partnerships-data.json - {len(deals)} total deals, {len(deals)} share pages.")

    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")


if __name__ == "__main__":
    main()
