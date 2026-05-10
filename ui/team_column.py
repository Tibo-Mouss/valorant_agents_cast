"""
TeamColumn — manages the UI for one team:
  • Team name input
  • 5 agent slot rows (empty or occupied by AgentCard)
  • Bookmark button that opens/closes the AgentPicker overlay
"""
from __future__ import annotations
import tkinter as tk
from models.agent import Agent
from models.team import Team, MAX_AGENTS
from ui import theme
from ui.agent_card import AgentCard
from ui.agent_picker import AgentPicker


class TeamColumn(tk.Frame):
    """
    side: "left" | "right"
    get_other_team: callable that returns the other Team instance
                    (used only to prevent cross-column duplicate check if desired)
    """

    def __init__(self, parent: tk.Widget,
                 side: str,
                 team: Team,
                 get_opposite_frame: callable,
                 **kwargs):
        super().__init__(parent, bg=theme.BG_PANEL, **kwargs)
        self._side = side          # "left" or "right"
        self._team = team
        self._get_opposite_frame = get_opposite_frame
        self._picker: AgentPicker | None = None
        self._slot_frames: list[tk.Frame] = []

        self._build()

    # ── Construction ──────────────────────────────────────────────────────

    def _build(self):
        # ── Team name input ───────────────────────────────────────────────
        name_row = tk.Frame(self, bg=theme.BG_PANEL)
        name_row.pack(fill="x", padx=10, pady=(10, 6))

        label_text = "TEAM A" if self._side == "left" else "TEAM B"
        tk.Label(name_row, text=label_text,
                 bg=theme.BG_PANEL, fg=theme.ACCENT_RED,
                 font=(theme.FONT_FAMILY, 8, "bold")).pack(anchor="w")

        self._name_var = tk.StringVar(value=self._team.name)
        self._name_var.trace_add("write",
                                  lambda *_: setattr(self._team, "name",
                                                     self._name_var.get()))
        name_entry = tk.Entry(name_row,
                               textvariable=self._name_var,
                               bg=theme.BG_INPUT,
                               fg=theme.TEXT_PRIMARY,
                               insertbackground=theme.TEXT_PRIMARY,
                               relief="flat",
                               font=theme.FONT_TITLE,
                               bd=4)
        name_entry.pack(fill="x", ipady=4)

        # ── Agent slots ───────────────────────────────────────────────────
        slots_container = tk.Frame(self, bg=theme.BG_PANEL)
        slots_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for i in range(MAX_AGENTS):
            slot = tk.Frame(slots_container, bg=theme.BG_PANEL)
            slot.pack(fill="x", pady=3)
            self._slot_frames.append(slot)
            self._render_slot(i)

    # ── Slot rendering ────────────────────────────────────────────────────

    def _render_slot(self, index: int):
        """Render slot *index* — either an empty placeholder or an AgentCard."""
        slot = self._slot_frames[index]
        # Clear current content
        for child in slot.winfo_children():
            child.destroy()

        agent = self._team.agents[index]

        if agent is None:
            # Empty placeholder
            placeholder = tk.Frame(slot,
                                    bg=theme.BG_CARD,
                                    height=theme.CARD_HEIGHT,
                                    highlightbackground=theme.BG_HOVER,
                                    highlightthickness=1)
            placeholder.pack(fill="x")
            placeholder.pack_propagate(False)

            tk.Label(placeholder,
                     text=f"— slot {index + 1} —",
                     bg=theme.BG_CARD,
                     fg=theme.TEXT_DISABLED,
                     font=theme.FONT_SMALL).place(relx=0.5, rely=0.5, anchor="center")
        else:
            card = AgentCard(slot, agent,
                              on_remove=lambda idx=index: self._remove_agent(idx))
            card.pack(fill="x")

    def _render_all_slots(self):
        for i in range(MAX_AGENTS):
            self._render_slot(i)

    # ── Agent management ──────────────────────────────────────────────────

    def _add_agent(self, agent: Agent):
        if self._team.is_full():
            return
        self._team.add_agent(agent)
        self._render_all_slots()
        # Refresh picker exclusions (agent is now selected)
        if self._picker and self._picker.winfo_exists():
            self._picker.refresh(set(self._team.selected_agents()))

    def _remove_agent(self, index: int):
        agent = self._team.agents[index]
        if agent:
            self._team.remove_agent(agent)
        self._render_slot(index)
        if self._picker and self._picker.winfo_exists():
            self._picker.refresh(set(self._team.selected_agents()))

    # ── Picker (bookmark) ────────────────────────────────────────────────

    def open_picker(self):
        """Open the agent picker over the opposite column."""
        if self._picker and self._picker.winfo_exists():
            self._close_picker()
            return

        opposite = self._get_opposite_frame()

        self._picker = AgentPicker(
            opposite,
            excluded_agents=set(self._team.selected_agents()),
            on_select=self._on_picker_select,
            on_close=self._close_picker,
        )
        self._picker.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._picker.lift()

    def _close_picker(self):
        if self._picker and self._picker.winfo_exists():
            self._picker.destroy()
        self._picker = None

    def _on_picker_select(self, agent: Agent):
        self._add_agent(agent)
        if self._team.is_full():
            self._close_picker()