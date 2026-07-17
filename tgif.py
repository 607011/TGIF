#!/usr/bin/env python3
"""
Erzeugt einen Teams-HTML-Schnipsel mit "TGIF" in zufälligen,
aber harmonisch abgestimmten Farben und kopiert ihn in die Zwischenablage.

Mit dem Parameter --gif N wird stattdessen ein animiertes GIF erzeugt,
das N zufällig generierte TGIF-Varianten in Endlosschleife zeigt, und
dieses GIF wird in die Zwischenablage kopiert.
"""

import argparse
import colorsys
import io
import pathlib
import random
import tempfile

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]


def hsl_to_rgb(h, s, l):
    """HSL (0-1) → RGB (0-255)"""
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return int(r * 255), int(g * 255), int(b * 255)


def rgb_str(r, g, b):
    return f"rgb({r}, {g}, {b})"


def generate_palette(n_colors=7):
    """
    Erzeugt n_colors Farben mit gleichmäßig verteilten Hues,
    aber zufälligem Startwinkel – alle pastellig und hell.
    """
    base_hue = random.random()
    saturation = random.uniform(0.45, 0.75)
    lightness = random.uniform(0.72, 0.82)

    colors = []
    for i in range(n_colors):
        hue = (base_hue + i / n_colors) % 1.0
        # Leichte Variation in Sättigung und Helligkeit für Lebendigkeit
        s = saturation + random.uniform(-0.08, 0.08)
        l = lightness + random.uniform(-0.05, 0.05)
        s = max(0.3, min(1.0, s))
        l = max(0.6, min(0.92, l))
        colors.append(hsl_to_rgb(hue, s, l))
    return colors


def darker(r, g, b, factor=0.45):
    """Erzeugt eine deutlich dunklere Variante für den Text."""
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    l_dark = max(0.15, l * factor)
    r2, g2, b2 = colorsys.hls_to_rgb(h, l_dark, s)
    return int(r2 * 255), int(g2 * 255), int(b2 * 255)


def span(bg_rgb, text=" ", fg_rgb=None):
    bg = rgb_str(*bg_rgb)
    style = f"background-color: {bg}; font-size: x-large;"
    if fg_rgb:
        style += f" color: {rgb_str(*fg_rgb)};"
    char = "&nbsp;" if text.strip() == "" else text
    return f'<span style="{style}"><strong>{char}</strong></span>'


def build_sequence(palette):
    """
    Baut die Sequenz aus (bg, text, fg) für Deko- und Buchstaben-Zellen.
    Wird sowohl für den HTML-Schnipsel als auch für das GIF-Rendering benutzt.

    Struktur: Regenbogenstreifen links, TGIF in der Mitte, Streifen rechts.

    Gesamtsequenz der Farb-Indizes (Palette hat 7 Farben, 0–6):
      Linke Deko:  0 1 2 3 4 5 6
      TGIF:                  T=0 G=1 I=2 F=3   ← startet neu bei 0, kein Clash mit 6
      Rechte Deko:                     4 5 6 5 4 3 2 1 0  ← beginnt NACH F=3, also bei 4

    So gibt es an keiner Naht zwei gleiche Farben hintereinander.
    """
    n = len(palette)
    letters = list("TGIF")

    # Buchstaben bekommen die ersten 4 Palettenfarben (0–3)
    letter_colors = palette[:len(letters)]

    seq = []

    # Linke Dekoration: Palette vorwärts (0 → 6)
    for color in palette:
        seq.append((color, None, None))

    # TGIF: Farben 0–3 → nach Farbe 6 kommt 0, kein Clash
    for i, letter in enumerate(letters):
        bg = letter_colors[i]
        fg = darker(*bg)
        seq.append((bg, letter, fg))

    # Rechte Dekoration: beginnt bei Index 4 (nach F=3), läuft dann rückwärts
    # Sequenz: 4 5 6 5 4 3 2 1 0
    right_indices = list(range(len(letters), n)) + list(range(n - 1, -1, -1))
    for i in right_indices:
        seq.append((palette[i], None, None))

    return seq


def build_tgif_html(palette):
    """Baut den Teams-HTML-Schnipsel aus der Farb-Sequenz."""
    spans = [span(bg, text or " ", fg) for bg, text, fg in build_sequence(palette)]
    inner = "".join(spans)
    return f"<meta charset='utf-8'><span data-teams=\"true\">{inner}</span>"


def render_frame(palette, height=56, h_padding_ratio=0.22):
    """
    Rendert eine Farb-Sequenz als Bild (ein Frame des GIFs).
    Jede Zelle ist nur so breit wie ihr Zeichen (Leerzeichen für Deko,
    Buchstabe für TGIF) plus etwas Innenabstand – analog zum HTML-Schnipsel,
    wo die Spans ebenfalls nur so breit wie ihr Inhalt sind.
    """
    from PIL import Image, ImageDraw, ImageFont

    seq = build_sequence(palette)
    font_path = next((f for f in FONT_CANDIDATES if pathlib.Path(f).exists()), None)
    font = ImageFont.truetype(font_path, int(height * 0.62)) if font_path else ImageFont.load_default()

    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    h_padding = int(height * h_padding_ratio)

    cells = []
    for bg, text, fg in seq:
        char = text if text else " "
        bbox = measure.textbbox((0, 0), char, font=font)
        cell_w = (bbox[2] - bbox[0]) + 2 * h_padding
        cells.append((cell_w, bg, text, fg, bbox))

    width = sum(c[0] for c in cells)
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    x = 0
    for cell_w, bg, text, fg, (l, t, r, b) in cells:
        draw.rectangle([x, 0, x + cell_w, height], fill=bg)
        if text:
            tx = x + (cell_w - (r - l)) / 2 - l
            ty = (height - (b - t)) / 2 - t
            draw.text((tx, ty), text, font=font, fill=fg)
        x += cell_w

    return img


def build_animated_gif(n_frames, cell_size=56, frame_duration_ms=800):
    """Erzeugt n_frames zufällige TGIF-Frames und baut daraus ein Endlos-GIF."""
    frames = [render_frame(generate_palette(7), cell_size) for _ in range(n_frames)]
    buf = io.BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration_ms,
        loop=0,
    )
    return buf.getvalue()


def copy_to_clipboard(html: str):
    try:
        from AppKit import NSPasteboard, NSPasteboardTypeHTML
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        pb.setString_forType_(html, NSPasteboardTypeHTML)
        print("✓ HTML in Zwischenablage kopiert – einfach in Teams einfügen!")
    except ImportError:
        print("⚠ pyobjc nicht gefunden – HTML wird nur ausgegeben.\n")
        print(html)


def copy_gif_to_clipboard(gif_bytes: bytes):
    gif_path = pathlib.Path(tempfile.gettempdir()) / "tgif_animated.gif"
    gif_path.write_bytes(gif_bytes)

    try:
        from AppKit import NSPasteboard
        from Foundation import NSData, NSURL

        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        # Datei-Referenz: sorgt dafür, dass Apps, die Dateien einfügen
        # (Finder, Mail, Slack, ...), das echte animierte GIF erhalten.
        pb.writeObjects_([NSURL.fileURLWithPath_(str(gif_path))])
        # Rohe GIF-Daten zusätzlich als Bild-Typ, für Apps, die
        # Bilddaten direkt von der Zwischenablage lesen (z. B. Web-Apps).
        pb.addTypes_owner_(["com.compuserve.gif"], None)
        ns_data = NSData.dataWithBytes_length_(gif_bytes, len(gif_bytes))
        pb.setData_forType_(ns_data, "com.compuserve.gif")
        print("✓ Animiertes GIF in Zwischenablage kopiert – einfach einfügen!")
    except ImportError:
        print(f"⚠ pyobjc nicht gefunden – GIF wurde stattdessen gespeichert unter: {gif_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Erzeugt ein farbenfrohes TGIF.")
    parser.add_argument(
        "-g", "--gif", type=int, metavar="N",
        help="Statt des HTML-Schnipsels ein animiertes GIF mit N zufälligen "
             "TGIF-Varianten in Endlosschleife erzeugen und in die Zwischenablage kopieren.",
    )
    parser.add_argument(
        "--duration", type=int, default=50, metavar="MS",
        help="Anzeigedauer pro Frame in Millisekunden (Standard: 50).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.gif is not None:
        if args.gif < 1:
            raise SystemExit("N muss mindestens 1 sein.")
        gif_bytes = build_animated_gif(args.gif, frame_duration_ms=args.duration)
        copy_gif_to_clipboard(gif_bytes)
    else:
        palette = generate_palette(n_colors=7)
        html = build_tgif_html(palette)
        copy_to_clipboard(html)