"""Fetch eCFR structure & version history (v1 API).

Usage:
  python fetch_data.py          # download *all* titles
  python fetch_data.py 21       # download only Title 21
  python fetch_data.py --force  # ignore cached data and download fresh copies

Each Title has its own `up_to_date_as_of` snapshot, so we fetch each
structure individually. This implementation uses concurrent requests for speed.
"""

from pathlib import Path
import argparse, requests, time, sys
import concurrent.futures

try:
    import ujson as json  # Much faster JSON processing
except ImportError:
    import json

    print("⚠️ Consider installing ujson for faster JSON processing: pip install ujson")

BASE = "https://www.ecfr.gov/api/versioner/v1"
DATA_DIR = Path("data")
TITLES_DIR = DATA_DIR / "titles"
TITLES_DIR.mkdir(parents=True, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("title", nargs="?", help="Title number to fetch (optional)")
parser.add_argument(
    "--force", action="store_true", help="Force download even if cached"
)
args = parser.parse_args()


def should_update_title(num, current_snapshot):
    """Check if we need to update this title based on snapshot date"""
    if args.force:
        return True

    title_path = TITLES_DIR / f"title-{num}.json"
    if not title_path.exists():
        return True

    try:
        # Check if we already have the latest data
        meta_path = TITLES_DIR / f"title-{num}-meta.json"
        if meta_path.exists():
            existing_meta = json.loads(meta_path.read_text())
            if existing_meta.get("snapshot") == current_snapshot:
                print(
                    f"⏩ Title {num}: Already have latest snapshot ({current_snapshot})"
                )
                return False
    except:
        pass
    return True


# -----------------------------------------------------------------------------
# 1️⃣  Get titles index
# -----------------------------------------------------------------------------
index_url = f"{BASE}/titles.json"
try:
    response = requests.get(index_url, timeout=30)
    response.raise_for_status()  # Raise exception for HTTP errors
    index = response.json()
except Exception as e:
    print(f"🚨 Failed to fetch {index_url}: {e}")
    sys.exit(1)

titles_raw = index["titles"]  # list of dicts
# helper – show any reserved titles in the index
reserved_titles = [t for t in titles_raw if t.get("reserved")]
if reserved_titles:
    print(
        "🔒 Reserved titles in index:",
        ", ".join(str(t["number"]) for t in reserved_titles),
    )
else:
    print("✅ No titles are marked reserved")
info = {
    str(t["number"]): t["up_to_date_as_of"] for t in titles_raw if not t.get("reserved")
}

if args.title:
    if str(args.title) not in info:
        print(f"❌ Title {args.title} not found in index.")
        sys.exit(1)
    title_nums = [str(args.title)]
else:
    title_nums = sorted(info.keys(), key=int)

meta = {
    # total titles including reserved ones per index (should be 50 as of 2025‑05‑14)
    "num_titles": len(titles_raw),
    # non‑reserved titles (useful for downstream analytics)
    "num_titles_non_reserved": len(info),
    "fetched": time.strftime("%Y-%m-%d %H:%M:%S"),
}
(DATA_DIR / "meta.json").write_text(json.dumps(meta, indent=2))

# Filter titles that need updating
titles_to_fetch = []
for num in title_nums:
    if should_update_title(num, info[num]):
        titles_to_fetch.append(num)

if not titles_to_fetch:
    print("✅ All titles are up to date!")
    sys.exit(0)

print(f"📑 Titles to fetch: {', '.join(titles_to_fetch)}")


# -----------------------------------------------------------------------------
# 2️⃣  Download structure + versions per title in parallel
# -----------------------------------------------------------------------------
def fetch_title(num):
    """Fetch both structure and versions for a title in parallel"""
    snap_date = info[num]
    result = {"number": num, "success": False}

    try:
        # Fetch structure
        struct_url = f"{BASE}/structure/{snap_date}/title-{num}.json"
        struct_response = requests.get(struct_url, timeout=60)
        struct_response.raise_for_status()
        struct = struct_response.json()

        # Fetch versions
        vers_url = f"{BASE}/versions/title-{num}.json"
        vers_response = requests.get(vers_url, timeout=60)
        vers_response.raise_for_status()
        vers = vers_response.json()

        # Write title-specific files
        (TITLES_DIR / f"title-{num}.json").write_text(json.dumps(struct, indent=2))
        (TITLES_DIR / f"title-{num}-versions.json").write_text(
            json.dumps(vers, indent=2)
        )

        # Write metadata for incremental updates
        meta_info = {
            "snapshot": snap_date,
            "fetched": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        (TITLES_DIR / f"title-{num}-meta.json").write_text(json.dumps(meta_info))

        result["success"] = True
        result["structure"] = struct
        result["versions"] = vers
        print(f"✅ Title {num}: Successfully downloaded")

    except Exception as e:
        print(f"❌ Title {num}: Failed - {str(e)}")
        result["error"] = str(e)

    return result


# Download titles in parallel
regulations = {}
versions_all = {}
start_time = time.time()

# Use ThreadPoolExecutor for parallel downloads
# Adjust max_workers based on your system and network capabilities
max_workers = min(10, len(titles_to_fetch))  # Don't use more than 10 threads
print(f"🚀 Starting parallel downloads with {max_workers} workers")

with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_to_title = {
        executor.submit(fetch_title, num): num for num in titles_to_fetch
    }

    for future in concurrent.futures.as_completed(future_to_title):
        result = future.result()
        num = result["number"]

        if result["success"]:
            regulations[num] = result["structure"]
            versions_all[num] = result["versions"]

# -----------------------------------------------------------------------------
# 3️⃣  Persist merged outputs
# -----------------------------------------------------------------------------
(DATA_DIR / "regulations.json").write_text(json.dumps(regulations))
(DATA_DIR / "versions.json").write_text(json.dumps(versions_all))

# Calculate and display statistics
end_time = time.time()
elapsed = end_time - start_time
success_count = sum(1 for num in titles_to_fetch if num in regulations)
failed_count = len(titles_to_fetch) - success_count

print("=" * 60)
print(f"✅ Fetch complete in {elapsed:.2f} seconds")
print(f"📊 Stats: {success_count} titles fetched successfully, {failed_count} failed")
print("=" * 60)
