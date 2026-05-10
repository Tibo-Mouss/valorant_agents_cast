"""
Main application window — two TeamColumns with bookmark buttons between them.
"""
from __future__ import annotations
import tkinter as tk
from models.team import Team
from ui import theme
from ui.team_column import TeamColumn


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Valorant Caster Companion")
        self.configure(bg=theme.BG_DARK)
        self.minsize(theme.WINDOW_MIN_W, theme.WINDOW_MIN_H)
        self.geometry(f"{theme.WINDOW_MIN_W}x{theme.WINDOW_MIN_H + 40}")

        # Model
        self._team_a = Team("Team A")
        self._team_b = Team("Team B")

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────

    def _build(self):
        # ── Title bar ─────────────────────────────────────────────────────
        title_bar = tk.Frame(self, bg=theme.BG_DARK)
        title_bar.pack(fill="x", padx=16, pady=(10, 6))

        tk.Label(title_bar,
                 text="VALORANT  CASTER  COMPANION",
                 bg=theme.BG_DARK,
                 fg=theme.ACCENT_RED,
                 font=(theme.FONT_FAMILY, 13, "bold")).pack(side="left")

        tk.Label(title_bar,
                 text="select agents · see ability names · cast better",
                 bg=theme.BG_DARK,
                 fg=theme.TEXT_SECONDARY,
                 font=theme.FONT_SMALL).pack(side="left", padx=14)

        # ── Main content: left col | divider+bookmarks | right col ────────
        main = tk.Frame(self, bg=theme.BG_DARK)
        main.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        main.columnconfigure(0, weight=1, uniform="col")
        main.columnconfigure(1, weight=0)   # bookmark strip
        main.columnconfigure(2, weight=1, uniform="col")
        main.rowconfigure(0, weight=1)

        # Left column frame (used as "opposite" by right's picker)
        self._left_frame = tk.Frame(main, bg=theme.BG_PANEL)
        self._left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 0))

        # Right column frame
        self._right_frame = tk.Frame(main, bg=theme.BG_PANEL)
        self._right_frame.grid(row=0, column=2, sticky="nsew", padx=(0, 0))

        # TeamColumns — each gets a ref to the OTHER frame
        self._col_a = TeamColumn(
            self._left_frame,
            side="left",
            team=self._team_a,
            get_opposite_frame=lambda: self._right_frame,
        )
        self._col_a.pack(fill="both", expand=True)

        self._col_b = TeamColumn(
            self._right_frame,
            side="right",
            team=self._team_b,
            get_opposite_frame=lambda: self._left_frame,
        )
        self._col_b.pack(fill="both", expand=True)

        # ── Divider strip with bookmark buttons ───────────────────────────
        divider = tk.Frame(main, bg=theme.BG_DARK, width=50)
        divider.grid(row=0, column=1, sticky="ns", padx=4)
        divider.pack_propagate(False)

        self._build_divider(divider)

    def _build_divider(self, divider: tk.Frame):
        """Central strip: VS label + two bookmark buttons."""
        # Centre everything vertically
        inner = tk.Frame(divider, bg=theme.BG_DARK)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        # Bookmark for left column (opens picker over RIGHT)
        self._bookmark_a = BookmarkButton(inner,
                                           side="right",
                                           on_click=self._col_a.open_picker)
        self._bookmark_a.pack(pady=(0, 8))

        tk.Label(inner, text="VS",
                 bg=theme.BG_DARK, fg=theme.ACCENT_RED,
                 font=(theme.FONT_FAMILY, 11, "bold")).pack()

        # Bookmark for right column (opens picker over LEFT)
        self._bookmark_b = BookmarkButton(inner,
                                           side="left",
                                           on_click=self._col_b.open_picker)
        self._bookmark_b.pack(pady=(8, 0))


# ── BookmarkButton ────────────────────────────────────────────────────────

class BookmarkButton(tk.Canvas):
    """
    A small bookmark-shaped toggle button.
    *side*: "left" | "right" — which side the pointed tip faces.
    """
    W = theme.BOOKMARK_W
    H = theme.BOOKMARK_H

    def __init__(self, parent: tk.Widget, side: str, on_click: callable, **kwargs):
        super().__init__(parent,
                         width=self.W, height=self.H,
                         bg=theme.BG_DARK,
                         bd=0, highlightthickness=0,
                         cursor="hand2",
                         **kwargs)
        self._side = side
        self._on_click = on_click
        self._active = False
        self._draw(active=False)
        self.bind("<Button-1>", self._toggle)
        self.bind("<Enter>", lambda e: self._draw(hover=True))
        self.bind("<Leave>", lambda e: self._draw(hover=False))

    def _toggle(self, event=None):
        self._active = not self._active
        self._draw(active=self._active)
        self._on_click()

    def deactivate(self):
        self._active = False
        self._draw(active=False)

    def _draw(self, active: bool = None, hover: bool = False):
        if active is None:
            active = self._active
        self.delete("all")

        color = theme.ACCENT_RED if active else (
            theme.ACCENT_RED_DIM if hover else theme.BG_HOVER
        )
        w, h = self.W, self.H
        notch = 7  # depth of V-notch at bottom

        if self._side == "right":
            # Notch on the left side (tab attached to left column's right edge)
            points = [
                w, 0,      # top-right
                0, 0,      # top-left
                0, h,      # bottom-left (notch tip)
                w//2, h - notch,
                w, h,      # bottom-right
            ]
        else:
            # Notch on the right side (tab attached to right column's left edge)
            points = [
                0, 0,      # top-left
                w, 0,      # top-right
                w, h,      # bottom-right (notch tip)
                w//2, h - notch,
                0, h,      # bottom-left
            ]

        self.create_polygon(points, fill=color, outline="")

        # Arrow indicator
        arrow = "▶" if self._side == "right" else "◀"
        self.create_text(w // 2, h // 2 - 4,
                          text=arrow,
                          fill="#ffffff" if active else theme.TEXT_SECONDARY,
                          font=(theme.FONT_FAMILY, 7))