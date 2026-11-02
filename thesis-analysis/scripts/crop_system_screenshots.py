from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path("/Users/eddy/Codes/design-platform/thesis-analysis/figures/screenshots")
SPECS = {
    "c-home.jpg": (0, 0, 1280, 1000),
    "c-product-order.jpg": (0, 0, 1280, 720),
    "c-orders.jpg": (0, 0, 1280, 1120),
    "c-publish.jpg": (0, 0, 1280, 1100),
    "c-profile-credit.jpg": (0, 0, 1280, 720),
    "admin-dashboard.jpg": (0, 0, 1280, 980),
    "admin-reports.jpg": (0, 0, 1280, 720),
}


def main() -> None:
    for name, crop in SPECS.items():
        source = ROOT / name
        with Image.open(source) as image:
            clipped = image.crop(crop)
            output = ROOT / name.replace(".jpg", "-crop.jpg")
            clipped.save(output, quality=94)
            print(output)


if __name__ == "__main__":
    main()
