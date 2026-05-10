"""
AgentCard — the widget displayed per agent slot when an agent is selected.
Shows portrait, ability icons with names, ultimate highlighted separately.
A red ✕ button in the top-right allows removal.

Layout (grid):
  col 0          col 1 (weight=1)
  ──────────     ──────────────────────────────────────
  portrait  │  row 0: Agent name
  (rowspan) │  row 1: Role badge  |  [E] Signature ability
            │  row 2: [C] ability   [Q] ability
  ──────────────────────────────────────────────────────
  row 3 (colspan): ── Ultimate (full width) ──
"""
from __future__ import annotations
import tkinter as tk
from models.agent import Agent
from ui import theme
from ui.image_loader import agent_portrait, ability_icon


class AgentCard(tk.Frame):
    """Rendered cell for one selected agent."""

    def __init__(self, parent: tk.Widget, agent: Agent,
                 on_remove: callable, **kwargs):
        super().__init__(parent,
                         bg=theme.BG_CARD,
                         highlightbackground=theme.BG_HOVER,
                         highlightthickness=1,
                         **kwargs)
        self._agent = agent
        self._on_remove = on_remove
        self._images: list = []   # keep refs so GC doesn't collect them

        self._build()

    # ── Construction ──────────────────────────────────────────────────────

    def _build(self):
        a = self._agent

        # col 1 stretches to fill available width so ult bar goes edge-to-edge
        self.columnconfigure(1, weight=1)

        # ── Remove button (top-right corner) ─────────────────────────────
        remove_btn = tk.Button(
            self, text="✕",
            bg=theme.BG_CARD, fg=theme.ACCENT_RED,
            activebackground=theme.ACCENT_RED, activeforeground="#ffffff",
            font=theme.FONT_SMALL, bd=0, cursor="hand2",
            command=self._on_remove,
            padx=2, pady=0,
        )
        remove_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)

        # ── Col 0: portrait ──────────────────────────────────────────────
        portrait_img = agent_portrait(a.id, theme.AGENT_THUMB)
        self._images.append(portrait_img)

        portrait_lbl = tk.Label(self, image=portrait_img, bg=theme.BG_CARD)
        portrait_lbl.grid(row=0, column=0, rowspan=3, padx=(8, 6), pady=(8, 4),
                          sticky="nw")

        # ── Row 0: Agent name ─────────────────────────────────────────────
        name_lbl = tk.Label(self,
                             text=a.display_name,
                             bg=theme.BG_CARD,
                             fg=theme.TEXT_PRIMARY,
                             font=theme.FONT_TITLE,
                             anchor="w")
        name_lbl.grid(row=0, column=1, sticky="sw", pady=(8, 1), padx=(0, 6))

        # ── Row 1: Role badge  +  E (signature) ability ───────────────────
        role_row = tk.Frame(self, bg=theme.BG_CARD)
        role_row.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        role_color = theme.ROLE_COLORS.get(a.role, theme.TEXT_SECONDARY)
        tk.Label(role_row,
                 text=a.role.upper(),
                 bg=theme.BG_CARD,
                 fg=role_color,
                 font=theme.FONT_SMALL,
                 anchor="w").pack(side="left")

        # Separator between role and E ability
        tk.Label(role_row, text="  │  ",
                 bg=theme.BG_CARD, fg=theme.TEXT_DISABLED,
                 font=theme.FONT_SMALL).pack(side="left")

        # E ability (signature)
        sig = next((ab for ab in a.abilities if ab.key == "E"), None)
        if sig:
            self._pack_ability_inline(role_row, sig, ultimate=False)

        # ── Row 2: C and Q abilities ──────────────────────────────────────
        cq_frame = tk.Frame(self, bg=theme.BG_CARD)
        cq_frame.grid(row=2, column=1, sticky="w", pady=(3, 0), padx=(0, 6))

        for ab in a.abilities:
            if ab.key in ("C", "Q"):
                self._pack_ability_inline(cq_frame, ab, ultimate=False)

        # ── Row 3: Ultimate — full width ──────────────────────────────────
        if a.ultimate:
            ult_frame = tk.Frame(self,
                                  bg=theme.BG_PANEL,
                                  highlightbackground=theme.ACCENT_GOLD,
                                  highlightthickness=1)
            # columnspan=2 covers portrait col + content col → true full width
            ult_frame.grid(row=3, column=0, columnspan=2,
                           padx=8, pady=(6, 8), sticky="ew")
            self._pack_ability_inline(ult_frame, a.ultimate, ultimate=True)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _pack_ability_inline(self, parent: tk.Frame, ability, ultimate: bool):
        """Pack an icon + key/name label into *parent* (side=left)."""
        bg = parent.cget("bg")

        container = tk.Frame(parent, bg=bg)
        container.pack(side="left", padx=(6 if ultimate else 2), pady=3)

        icon_img = ability_icon(self._agent.id, ability.icon_filename,
                                theme.ABILITY_ICON)
        self._images.append(icon_img)

        tk.Label(container, image=icon_img, bg=bg).pack(side="left", padx=(0, 3))

        fg = theme.ACCENT_GOLD if ultimate else theme.TEXT_PRIMARY
        tk.Label(container,
                 text=f"[{ability.key}] {ability.name}",
                 bg=bg, fg=fg,
                 font=(theme.FONT_FAMILY, 8, "bold") if ultimate else theme.FONT_ABILITY,
                 anchor="w").pack(side="left")