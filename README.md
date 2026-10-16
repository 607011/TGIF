# TGIF

A deliberately silly little utility that generates colorful `TGIF` snippets for chat and collaboration tools such as Microsoft Teams. It can either:

- produce a vibrant HTML snippet with randomized pastel colors, ready to paste into Teams
- generate an animated GIF with multiple TGIF variants in a looping palette-based animation

The project is intentionally playful rather than production-oriented, but it works well as a quick visual gimmick or a lightweight clipboard helper.

## What it does

The script creates a rainbow-like palette, builds a stylized `TGIF` wordmark, and copies the result to the macOS clipboard.

- HTML mode: produces a styled snippet that can be pasted directly into Teams or similar apps
- GIF mode: creates a short animated loop with randomized frames and saves it to a temporary GIF file, while also copying it to the clipboard when possible

## Requirements

- Python 3.14 (as specified in the Pipfile)
- macOS (for clipboard integration via AppKit)
- `pipenv`

## Installation

```bash
pipenv install
```

## Usage

Generate a single HTML snippet:

```bash
pipenv run ./tgif.py
```

Generate an animated GIF with 50 frames:

```bash
pipenv run ./tgif.py --gif 50
```

Customize the frame delay:

```bash
pipenv run ./tgif.py --gif 50 --duration 100
```

A convenience `Makefile` is also included:

```bash
make
make gif
```

## Notes

- The program uses `Pillow` for image rendering and `pyobjc-framework-cocoa` for clipboard integration.
- When `pyobjc` is unavailable, the script falls back to printing the HTML to stdout or saving the GIF to a temp file instead of copying it to the clipboard.
- Font selection is automatic and prefers macOS system fonts when available.


## Why this exists

Because some ideas are not "serious software" in the traditional sense—they are tiny, cheerful, and a little bit ridiculous. This project is exactly that.
