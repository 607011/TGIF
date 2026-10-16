# TGIF

A deliberately silly little utility that generates colorful `TGIF` snippets for chat and collaboration tools such as Microsoft Teams. It can either:

- produce a vibrant HTML snippet with randomized pastel colors, ready to paste into Teams
- generate an animated GIF with multiple TGIF variants in a looping palette-based animation

The project is intentionally playful rather than production-oriented, but it works well as a quick visual gimmick or a lightweight clipboard helper.

## What it does

The script creates a rainbow-like palette, builds a stylized `TGIF` wordmark, and copies the result to the clipboard when supported on your platform.

- HTML mode: produces a styled snippet that can be pasted directly into Teams or similar apps
- GIF mode: creates a short animated loop with randomized frames and saves it to a temporary GIF file, while also copying it to the clipboard when possible

### Example

![TGIF](example/example.gif)

## Requirements

- Python 3.14 (as specified in the Pipfile)
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

Save the generated GIF to a specific path:

```bash
pipenv run ./tgif.py --gif 50 --out ./tgif_animated.gif
```

A convenience `Makefile` is also included:

```bash
make
make gif
```

## Notes

- The program uses `Pillow` for image rendering.
- On macOS, rich HTML/GIF clipboard integration uses `pyobjc-framework-cocoa`.
- On Windows and Linux, clipboard behavior depends on available tools (`pyperclip`, `clip`, `wl-copy`, `xclip`, or `xsel`), with graceful fallback.
- GIF mode always writes a real `.gif` file (default: system temp directory) and tries to copy GIF data to the clipboard where possible.
- When no supported clipboard integration is available, HTML is printed to stdout and the GIF path is shown.
- Font selection is automatic and prefers macOS system fonts when available.


## Why this exists

Because some ideas are not "serious software" in the traditional sense—they are tiny, cheerful, and a little bit ridiculous. This project is exactly that.
