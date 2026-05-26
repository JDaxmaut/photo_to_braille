from PIL import Image

DOT_MAP = [
    (0, 0),
    (1, 0),
    (2, 0),
    (0, 1),
    (1, 1),
    (2, 1),
    (3, 0),
    (3, 1),
]

BRAILLE_BASE = 0x2800


def image_to_braille(image_path, width=60, threshold=None):
    img = Image.open(image_path).convert("L")

    pixel_w = width * 2
    aspect = img.height / img.width
    pixel_h = int(pixel_w * aspect * 0.72)
    pixel_h = (pixel_h + 3) // 4 * 4
    img = img.resize((pixel_w, pixel_h))

    px = list(img.getdata())

    if threshold is None:
        sorted_px = sorted(px)
        threshold = sorted_px[len(sorted_px) // 4]
        threshold = min(255, int(threshold * 1.2))

    out = []

    for y in range(0, pixel_h, 4):
        row = []
        for x in range(0, pixel_w, 2):
            code = BRAILLE_BASE

            for i, (dr, dc) in enumerate(DOT_MAP):
                idx = (y + dr) * pixel_w + (x + dc)
                if idx < len(px) and px[idx] < threshold:
                    code |= (1 << i)

            row.append(chr(code))

        out.append("".join(row))

    return "\n".join(out)


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else input("Image path: ").strip().strip('"')
    try:
        result = image_to_braille(path, width=60)
        print()
        print(result)

        with open("braille_art.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print("\nSaved to braille_art.txt")
    except Exception as e:
        print(f"Error: {e}")
