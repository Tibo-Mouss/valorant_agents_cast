"""
Main application window — two TeamColumns with bookmark buttons between them.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from models.team import Team
from ui import theme
from ui.team_column import TeamColumn
from translations.locale_manager import locale_manager
from ui.image_loader import agent_portrait
from ui.overlay_window import OverlayWindow, ScreenInfo, available_screens
from data.agents import ALL_AGENTS


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

        # Overlay state
        self._overlay_window: OverlayWindow | None = None
        self._overlay_enabled = False
        self._screens: list[ScreenInfo] = available_screens(self)
        self._screen_var = tk.StringVar(value=self._screens[0].name if self._screens else "Screen 1")

        # Pre-cache agent portrait images for the picker (runs in background)
        self._pre_cache_images()

        self._build()

    def _pre_cache_images(self):
        """
        Pre-load agent portrait images in the background.
        This speeds up the agent picker UI since all images will already be cached
        when the picker opens, eliminating the initial load delay.
        """
        def cache_images():
            for agent in ALL_AGENTS:
                # Load at the picker icon size to cache it
                agent_portrait(agent.id, theme.PICKER_ICON)
        
        # Schedule on next event loop iteration to not block UI startup
        self.after(100, cache_images)

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

        # ── Language and overlay controls (right side of title bar) ─────
        self._build_lang_selector(title_bar)
        self._build_overlay_controls(title_bar)

        # ── Team names row with swap button ───────────────────────────────
        self._build_team_names_row()

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
            show_team_name=False,
            on_team_change=self._refresh_overlay,
        )
        self._col_a.pack(fill="both", expand=True)

        self._col_b = TeamColumn(
            self._right_frame,
            side="right",
            team=self._team_b,
            get_opposite_frame=lambda: self._left_frame,
            show_team_name=False,
            on_team_change=self._refresh_overlay,
        )
        self._col_b.pack(fill="both", expand=True)

        # ── Divider strip with bookmark buttons ───────────────────────────
        divider = tk.Frame(main, bg=theme.BG_DARK, width=50)
        divider.grid(row=0, column=1, sticky="ns", padx=4)
        divider.pack_propagate(False)

        self._build_divider(divider)

        # Wire bookmark refs so columns can reset them when picker closes via ✕
        self._col_a.set_bookmark(self._bookmark_a)
        self._col_b.set_bookmark(self._bookmark_b)

    def _build_lang_selector(self, parent: tk.Frame):
        """Build the language dropdown on the right end of the title bar."""
        locales = locale_manager.available_locales()   # [{"code", "language"}, ...]

        # Label
        tk.Label(parent, text="🌐",
                 bg=theme.BG_DARK, fg=theme.TEXT_SECONDARY,
                 font=(theme.FONT_FAMILY, 10)).pack(side="right", padx=(4, 0))

        # Style the combobox to match the dark theme
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Lang.TCombobox",
                        fieldbackground=theme.BG_INPUT,
                        background=theme.BG_INPUT,
                        foreground=theme.TEXT_PRIMARY,
                        selectbackground=theme.ACCENT_RED,
                        selectforeground="#ffffff",
                        bordercolor=theme.BG_HOVER,
                        arrowcolor=theme.TEXT_SECONDARY,
                        relief="flat")
        style.map("Lang.TCombobox",
                  fieldbackground=[("readonly", theme.BG_INPUT)],
                  foreground=[("readonly", theme.TEXT_PRIMARY)])

        language_names = [loc["language"] for loc in locales]
        current_name = next(
            (loc["language"] for loc in locales
             if loc["code"] == locale_manager.current_code),
            language_names[0] if language_names else "English"
        )

        self._lang_var = tk.StringVar(value=current_name)
        combo = ttk.Combobox(parent,
                              textvariable=self._lang_var,
                              values=language_names,
                              state="readonly",
                              width=12,
                              style="Lang.TCombobox",
                              font=(theme.FONT_FAMILY, 9))
        combo.pack(side="right", padx=(0, 6))

        def _on_lang_change(event=None):
            selected_name = self._lang_var.get()
            code = next(
                (loc["code"] for loc in locales if loc["language"] == selected_name),
                None
            )
            if code:
                locale_manager.set_locale(code)

        combo.bind("<<ComboboxSelected>>", _on_lang_change)

    def _build_overlay_controls(self, parent: tk.Frame):
        """Build screen selector and overlay on/off button."""
        tk.Label(parent, text="🖥️",
                 bg=theme.BG_DARK, fg=theme.TEXT_SECONDARY,
                 font=(theme.FONT_FAMILY, 10)).pack(side="right", padx=(4, 0))

        screen_names = [screen.name for screen in self._screens]
        self._screen_combo = ttk.Combobox(parent,
                                         textvariable=self._screen_var,
                                         values=screen_names,
                                         state="readonly",
                                         width=12,
                                         style="Lang.TCombobox",
                                         font=(theme.FONT_FAMILY, 9))
        self._screen_combo.pack(side="right", padx=(0, 6))
        self._screen_combo.bind("<<ComboboxSelected>>", self._on_screen_change)

        self._overlay_btn = tk.Button(parent,
                                     text="Overlay Off",
                                     bg=theme.BG_DARK,
                                     fg=theme.TEXT_SECONDARY,
                                     activebackground=theme.ACCENT_RED,
                                     activeforeground="#ffffff",
                                     font=(theme.FONT_FAMILY, 9),
                                     bd=0,
                                     cursor="hand2",
                                     command=self._toggle_overlay)
        self._overlay_btn.pack(side="right", padx=(0, 6))
        self._update_overlay_button()

    def _get_selected_screen(self) -> ScreenInfo | None:
        return next((screen for screen in self._screens
                     if screen.name == self._screen_var.get()),
                    self._screens[0] if self._screens else None)

    def _on_screen_change(self, event=None):
        if self._overlay_enabled and self._overlay_window:
            selected = self._get_selected_screen()
            if selected:
                self._overlay_window.refresh(selected)

    def _toggle_overlay(self):
        self._overlay_enabled = not self._overlay_enabled
        if self._overlay_enabled:
            selected = self._get_selected_screen()
            if selected:
                self._overlay_window = OverlayWindow(
                    self,
                    self._team_a,
                    self._team_b,
                    selected,
                    on_close=self._set_overlay_off,
                )
        else:
            if self._overlay_window and self._overlay_window.winfo_exists():
                self._overlay_window.destroy()
            self._overlay_window = None
        self._update_overlay_button()

    def _set_overlay_off(self):
        self._overlay_enabled = False
        if self._overlay_window and self._overlay_window.winfo_exists():
            self._overlay_window.destroy()
        self._overlay_window = None
        self._update_overlay_button()

    def _update_overlay_button(self):
        if self._overlay_enabled:
            self._overlay_btn.configure(text="Overlay On",
                                       bg=theme.ACCENT_RED,
                                       fg="#ffffff")
        else:
            self._overlay_btn.configure(text="Overlay Off",
                                       bg=theme.BG_DARK,
                                       fg=theme.TEXT_SECONDARY)

    def _refresh_overlay(self):
        if self._overlay_enabled and self._overlay_window:
            selected = self._get_selected_screen()
            if selected:
                self._overlay_window.refresh(selected)

    def _build_team_names_row(self):
        """Build the team names row with swap button in the middle."""
        names_row = tk.Frame(self, bg=theme.BG_DARK)
        names_row.pack(fill="x", padx=8, pady=8)

        names_row.columnconfigure(0, weight=1)
        names_row.columnconfigure(1, weight=0)
        names_row.columnconfigure(2, weight=1)

        # Left team name input
        left_frame = tk.Frame(names_row, bg=theme.BG_DARK)
        left_frame.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        # Store reference so we can update it later
        self._team_a_name_var = tk.StringVar(value=self._team_a.name)
        def _on_a_name_change(*_):
            self._team_a.name = self._team_a_name_var.get()
            self._refresh_overlay()
        self._team_a_name_var.trace_add("write", _on_a_name_change)
        team_a_entry = tk.Entry(left_frame,
                                textvariable=self._team_a_name_var,
                                bg=theme.BG_INPUT,
                                fg=theme.TEXT_PRIMARY,
                                insertbackground=theme.TEXT_PRIMARY,
                                relief="flat",
                                font=theme.FONT_TITLE,
                                bd=4)
        team_a_entry.pack(fill="x", ipady=4)

        # Swap button in the middle
        swap_btn = tk.Button(names_row,
                              text="⇄",
                              bg=theme.BG_DARK,
                              fg=theme.TEXT_SECONDARY,
                              activebackground=theme.ACCENT_RED,
                              activeforeground="#fff",
                              font=(theme.FONT_FAMILY, 16, "bold"),
                              bd=0,
                              cursor="hand2",
                              command=self._swap_teams,
                              padx=12,
                              pady=4)
        swap_btn.grid(row=0, column=1, padx=8)

        # Right team name input
        right_frame = tk.Frame(names_row, bg=theme.BG_DARK)
        right_frame.grid(row=0, column=2, sticky="ew", padx=(8, 0))

        self._team_b_name_var = tk.StringVar(value=self._team_b.name)
        def _on_b_name_change(*_):
            self._team_b.name = self._team_b_name_var.get()
            self._refresh_overlay()
        self._team_b_name_var.trace_add("write", _on_b_name_change)
        team_b_entry = tk.Entry(right_frame,
                                textvariable=self._team_b_name_var,
                                bg=theme.BG_INPUT,
                                fg=theme.TEXT_PRIMARY,
                                insertbackground=theme.TEXT_PRIMARY,
                                relief="flat",
                                font=theme.FONT_TITLE,
                                bd=4)
        team_b_entry.pack(fill="x", ipady=4)

    # ── Build lang selector ────────────────────────────────────────────────

    def _build_lang_selector(self, parent: tk.Frame):
        """Build the language dropdown on the right end of the title bar."""
        locales = locale_manager.available_locales()   # [{"code", "language"}, ...]

        # Label
        tk.Label(parent, text="🌐",
                 bg=theme.BG_DARK, fg=theme.TEXT_SECONDARY,
                 font=(theme.FONT_FAMILY, 10)).pack(side="right", padx=(4, 0))

        # Style the combobox to match the dark theme
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Lang.TCombobox",
                        fieldbackground=theme.BG_INPUT,
                        background=theme.BG_INPUT,
                        foreground=theme.TEXT_PRIMARY,
                        selectbackground=theme.ACCENT_RED,
                        selectforeground="#ffffff",
                        bordercolor=theme.BG_HOVER,
                        arrowcolor=theme.TEXT_SECONDARY,
                        relief="flat")
        style.map("Lang.TCombobox",
                  fieldbackground=[("readonly", theme.BG_INPUT)],
                  foreground=[("readonly", theme.TEXT_PRIMARY)])

        language_names = [loc["language"] for loc in locales]
        current_name = next(
            (loc["language"] for loc in locales
             if loc["code"] == locale_manager.current_code),
            language_names[0] if language_names else "English"
        )

        self._lang_var = tk.StringVar(value=current_name)
        combo = ttk.Combobox(parent,
                              textvariable=self._lang_var,
                              values=language_names,
                              state="readonly",
                              width=12,
                              style="Lang.TCombobox",
                              font=(theme.FONT_FAMILY, 9))
        combo.pack(side="right", padx=(0, 6))

        def _on_lang_change(event=None):
            selected_name = self._lang_var.get()
            code = next(
                (loc["code"] for loc in locales if loc["language"] == selected_name),
                None
            )
            if code:
                locale_manager.set_locale(code)

        combo.bind("<<ComboboxSelected>>", _on_lang_change)

    # ── Build divider ──────────────────────────────────────────────────────

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

    def _swap_teams(self):
        """Swap team names and agents between left and right columns."""
        self._team_a.swap_with(self._team_b)
        # Refresh both columns to display the swapped data
        self._team_a_name_var.set(self._team_a.name)
        self._team_b_name_var.set(self._team_b.name)
        self._col_a._render_all_slots()
        self._col_b._render_all_slots()
        self._refresh_overlay()


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