# Photo to Braille ASCII Art

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Pillow](https://img.shields.io/badge/Pillow-powered-green.svg)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-UI-orange.svg)

Converts any image into Braille Unicode ASCII art. Each Braille character (U+2800–U+28FF) represents a 2×4 pixel block with per-dot thresholding, preserving gradients, shadows, and fine detail.

## Features

- **Full Braille matrix** — all 256 patterns used for smooth gradients
- **Desktop GUI** — custom dark theme (music-player aesthetic), album-art preview
- **CLI scripts** — both original and improved engine included
- **Aspect ratio correction** — compensates for Braille cell vertical stretch
- **No regular spaces** — empty cells use U+2800 (Braille blank), all rows equal-width

## GUI

```bash
pip install -r requirements.txt
python gui.py
```

- Left panel: settings (width slider, sensitivity, invert toggle)
- Right panel: image preview (click to select/replace), filename, resolution, file size
- Convert button saves `*_braille.txt` with full Braille art
- Save directory picker, status bar

## Scripts

| Script | Description |
|---|---|
| `gui.py` | Desktop GUI (CustomTkinter + Pillow) |
| `photo_to_ascii.py` | CLI — mean-threshold, sensitivity control, full DOT_MAP engine |
| `photo_to_braille.py` | CLI — percentile-threshold, same engine |

## Example

![Mavashi](mavashi.png)

## Scripts

```bash
python photo_to_ascii.py
# Enter path when prompted
```

| Parameter | Default |
|---|---|
| `width` | 120 |
| `sensitivity` | 1.0 (0.5–1.5) |

### photo_to_braille.py (CLI)

```bash
python photo_to_braille.py path/to/image.jpg
```

Fixed width 60, percentile-based threshold.

## How it works

1. Image is grayscaled and resized to `width × 2` pixels wide
2. Height = `pixel_w × aspect × 0.72` — compensates Braille cell shape (2:1 font aspect)
3. Each 2×4 pixel block → one Braille char via `DOT_MAP` (per-pixel dot bit)
4. Empty cells → U+2800 (Braille blank), ensuring uniform line widths
5. Output saved as UTF-8 `.txt`, renderable in any monospace font

```
Uses up to 147/256 Braille patterns on typical photos — smooth gradients, no banding.
```

## Requirements

- Python 3.8+
- Pillow
- customtkinter (for GUI)

## Roadmap

- Standalone `.exe` build (no Python required)
