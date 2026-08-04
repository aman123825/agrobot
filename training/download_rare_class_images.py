"""
Download sample images for rock/stump/ditch from free image APIs.
================================================================
Uses the Pexels API (free, 200 req/hr) to get starter images for
the three hardest obstacle classes.

IMPORTANT: These are general images, NOT annotated. After downloading,
you MUST annotate them with bounding boxes using Roboflow/CVAT/LabelImg.

Usage:
  1. Get a free API key from https://www.pexels.com/api/
  2. Set it: set PEXELS_API_KEY=your_key_here
  3. Run:    python download_rare_class_images.py
  4. Annotate the downloaded images (see OBSTACLE_DATASET_GUIDE.md)
"""

import os
import time
import urllib.request
from pathlib import Path

API_KEY = os.getenv("PEXELS_API_KEY", "")

# Search queries per class - multiple queries get diverse results
SEARCHES = {
    "rock": [
        "rock on dirt path",
        "boulder field agriculture",
        "stones farm ground",
        "rocks in grass",
        "large rock outdoor ground",
    ],
    "stump": [
        "tree stump field",
        "cut tree stump grass",
        "old tree stump forest",
        "tree stump farm",
        "wooden stump ground",
    ],
    "fence": [
        "farm fence field",
        "wooden fence rural",
        "wire fence agriculture",
        "barbed wire fence farm",
        "metal fence field",
    ],
    "ditch": [
        "irrigation ditch farm",
        "drainage ditch field",
        "water channel agriculture",
        "trench farm land",
        "canal irrigation rural",
    ],
}

IMAGES_PER_QUERY = 20  # Pexels returns max 80 per request
OUTPUT_DIR = Path("manual_data")


def search_pexels(query: str, per_page: int = 20) -> list[str]:
    """Search Pexels and return image URLs."""
    import json

    url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}&orientation=landscape"
    req = urllib.request.Request(url)
    req.add_header("Authorization", API_KEY)

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return [
                photo["src"]["medium"]  # 350x350 ish - good for training
                for photo in data.get("photos", [])
            ]
    except Exception as e:
        print(f"    Error: {e}")
        return []


def download_image(url: str, dest: Path) -> bool:
    """Download a single image."""
    try:
        urllib.request.urlretrieve(url, str(dest))
        return True
    except Exception:
        return False


def main():
    if not API_KEY:
        print("=" * 60)
        print("Pexels API key not set!")
        print("=" * 60)
        print()
        print("Option 1: Get a free key from https://www.pexels.com/api/")
        print("  Then run: set PEXELS_API_KEY=your_key_here")
        print()
        print("Option 2: Download images manually from:")
        print("  - https://www.pexels.com/search/rock%20field/")
        print("  - https://www.pexels.com/search/tree%20stump/")
        print("  - https://www.pexels.com/search/irrigation%20ditch/")
        print("  - https://www.pexels.com/search/farm%20fence/")
        print()
        print("Option 3: Take photos yourself (BEST for accuracy!)")
        print("  See OBSTACLE_DATASET_GUIDE.md for photography tips.")
        print()
        print("After getting images, annotate with Roboflow/CVAT/LabelImg")
        print("and place in manual_data/<class>/images/ and labels/")
        return

    print("=" * 60)
    print("Downloading sample images from Pexels")
    print("=" * 60)
    print("NOTE: You MUST annotate these with bounding boxes after download!")
    print()

    total = 0
    for class_name, queries in SEARCHES.items():
        img_dir = OUTPUT_DIR / class_name / "images"
        img_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n[{class_name}]")
        count = 0

        for query in queries:
            print(f"  Searching: '{query}'...")
            urls = search_pexels(query, IMAGES_PER_QUERY)
            print(f"    Found {len(urls)} images")

            for url in urls:
                dest = img_dir / f"{class_name}_{count:04d}.jpg"
                if download_image(url, dest):
                    count += 1

            # Rate limit: Pexels allows 200 req/hr
            time.sleep(1.5)

        print(f"  Downloaded: {count} images -> {img_dir}")
        total += count

    print(f"\n{'=' * 60}")
    print(f"Total downloaded: {total} images")
    print(f"{'=' * 60}")
    print()
    print("NEXT STEPS:")
    print("1. Review images - delete irrelevant ones")
    print("2. Annotate with bounding boxes:")
    print("   - Use https://app.roboflow.com/ (easiest)")
    print("   - Or https://app.cvat.ai/ (free)")
    print("   - Or: pip install labelImg && labelImg")
    print("3. Export annotations as YOLO format")
    print("4. Place .txt files in manual_data/<class>/labels/")
    print("5. Run: python prepare_obstacle_dataset_lite.py")


if __name__ == "__main__":
    main()
