"""
AgentPicker — an overlay panel showing all agents in a 3-column grid.

Agents already on the team are greyed-out (not clickable).
Selecting an agent calls on_select without rebuilding the whole widget —
only the affected cell is updated, eliminating the flicker.
"""
from __future__ import annotations
import tkinter as tk
from models.agent import Agent
from data.agents import ALL_AGENTS
from ui import theme
from ui.image_loader import agent_portrait

# Columns in the agent grid
GRID_COLS = 3


class AgentPicker(tk.Frame):
    """
    Overlay panel placed on top of the opposite column.
    Parent is responsible for placing/removing it.
    """

    def __init__(self, parent: tk.Widget,
                 excluded_agents: set[Agent],
                 on_select: callable,
                 on_close: callable,
                 **kwargs):
        super().__init__(parent,
                         bg=theme.BG_OVERLAY,
                         highlightbackground=theme.ACCENT_RED,
                         highlightthickness=1,
                         **kwargs)
        self._excluded = excluded_agents
        self._on_select = on_select
        self._on_close = on_close
        self._images: list = []
        # Map agent.id → AgentTile so we can update them without rebuilding
        self._tiles: dict[str, "_AgentTile"] = {}

        self._build()

    # ── Build (called once) ───────────────────────────────────────────────

    def _build(self):
        # Header
        header = tk.Frame(self, bg=theme.BG_OVERLAY)
        header.pack(fill="x", padx=8, pady=(8, 4))

        tk.Label(header, text="SELECT AGENT",
                 bg=theme.BG_OVERLAY, fg=theme.ACCENT_RED,
                 font=theme.FONT_TITLE).pack(side="left")

        tk.Button(header, text="✕",
                  bg=theme.BG_OVERLAY, fg=theme.TEXT_SECONDARY,
                  activebackground=theme.ACCENT_RED, activeforeground="#fff",
                  font=theme.FONT_BODY, bd=0, cursor="hand2",
                  command=self._on_close).pack(side="right")

        # Scrollable canvas
        container = tk.Frame(self, bg=theme.BG_OVERLAY)
        container.pack(fill="both", expand=True, padx=4, pady=(0, 6))

        self._canvas = tk.Canvas(container, bg=theme.BG_OVERLAY,
                                  bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical",
                                  command=self._canvas.yview,
                                  bg=theme.BG_PANEL,
                                  troughcolor=theme.BG_DARK)
        self._canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=theme.BG_OVERLAY)
        self._win_id = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse-wheel — bind to canvas only (not all widgets) to avoid side effects
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind("<Enter>",
                          lambda e: self._canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self._canvas.bind("<Leave>",
                          lambda e: self._canvas.unbind_all("<MouseWheel>"))

        # Populate grid
        self._populate_grid()

    def _on_inner_configure(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._win_id, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ── Grid population ───────────────────────────────────────────────────

    def _populate_grid(self):
        """Build the 3-column grid of agent tiles grouped by role."""
        roles_order = ["Duelist", "Initiator", "Controller", "Sentinel"]
        by_role: dict[str, list[Agent]] = {r: [] for r in roles_order}
        for agent in sorted(ALL_AGENTS, key=lambda a: a.display_name):
            by_role.setdefault(agent.role, []).append(agent)

        # Make all 3 grid columns equal weight so tiles share space evenly
        for c in range(GRID_COLS):
            self._inner.columnconfigure(c, weight=1, uniform="agcol")

        current_row = 0
        for role in roles_order:
            agents = by_role.get(role, [])
            if not agents:
                continue

            # Role header — spans all columns
            role_color = theme.ROLE_COLORS.get(role, theme.TEXT_SECONDARY)
            tk.Label(self._inner, text=role.upper(),
                     bg=theme.BG_OVERLAY, fg=role_color,
                     font=(theme.FONT_FAMILY, 8, "bold"),
                     anchor="w").grid(row=current_row, column=0,
                                      columnspan=GRID_COLS,
                                      sticky="ew", padx=8, pady=(8, 2))
            current_row += 1

            # Agent tiles — 3 per row
            for i, agent in enumerate(agents):
                col = i % GRID_COLS
                if col == 0 and i != 0:
                    current_row += 1

                tile = _AgentTile(
                    self._inner,
                    agent=agent,
                    excluded=agent in self._excluded,
                    on_click=self._handle_select,
                )
                tile.grid(row=current_row, column=col,
                          padx=3, pady=3, sticky="ew")
                self._tiles[agent.id] = tile
                # Store image ref in tile; tile keeps its own list

            current_row += 1   # advance past the last tiles row

    # ── Public API ────────────────────────────────────────────────────────

    def refresh(self, excluded_agents: set[Agent]):
        """
        Update the excluded state of each tile WITHOUT rebuilding the whole widget.
        This prevents the flicker that a full destroy/rebuild would cause.
        """
        self._excluded = excluded_agents
        for agent_id, tile in self._tiles.items():
            should_be_excluded = any(a.id == agent_id for a in excluded_agents)
            tile.set_excluded(should_be_excluded)

    def _handle_select(self, agent: Agent):
        self._on_select(agent)


# ── AgentTile ─────────────────────────────────────────────────────────────

class _AgentTile(tk.Frame):
    """
    A single agent cell inside the picker grid.
    Supports toggling the greyed-out (excluded) state in-place.
    """

    def __init__(self, parent: tk.Widget, agent: Agent,
                 excluded: bool, on_click: callable, **kwargs):
        super().__init__(parent, bg=theme.BG_OVERLAY,
                         cursor="" if excluded else "hand2", **kwargs)
        self._agent = agent
        self._excluded = excluded
        self._on_click = on_click
        self._images: list = []

        self._bg_normal = theme.BG_OVERLAY
        self._bg_hover = theme.BG_HOVER

        self._build()
        self._apply_state()

    def _build(self):
        img = agent_portrait(self._agent.id, theme.PICKER_ICON)
        self._images.append(img)

        self._img_lbl = tk.Label(self, image=img, bg=self._bg_normal)
        self._img_lbl.pack(pady=(6, 2))

        self._name_lbl = tk.Label(self,
                                   text=self._agent.display_name,
                                   bg=self._bg_normal,
                                   fg=theme.TEXT_PRIMARY,
                                   font=theme.FONT_SMALL,
                                   wraplength=80,
                                   justify="center")
        self._name_lbl.pack(pady=(0, 4))

        # Checkmark overlay (visible only when excluded)
        self._check_lbl = tk.Label(self, text="✓",
                                    bg=self._bg_normal,
                                    fg=theme.TEXT_DISABLED,
                                    font=(theme.FONT_FAMILY, 9, "bold"))

        self._all_widgets = [self, self._img_lbl, self._name_lbl]

        for w in self._all_widgets:
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_click_evt)

    def _apply_state(self):
        """Apply current excluded/active visual state."""
        fg = theme.TEXT_DISABLED if self._excluded else theme.TEXT_PRIMARY
        cursor = "" if self._excluded else "hand2"

        self._name_lbl.configure(fg=fg)
        self.configure(cursor=cursor)

        if self._excluded:
            self._check_lbl.place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)
        else:
            self._check_lbl.place_forget()

    def set_excluded(self, excluded: bool):
        """Update excluded state in-place — no widget rebuild."""
        if self._excluded == excluded:
            return
        self._excluded = excluded
        self._apply_state()

    def _on_enter(self, event):
        if not self._excluded:
            for w in self._all_widgets:
                w.configure(bg=self._bg_hover)
            self._name_lbl.configure(bg=self._bg_hover)
            self._check_lbl.configure(bg=self._bg_hover)

    def _on_leave(self, event):
        for w in self._all_widgets:
            w.configure(bg=self._bg_normal)
        self._name_lbl.configure(bg=self._bg_normal)
        self._check_lbl.configure(bg=self._bg_normal)

    def _on_click_evt(self, event):
        if not self._excluded:
            self._on_click(self._agent)