"""
AgentCard — the widget displayed per agent slot when an agent is selected.
Shows portrait, ability icons with names, ultimate highlighted separately.
A red ✕ button in the top-right allows removal.
"""
from __future__ import annotations
import tkinter as tk
from models.agent import Agent
from ui import theme
from ui.image_loader import agent_portrait, ability_icon
from collections.abc import Callable


class AgentCard(tk.Frame):
    """Rendered cell for one selected agent."""

    def __init__(self, parent: tk.Widget, agent: Agent,
                 on_remove: Callable[[], None], **kwargs):
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

        # ── Left side: portrait + role badge ─────────────────────────────
        portrait_img = agent_portrait(a.id, theme.AGENT_THUMB)
        self._images.append(portrait_img)

        portrait_lbl = tk.Label(self, image=portrait_img, bg=theme.BG_CARD)
        portrait_lbl.grid(row=0, column=0, rowspan=3, padx=(8, 6), pady=8,
                          sticky="nw")

        # Agent name
        name_lbl = tk.Label(self,
                             text=a.display_name,
                             bg=theme.BG_CARD,
                             fg=theme.TEXT_PRIMARY,
                             font=theme.FONT_TITLE,
                             anchor="w")
        name_lbl.grid(row=0, column=1, columnspan=4, sticky="sw", pady=(8, 1))

        # Role badge
        role_color = theme.ROLE_COLORS.get(a.role, theme.TEXT_SECONDARY)
        role_lbl = tk.Label(self,
                             text=a.role.upper(),
                             bg=theme.BG_CARD,
                             fg=role_color,
                             font=theme.FONT_SMALL,
                             anchor="w")
        role_lbl.grid(row=1, column=1, columnspan=4, sticky="nw")

        # ── Abilities row (C, Q, E) ───────────────────────────────────────
        ab_frame = tk.Frame(self, bg=theme.BG_CARD)
        ab_frame.grid(row=2, column=1, columnspan=4, sticky="w", pady=(4, 0))

        for ab in a.basic_abilities:
            self._add_ability_widget(ab_frame, ab, ultimate=False)

        # ── Ultimate row ─────────────────────────────────────────────────
        if a.ultimate:
            ult_frame = tk.Frame(self,
                                  bg=theme.BG_PANEL,
                                  highlightbackground=theme.ACCENT_GOLD,
                                  highlightthickness=1)
            ult_frame.grid(row=3, column=0, columnspan=5,
                           padx=8, pady=(4, 6), sticky="ew")
            self._add_ability_widget(ult_frame, a.ultimate, ultimate=True)

        # Allow column 5 to absorb leftover space (keeps layout stable)
        self.columnconfigure(5, weight=1)

    def _add_ability_widget(self, parent: tk.Frame, ability, ultimate: bool):
        """Create a small icon+label pair inside *parent*."""
        container = tk.Frame(parent,
                              bg=parent.cget("bg"))
        container.pack(side="left", padx=(6 if ultimate else 4), pady=3)

        icon_img = ability_icon(self._agent.id, ability.icon_filename,
                                theme.ABILITY_ICON)
        self._images.append(icon_img)

        icon_lbl = tk.Label(container, image=icon_img,
                             bg=parent.cget("bg"))
        icon_lbl.pack(side="left", padx=(0, 3))

        fg = theme.ACCENT_GOLD if ultimate else theme.TEXT_PRIMARY
        key_lbl = tk.Label(container,
                            text=f"[{ability.key}] {ability.name}",
                            bg=parent.cget("bg"),
                            fg=fg,
                            font=theme.FONT_ABILITY if not ultimate else (theme.FONT_FAMILY, 8, "bold"),
                            anchor="w")
        key_lbl.pack(side="left")