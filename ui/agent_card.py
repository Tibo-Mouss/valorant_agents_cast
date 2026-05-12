"""
AgentCard — the widget displayed per agent slot when an agent is selected.

Ability name labels are backed by tk.StringVar so they update instantly
when the locale changes — no widget rebuild required.

Layout (grid):
  col 0          col 1 (weight=1)
  ──────────     ──────────────────────────────────────
  portrait  │  row 0: Agent name
  (rowspan) │  row 1: Role badge  │  [E] Signature ability
            │  row 2: [C] ability    [Q] ability
  ──────────────────────────────────────────────────────
  row 3 (colspan): ── Ultimate (full width) ──
"""
from __future__ import annotations
import tkinter as tk
from models.agent import Agent, Ability
from ui import theme
from ui.image_loader import agent_portrait, ability_icon
from translations.locale_manager import locale_manager


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
        self._images: list = []

        # One StringVar per ability key — set on locale change without rebuilding
        self._ability_vars: dict[str, tk.StringVar] = {}

        self._build()

        # Subscribe; unsubscribe automatically when this widget is destroyed
        locale_manager.subscribe(self._on_locale_change)
        self.bind("<Destroy>", lambda e: locale_manager.unsubscribe(self._on_locale_change))

    # ── Construction ──────────────────────────────────────────────────────

    def _build(self):
        a = self._agent
        self.columnconfigure(1, weight=1)

        # ── Remove button ─────────────────────────────────────────────────
        tk.Button(
            self, text="✕",
            bg=theme.BG_CARD, fg=theme.ACCENT_RED,
            activebackground=theme.ACCENT_RED, activeforeground="#ffffff",
            font=theme.FONT_SMALL, bd=0, cursor="hand2",
            command=self._on_remove, padx=2, pady=0,
        ).place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)

        # ── Col 0: portrait ───────────────────────────────────────────────
        portrait_img = agent_portrait(a.id, theme.AGENT_THUMB)
        self._images.append(portrait_img)
        tk.Label(self, image=portrait_img, bg=theme.BG_CARD).grid(
            row=0, column=0, rowspan=3, padx=(8, 6), pady=(8, 4), sticky="nw")

        # ── Row 0: Agent name ─────────────────────────────────────────────
        tk.Label(self, text=a.display_name, bg=theme.BG_CARD,
                 fg=theme.TEXT_PRIMARY, font=theme.FONT_TITLE, anchor="w").grid(
            row=0, column=1, sticky="sw", pady=(8, 1), padx=(0, 6))

        # ── Row 1: Role badge + │ + E ability ────────────────────────────
        role_row = tk.Frame(self, bg=theme.BG_CARD)
        role_row.grid(row=1, column=1, sticky="ew", padx=(0, 6))

        role_color = theme.ROLE_COLORS.get(a.role, theme.TEXT_SECONDARY)
        tk.Label(role_row, text=a.role.upper(), bg=theme.BG_CARD,
                 fg=role_color, font=theme.FONT_SMALL, anchor="w").pack(side="left")

        tk.Label(role_row, text="  │  ", bg=theme.BG_CARD,
                 fg=theme.TEXT_DISABLED, font=theme.FONT_SMALL).pack(side="left")

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
            ult_frame = tk.Frame(self, bg=theme.BG_PANEL,
                                  highlightbackground=theme.ACCENT_GOLD,
                                  highlightthickness=1)
            ult_frame.grid(row=3, column=0, columnspan=2,
                           padx=8, pady=(6, 8), sticky="ew")
            self._pack_ability_inline(ult_frame, a.ultimate, ultimate=True)

    # ── Widget factory ────────────────────────────────────────────────────

    def _pack_ability_inline(self, parent: tk.Frame, ability: Ability,
                              ultimate: bool):
        """Create icon + translatable label packed left into *parent*."""
        bg = parent.cget("bg")

        container = tk.Frame(parent, bg=bg)
        container.pack(side="left", padx=(6 if ultimate else 2), pady=3)

        icon_img = ability_icon(self._agent.id, ability.icon_filename,
                                theme.ABILITY_ICON)
        self._images.append(icon_img)
        tk.Label(container, image=icon_img, bg=bg).pack(side="left", padx=(0, 3))

        # StringVar so the label text updates without any widget rebuild
        var = tk.StringVar(value=self._label_text(ability))
        self._ability_vars[ability.key] = var

        fg = theme.ACCENT_GOLD if ultimate else theme.TEXT_PRIMARY
        font = theme.FONT_ULTIMATE if ultimate else theme.FONT_ABILITY
        tk.Label(container, textvariable=var, bg=bg, fg=fg,
                 font=font, anchor="w").pack(side="left")

    # ── Locale ────────────────────────────────────────────────────────────

    def _label_text(self, ability: Ability) -> str:
        """Build the display string for *ability* in the current locale."""
        name = locale_manager.ability_name(
            self._agent.id, ability.key, fallback=ability.name)
        return f"[{ability.key}] {name}"

    def _on_locale_change(self):
        """Called by LocaleManager when the user picks a different language."""
        for ab in self._agent.abilities:
            var = self._ability_vars.get(ab.key)
            if var is not None:
                var.set(self._label_text(ab))