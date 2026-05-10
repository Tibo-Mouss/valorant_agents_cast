"""
AgentPicker — a scrollable overlay panel that lists all agents.
Greyed-out agents are already on the same team.
Clicking a non-greyed agent calls the on_select callback.
"""
from __future__ import annotations
import tkinter as tk
from models.agent import Agent
from data.agents import ALL_AGENTS
from ui import theme
from ui.image_loader import agent_portrait


class AgentPicker(tk.Frame):
    """
    An overlay panel placed on top of the opposite column.
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

        self._build()

    # ── Build ─────────────────────────────────────────────────────────────

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

        # Scrollable list
        container = tk.Frame(self, bg=theme.BG_OVERLAY)
        container.pack(fill="both", expand=True, padx=4, pady=(0, 6))

        canvas = tk.Canvas(container, bg=theme.BG_OVERLAY,
                            bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical",
                                  command=canvas.yview,
                                  bg=theme.BG_PANEL,
                                  troughcolor=theme.BG_DARK)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=theme.BG_OVERLAY)
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(window_id, width=canvas.winfo_width())

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(window_id, width=e.width))

        # Bind mouse-wheel scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Group agents by role
        roles_order = ["Duelist", "Initiator", "Controller", "Sentinel"]
        by_role: dict[str, list[Agent]] = {r: [] for r in roles_order}
        for agent in sorted(ALL_AGENTS, key=lambda a: a.display_name):
            by_role.setdefault(agent.role, []).append(agent)

        for role in roles_order:
            agents = by_role.get(role, [])
            if not agents:
                continue

            role_color = theme.ROLE_COLORS.get(role, theme.TEXT_SECONDARY)
            tk.Label(inner, text=role.upper(),
                     bg=theme.BG_OVERLAY, fg=role_color,
                     font=(theme.FONT_FAMILY, 8, "bold"),
                     anchor="w").pack(fill="x", padx=8, pady=(6, 2))

            for agent in agents:
                self._make_row(inner, agent)

    def _make_row(self, parent: tk.Frame, agent: Agent):
        is_excluded = agent in self._excluded
        fg = theme.TEXT_DISABLED if is_excluded else theme.TEXT_PRIMARY
        bg_normal = theme.BG_OVERLAY
        bg_hover = theme.BG_HOVER if not is_excluded else theme.BG_OVERLAY

        row = tk.Frame(parent, bg=bg_normal, cursor="hand2" if not is_excluded else "")
        row.pack(fill="x", padx=4, pady=1)

        # Portrait
        img = agent_portrait(agent.id, theme.PICKER_ICON)
        self._images.append(img)

        img_lbl = tk.Label(row, image=img, bg=bg_normal)
        img_lbl.pack(side="left", padx=(4, 8), pady=3)

        # Name + role
        text_frame = tk.Frame(row, bg=bg_normal)
        text_frame.pack(side="left", fill="x", expand=True)

        name_lbl = tk.Label(text_frame, text=agent.display_name,
                             bg=bg_normal, fg=fg, font=theme.FONT_BODY, anchor="w")
        name_lbl.pack(anchor="w")

        role_color = theme.TEXT_DISABLED if is_excluded else theme.ROLE_COLORS.get(agent.role, theme.TEXT_SECONDARY)
        role_lbl = tk.Label(text_frame, text=agent.role,
                             bg=bg_normal, fg=role_color,
                             font=theme.FONT_SMALL, anchor="w")
        role_lbl.pack(anchor="w")

        if is_excluded:
            tk.Label(row, text="✓", bg=bg_normal, fg=theme.TEXT_DISABLED,
                     font=theme.FONT_SMALL).pack(side="right", padx=6)

        # Hover & click only for non-excluded
        if not is_excluded:
            widgets = [row, img_lbl, text_frame, name_lbl, role_lbl]

            def _enter(e, wlist=widgets):
                for w in wlist:
                    w.configure(bg=bg_hover)

            def _leave(e, wlist=widgets):
                for w in wlist:
                    w.configure(bg=bg_normal)

            def _click(e, ag=agent):
                self._on_select(ag)

            for w in widgets:
                w.bind("<Enter>", _enter)
                w.bind("<Leave>", _leave)
                w.bind("<Button-1>", _click)

    def refresh(self, excluded_agents: set[Agent]):
        """Rebuild the picker with an updated exclusion set."""
        self._excluded = excluded_agents
        for child in self.winfo_children():
            child.destroy()
        self._images.clear()
        self._build()