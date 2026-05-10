"""
Image loader — loads PNG assets and resizes them.
Falls back to a coloured placeholder when an asset is missing,
so the app runs fully even before real artwork is added.
"""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
import tkinter as tk

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# Root of the project (parent of this file's package)
ASSETS_ROOT = Path(__file__).parent.parent / "assets"

# ── Placeholder generators ────────────────────────────────────────────────

def _placeholder_pil(width: int, height: int, color: str, text: str = "") -> "ImageTk.PhotoImage":
    img = Image.new("RGBA", (width, height), color)
    draw = ImageDraw.Draw(img)
    if text:
        try:
            font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((width - tw) // 2, (height - th) // 2), text, fill="#ffffff", font=font)
        except Exception:
            pass
    return ImageTk.PhotoImage(img)


def _placeholder_tk(width: int, height: int) -> tk.PhotoImage:
    """Minimal fallback when Pillow is not installed."""
    img = tk.PhotoImage(width=width, height=height)
    return img


# ── Public API ────────────────────────────────────────────────────────────

@lru_cache(maxsize=512)
def load_image(path: str | Path, width: int, height: int,
               placeholder_color: str = "#2a3040",
               placeholder_text: str = "") -> "ImageTk.PhotoImage | tk.PhotoImage":
    """
    Load an image from *path*, resize to (width, height), return a Tk-compatible object.
    Returns a placeholder if the file is missing or unreadable.
    """
    p = Path(path)
    if not p.is_absolute():
        p = ASSETS_ROOT / p

    if PIL_AVAILABLE:
        try:
            img = Image.open(p).convert("RGBA")
            img = img.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            return _placeholder_pil(width, height, placeholder_color, placeholder_text)
    else:
        return _placeholder_tk(width, height)


def agent_portrait(agent_id: str, size: int) -> "ImageTk.PhotoImage | tk.PhotoImage":
    path = Path("agents") / f"{agent_id}.png"
    return load_image(path, size, size, placeholder_color="#1e2636",
                      placeholder_text=agent_id[:2].upper())


def ability_icon(agent_id: str, icon_filename: str, size: int) -> "ImageTk.PhotoImage | tk.PhotoImage":
    path = Path("abilities") / agent_id / icon_filename
    return load_image(path, size, size, placeholder_color="#2a3040",
                      placeholder_text="?")