# Photo to Braille ASCII Art

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Pillow](https://img.shields.io/badge/Pillow-powered-green.svg)
![Status](https://img.shields.io/badge/status-draft-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Converts any image into Braille Unicode ASCII art. Each Braille character represents a 2×4 pixel block, creating detailed terminal-friendly art.

## Example

```
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠶⠶⠶⢦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠾⠛⠉⠀⠀⠀⠀⠀⠈⠙⠳⣤⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⠞⠋⠀⠀⢀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠈⠳⣄⠀⠀⠀⠀⠀
```

## Usage

```bash
pip install Pillow
python photo_to_braille.py path/to/image.jpg
```

The output is printed to the console and saved to `braille_art.txt`.

### Arguments

| Argument | Description |
|---|---|
| `path` | Path to image file (optional — prompts if omitted) |
| `width` | Output width in Braille characters (default: 60) — edit in `image_to_braille()` |

## How it works

1. Image is converted to grayscale and resized to `width × 2` pixels wide
2. Height is adjusted to maintain aspect ratio (rounded to multiple of 4)
3. Each 2×4 pixel block is mapped to a Braille Unicode character (U+2800–U+28FF)
4. Adaptive thresholding picks the best black/white cutoff for maximum detail

No external dependencies beyond Pillow.