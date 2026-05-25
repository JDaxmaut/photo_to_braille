from PIL import Image

BRAILLE_BITS = [
    0x01, 0x02, 0x04, 0x40,  # левая колонка: верх → низ
    0x08, 0x10, 0x20, 0x80,  # правая колонка: верх → низ
]

BRAILLE_BASE = 0x2800

def pixels_to_braille(block, threshold):
    code = BRAILLE_BASE
    has_points = False
    for i, val in enumerate(block):
        if val >= threshold:  
            code |= BRAILLE_BITS[i]
            has_points = True
            
    # Полная замена пустого Брайля на пробел (убирает полосы)
    if not has_points:
        return " "
        
    return chr(code)

def image_to_braille(image_path, width=120, sensitivity=1.0):
    """
    width: ширина арта в символах (чем больше, тем чётче)
    sensitivity: коэффициент чувствительности (от 0.5 до 1.5). 
                 Меньше 1.0 — линии тоньше, больше 1.0 — линии жирнее.
    """
    img = Image.open(image_path).convert("L")

    braille_w = width
    img_w = braille_w * 2
    aspect_ratio = img.height / img.width
    img_h = int(img_w * aspect_ratio)
    img_h = (img_h + 3) // 4 * 4
    img = img.resize((img_w, img_h))

    pixels = list(img.getdata())
    
    # Расчёт адаптивного порога с учётом чувствительности
    threshold = (sum(pixels) / len(pixels)) * sensitivity
    threshold = max(0, min(255, threshold))

    result = []

    for y in range(0, img_h, 4):
        line = []
        for x in range(0, img_w, 2):
            block = []
            
            for dy in range(4):
                px = x + 0
                py = y + dy
                block.append(pixels[py * img_w + px] if px < img_w and py < img_h else 0)
            
            for dy in range(4):
                px = x + 1
                py = y + dy
                block.append(pixels[py * img_w + px] if px < img_w and py < img_h else 0)

            line.append(pixels_to_braille(block, threshold))
        result.append("".join(line))

    return "\n".join(result)

if __name__ == "__main__":
    path = input("Путь к фото: ").strip().strip('"')
    try:
        # Увеличили width до 120 для высокой чёткости букв
        result = image_to_braille(path, width=120, sensitivity=1.0)
        print()
        print(result)

        with open("braille_art.txt", "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\nСохранено в braille_art.txt с высокой чёткостью!")
    except Exception as e:
        print(f"Ошибка: {e}")
