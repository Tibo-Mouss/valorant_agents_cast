"""
Overlay window — fullscreen transparent, agent cards on left/right edges.

The window background uses a chroma-key color (#010101) made fully transparent
via -transparentcolor (Windows) so the game shows through the center.
Each agent card has its own opaque background, keeping the middle clear.

Layout:
  ┌────────────────────────────────────────────────┐
  │ [Team A cards]          (game)  [Team B cards] │
  │  stacked left edge              stacked right  │
  └────────────────────────────────────────────────┘
"""
from __future__ import annotations

import sys
import tkinter as tk
from dataclasses import dataclass
from ctypes import wintypes
import ctypes

from ui import theme
from ui.image_loader import agent_portrait, ability_icon
from translations.locale_manager import locale_manager
from models.team import Team
from models.agent import Agent, Ability

# Color used as the transparent "chroma key" — must not appear in any widget bg
_CHROMA = "#010101"

# Width of each side column (px)
_COL_W = 215

# Portrait thumbnail size
_THUMB = (32, 32)

# Ability icon size
_ICON = (13, 13)

# Role → accent colour mapping (mirrors AgentCard)
_ROLE_COLORS: dict[str, str] = {
    "Duelist":    "#ff6b78",
    "Initiator":  "#6ecf97",
    "Controller": "#c084fc",
    "Sentinel":   "#5db8f7",
}
_ROLE_BG: dict[str, str] = {
    "Duelist":    "#3d1215",
    "Initiator":  "#12301e",
    "Controller": "#251040",
    "Sentinel":   "#0e2438",
}


# ── Screen enumeration ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ScreenInfo:
    name: str
    x: int
    y: int
    width: int
    height: int


def available_screens(root: tk.Tk) -> list[ScreenInfo]:
    """Return detected screens, or a single primary-screen fallback."""
    if sys.platform == "win32":
        screens = _enumerate_windows_screens()
        if screens:
            return screens
    return [ScreenInfo("Screen 1", 0, 0,
                       root.winfo_screenwidth(),
                       root.winfo_screenheight())]


def _enumerate_windows_screens() -> list[ScreenInfo]:
    user32 = ctypes.windll.user32
    monitors: list[ScreenInfo] = []

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left",   wintypes.LONG),
            ("top",    wintypes.LONG),
            ("right",  wintypes.LONG),
            ("bottom", wintypes.LONG),
        ]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize",    wintypes.DWORD),
            ("rcMonitor", RECT),
            ("rcWork",    RECT),
            ("dwFlags",   wintypes.DWORD),
        ]

    MonitorEnumProc = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(RECT),
        wintypes.LPARAM,
    )

    def _callback(hMonitor, hdcMonitor, lprcMonitor, data):
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(info)
        if user32.GetMonitorInfoW(hMonitor, ctypes.byref(info)):
            r = info.rcMonitor
            monitors.append(ScreenInfo(
                name=f"Screen {len(monitors) + 1}",
                x=r.left, y=r.top,
                width=r.right - r.left,
                height=r.bottom - r.top,
            ))
        return True

    try:
        user32.EnumDisplayMonitors(0, 0, MonitorEnumProc(_callback), 0)
    except Exception:
        return []

    return monitors


# ── Overlay window ────────────────────────────────────────────────────────────

class OverlayWindow(tk.Toplevel):
    """
    Frameless fullscreen overlay.

    The root background is set to _CHROMA and made transparent on Windows so
    the game (or desktop) shows through everywhere except the agent cards.
    """

    def __init__(self, parent: tk.Widget, team_a: Team, team_b: Team,
                 screen: ScreenInfo, on_close: callable | None = None):
        super().__init__(parent)
        self.withdraw()

        self._team_a = team_a
        self._team_b = team_b
        self._screen = screen
        self._on_close = on_close

        # Keep tk image references alive
        self._images: list = []

        # ── Window chrome ──────────────────────────────────────────────────
        self.overrideredirect(True)          # no title bar / borders
        self.attributes("-topmost", True)    # always on top
        self.configure(bg=_CHROMA)

        if sys.platform == "win32":
            # Make _CHROMA fully transparent (Windows only)
            self.attributes("-transparentcolor", _CHROMA)
        else:
            # On other platforms fall back to partial alpha
            self.attributes("-alpha", 0.92)

        # ── Position & size ────────────────────────────────────────────────
        self._apply_geometry()

        # ── Build UI ───────────────────────────────────────────────────────
        self._build()

        # ── Close hotkey: Escape ───────────────────────────────────────────
        self.bind("<Escape>", lambda _: self._close())

        # ── Locale subscription ────────────────────────────────────────────
        locale_manager.subscribe(self._refresh)
        self.bind("<Destroy>", lambda _: locale_manager.unsubscribe(self._refresh))

        self.deiconify()

    # ── Geometry ───────────────────────────────────────────────────────────

    def _apply_geometry(self):
        s = self._screen
        self.geometry(f"{s.width}x{s.height}+{s.x}+{s.y}")

    # ── Build ──────────────────────────────────────────────────────────────

    def _build(self):
        """Create the two side columns using place() so the center is clear."""
        # Transparent canvas frame (same as _CHROMA → invisible)
        canvas = tk.Frame(self, bg=_CHROMA)
        canvas.place(relwidth=1.0, relheight=1.0)

        # Close button — top-centre
        tk.Button(
            canvas, text="✕ fermer l'overlay",
            bg="#1a1a1a", fg="#888888",
            activebackground="#ff4655", activeforeground="#ffffff",
            font=(theme.FONT_FAMILY, 9), bd=0, cursor="hand2",
            padx=8, pady=3,
            command=self._close,
        ).place(relx=0.5, y=8, anchor="n")

        # Left column — Team A
        self._left_col = tk.Frame(canvas, bg=_CHROMA)
        self._left_col.place(x=10, y=36, width=_COL_W)

        # Right column — Team B
        self._right_col = tk.Frame(canvas, bg=_CHROMA)
        self._right_col.place(relx=1.0, x=-(10 + _COL_W), y=36, width=_COL_W)

        self._refresh()

    # ── Refresh ────────────────────────────────────────────────────────────

    def _refresh(self):
        """Rebuild both columns (called on init and locale change)."""
        self._images.clear()
        self._build_column(self._left_col,  self._team_a, accent="#ff4655", right=False)
        self._build_column(self._right_col, self._team_b, accent="#3ea9f5", right=True)

    def _build_column(self, col: tk.Frame, team: Team,
                      accent: str, right: bool):
        for child in col.winfo_children():
            child.destroy()

        # Team name label
        tk.Label(
            col,
            text=(team.name or ("Team A" if not right else "Team B")).upper(),
            bg=_CHROMA, fg=accent,
            font=(theme.FONT_FAMILY, 9, "bold"),
            anchor="e" if right else "w",
        ).pack(fill="x", padx=2, pady=(0, 4))

        agents = team.selected_agents()
        if not agents:
            tk.Label(
                col, text="Aucun agent sélectionné",
                bg="#0A0C14", fg="#555555",
                font=(theme.FONT_FAMILY, 9),
            ).pack(fill="x", padx=2, pady=4)
            return

        for agent in agents:
            self._agent_card(col, agent, accent, right)

    # ── Agent card ─────────────────────────────────────────────────────────

    def _agent_card(self, parent: tk.Frame, agent: Agent,
                    team_accent: str, right: bool):
        """One compact card per agent, styled like AgentCard in the main app."""

        # Card frame — opaque dark bg, accent border on the inner edge
        border_kw = (
            {"highlightthickness": 2,
             "highlightbackground": team_accent,
             "highlightcolor": team_accent}
        )
        card = tk.Frame(
            parent, bg="#0A0C14",
            **border_kw,
        )
        card.pack(fill="x", pady=3, padx=0)
        card.columnconfigure(1, weight=1)

        # ── Portrait ───────────────────────────────────────────────────────
        portrait_img = agent_portrait(agent.id, _THUMB)
        self._images.append(portrait_img)

        tk.Label(
            card, image=portrait_img,
            bg="#0A0C14",
        ).grid(row=0, column=0, rowspan=2, padx=(6, 4), pady=6, sticky="nw")

        # ── Name + role ────────────────────────────────────────────────────
        header = tk.Frame(card, bg="#0A0C14")
        header.grid(row=0, column=1, sticky="ew", padx=(0, 6), pady=(6, 1))

        tk.Label(
            header,
            text=agent.display_name,
            bg="#0A0C14", fg="#ffffff",
            font=(theme.FONT_FAMILY, 11, "bold"),
            anchor="w",
        ).pack(side="left")

        role_fg = _ROLE_COLORS.get(agent.role, "#888888")
        role_bg = _ROLE_BG.get(agent.role, "#1a1a1a")

        tk.Label(
            header,
            text=agent.role.upper(),
            bg=role_bg, fg=role_fg,
            font=(theme.FONT_FAMILY, 7, "bold"),
            padx=4, pady=1,
        ).pack(side="left", padx=(6, 0))

        # ── Abilities grid 2×2 ────────────────────────────────────────────
        ab_frame = tk.Frame(card, bg="#0A0C14")
        ab_frame.grid(row=1, column=0, columnspan=2,
                      sticky="ew", padx=6, pady=(0, 6))
        ab_frame.columnconfigure(0, weight=1)
        ab_frame.columnconfigure(1, weight=1)

        abilities = list(agent.abilities)

        for i, ability in enumerate(abilities):
            is_ult = (agent.ultimate and ability.key == agent.ultimate.key)
            row, col = divmod(i, 2)
            self._ability_badge(ab_frame, agent, ability, is_ult, row, col)

    # ── Ability badge ──────────────────────────────────────────────────────

    def _ability_badge(self, parent: tk.Frame, agent: Agent,
                       ability: Ability, ultimate: bool,
                       grid_row: int, grid_col: int):
        """Small icon + name badge placed in a 2×2 grid, gold if ultimate."""

        bg_badge = "#1f1a00" if ultimate else "#131520"
        fg_key   = "#fbbf24" if ultimate else "#7a8099"
        fg_name  = "#fbbf24" if ultimate else "#b0b8d0"
        border   = "#3d3000" if ultimate else "#222535"

        badge = tk.Frame(
            parent, bg=bg_badge,
            highlightbackground=border,
            highlightthickness=1,
        )
        badge.grid(row=grid_row, column=grid_col,
                   sticky="ew", padx=(0, 2), pady=2)

        # Ability icon
        try:
            icon_img = ability_icon(agent.id, ability.icon_filename, _ICON)
            self._images.append(icon_img)
            tk.Label(badge, image=icon_img, bg=bg_badge).pack(
                side="left", padx=(3, 1), pady=2)
        except Exception:
            tk.Label(
                badge, text=ability.key,
                bg=bg_badge, fg=fg_key,
                font=(theme.FONT_FAMILY, 7, "bold"),
                padx=3,
            ).pack(side="left")

        translated = locale_manager.ability_name(
            agent.id, ability.key, fallback=ability.name)

        tk.Label(
            badge,
            text=translated,
            bg=bg_badge, fg=fg_name,
            font=(theme.FONT_FAMILY, 8),
            padx=4, pady=2,
        ).pack(side="left")

    # ── Public API ─────────────────────────────────────────────────────────

    def refresh(self, screen: ScreenInfo | None = None):
        """Call from outside to reposition or redraw (e.g. after locale change)."""
        if screen is not None:
            self._screen = screen
            self._apply_geometry()
        self._refresh()

    # ── Close ──────────────────────────────────────────────────────────────

    def _close(self):
        if self._on_close:
            self._on_close()
        else:
            self.destroy()