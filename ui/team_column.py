"""
TeamColumn — manages the UI for one team:
  • Team name input
  • 5 agent slot rows (empty or occupied by AgentCard)
  • Bookmark button reference for active-state reset when picker closes
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
    get_opposite_frame: callable → the other team's container Frame
                        (picker is placed on top of it)
    """

    def __init__(self, parent: tk.Widget,
                 side: str,
                 team: Team,
                 get_opposite_frame: callable,
                 show_team_name: bool = True,
                 **kwargs):
        super().__init__(parent, bg=theme.BG_PANEL, **kwargs)
        self._side = side
        self._team = team
        self._get_opposite_frame = get_opposite_frame
        self._picker: AgentPicker | None = None
        self._slot_frames: list[tk.Frame] = []
        self._show_team_name = show_team_name
        # Injected by App after both columns exist
        self._bookmark: tk.Widget | None = None

        self._build()

    # ── Public: let App wire the bookmark reference ───────────────────────

    def set_bookmark(self, bookmark):
        """Give this column a reference to its BookmarkButton."""
        self._bookmark = bookmark

    # ── Construction ──────────────────────────────────────────────────────

    def _build(self):
        # ── Team name input ───────────────────────────────────────────────
        if self._show_team_name:
            name_row = tk.Frame(self, bg=theme.BG_PANEL)
            name_row.pack(fill="x", padx=10, pady=(10, 6))

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
        else:
            # Create the StringVar anyway so it can be accessed by App
            self._name_var = tk.StringVar(value=self._team.name)
            self._name_var.trace_add("write",
                                      lambda *_: setattr(self._team, "name",
                                                         self._name_var.get()))

        # ── Agent slots ───────────────────────────────────────────────────
        slots_container = tk.Frame(self, bg=theme.BG_PANEL)
        slots_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for i in range(MAX_AGENTS):
            # The slot wrapper must NOT shrink — we enforce card height on it
            slot = tk.Frame(slots_container, bg=theme.BG_PANEL,
                             height=theme.CARD_HEIGHT)
            slot.pack(fill="x", pady=3)
            slot.pack_propagate(False)   # keep fixed height regardless of content
            self._slot_frames.append(slot)
            self._render_slot(i)

    # ── Slot rendering ────────────────────────────────────────────────────

    def _render_slot(self, index: int):
        """Render slot *index* — empty placeholder or AgentCard."""
        slot = self._slot_frames[index]
        for child in slot.winfo_children():
            child.destroy()

        agent = self._team.agents[index]

        if agent is None:
            placeholder = tk.Frame(slot,
                                    bg=theme.BG_CARD,
                                    highlightbackground=theme.BG_HOVER,
                                    highlightthickness=1)
            placeholder.place(relx=0, rely=0, relwidth=1, relheight=1)

            tk.Label(placeholder,
                     text=f"— slot {index + 1} —",
                     bg=theme.BG_CARD,
                     fg=theme.TEXT_DISABLED,
                     font=theme.FONT_SMALL).place(relx=0.5, rely=0.5, anchor="center")
        else:
            card = AgentCard(slot, agent,
                              on_remove=lambda idx=index: self._remove_agent(idx))
            card.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _render_all_slots(self):
        for i in range(MAX_AGENTS):
            self._render_slot(i)

    # ── Agent management ──────────────────────────────────────────────────

    def _add_agent(self, agent: Agent):
        if self._team.is_full():
            return
        self._team.add_agent(agent)
        self._render_all_slots()
        if self._picker and self._picker.winfo_exists():
            self._picker.refresh(set(self._team.selected_agents()))

    def _remove_agent(self, index: int):
        agent = self._team.agents[index]
        self._remove_agent_obj(agent)

    def _remove_agent_obj(self, agent: Agent | None):
        if agent and self._team.remove_agent(agent):
            self._render_all_slots()
            if self._picker and self._picker.winfo_exists():
                self._picker.refresh(set(self._team.selected_agents()))

    # ── Picker (bookmark) ────────────────────────────────────────────────

    def open_picker(self):
        """Toggle the agent picker over the opposite column."""
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
        # Reset the bookmark button back to inactive state
        if self._bookmark is not None:
            self._bookmark.deactivate()

    def _on_picker_select(self, agent: Agent):
        if self._team.has_agent(agent):
            self._remove_agent_obj(agent)
        else:
            self._add_agent(agent)

        if self._team.is_full() and not self._team.has_agent(agent):
            self._close_picker()