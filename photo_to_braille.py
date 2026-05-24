from PIL import Image

BRAILLE_BITS = [
    0x01, 0x02, 0x04, 0x40,
    0x08, 0x10, 0x20, 0x80,
]

BRAILLE_BASE = 0x2800


def pixels_to_braille(block, threshold):
    code = BRAILLE_BASE
    for i, val in enumerate(block):
        if val < threshold:
            code |= BRAILLE_BITS[i]
    return chr(code)


def image_to_braille(image_path, width=60):
    img = Image.open(image_path).convert("L")

    braille_w = width
    img_w = braille_w * 2
    aspect_ratio = img.height / img.width
    img_h = int(img_w * aspect_ratio)
    img_h = (img_h + 3) // 4 * 4
    img = img.resize((img_w, img_h))

    pixels = list(img.getdata())

    sorted_pixels = sorted(pixels)
    threshold = sorted_pixels[len(sorted_pixels) // 4]
    threshold = min(255, int(threshold * 1.2))

    result = []

    for y in range(0, img_h, 4):
        line = []
        for x in range(0, img_w, 2):
            block = []
            for dy in range(4):
                for dx in range(2):
                    px = x + dx
                    py = y + dy
                    if px < img_w and py < img_h:
                        block.append(pixels[py * img_w + px])
                    else:
                        block.append(255)
            line.append(pixels_to_braille(block, threshold))
        result.append("".join(line))

    return "\n".join(result)


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else input("Image path: ").strip().strip('"')
    try:
        result = image_to_braille(path, width=60)
        print()
        print(result)

        with open("braille_art.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\nSaved to braille_art.txt")
    except Exception as e:
        print(f"Error: {e}")