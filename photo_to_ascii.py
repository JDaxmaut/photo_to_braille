from PIL import Image

# Соответствие позиции пикселя в блоке 2×4 биту символа Брайля
# Каждый элемент: (смещение_строки, смещение_столбца)
# i-й элемент → бит i (1 << i) → точка Брайля
DOT_MAP = [
    (0, 0),  # i=0 (0x01) → точка 1, левый верхний
    (1, 0),  # i=1 (0x02) → точка 2, левый средний 1
    (2, 0),  # i=2 (0x04) → точка 3, левый средний 2
    (0, 1),  # i=3 (0x08) → точка 4, правый верхний
    (1, 1),  # i=4 (0x10) → точка 5, правый средний 1
    (2, 1),  # i=5 (0x20) → точка 6, правый средний 2
    (3, 0),  # i=6 (0x40) → точка 7, левый нижний
    (3, 1),  # i=7 (0x80) → точка 8, правый нижний
]

BRAILLE_BASE = 0x2800


def image_to_braille(image_path, width=120, sensitivity=1.0):
    """
    width: ширина арта в символах (чем больше, тем чётче)
    sensitivity: коэффициент чувствительности (от 0.5 до 1.5).
                 Меньше 1.0 — линии тоньше, больше 1.0 — линии жирнее.
    """
    img = Image.open(image_path).convert("L")

    pixel_w = width * 2
    aspect = img.height / img.width
    pixel_h = int(pixel_w * aspect * 0.72)
    pixel_h = (pixel_h + 3) // 4 * 4
    img = img.resize((pixel_w, pixel_h))

    px = list(img.getdata())

    threshold = (sum(px) / len(px)) * sensitivity
    threshold = max(0, min(255, threshold))

    out = []

    for y in range(0, pixel_h, 4):
        row = []
        for x in range(0, pixel_w, 2):
            code = BRAILLE_BASE

            for i, (dr, dc) in enumerate(DOT_MAP):
                idx = (y + dr) * pixel_w + (x + dc)
                if idx < len(px) and px[idx] >= threshold:
                    code |= (1 << i)

            row.append(chr(code))

        out.append("".join(row))

    return "\n".join(out)


if __name__ == "__main__":
    path = input("Путь к фото: ").strip().strip('"')
    try:
        result = image_to_braille(path, width=120, sensitivity=1.0)
        print()
        print(result)

        with open("braille_art.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print("\nСохранено в braille_art.txt")
    except Exception as e:
        print(f"Ошибка: {e}")
