"""
Team model — holds up to 5 agents and a team name.
"""
from models.agent import Agent

MAX_AGENTS = 5


class Team:
    """Represents one of the two teams in a Valorant match."""

    def __init__(self, name: str = ""):
        self.name: str = name
        self._agents: list[Agent | None] = [None] * MAX_AGENTS

    @property
    def agents(self) -> list[Agent | None]:
        return list(self._agents)

    def add_agent(self, agent: Agent) -> bool:
        """Add agent to first empty slot. Returns True on success."""
        if self.has_agent(agent):
            return False
        for i, slot in enumerate(self._agents):
            if slot is None:
                self._agents[i] = agent
                return True
        return False  # Team is full

    def remove_agent(self, agent: Agent) -> bool:
        """Remove agent from team, then compact remaining agents.
        Returns True on success."""
        for i, slot in enumerate(self._agents):
            if slot == agent:
                self._agents[i] = None
                self._compact()
                return True
        return False

    def _compact(self) -> None:
        selected = [a for a in self._agents if a is not None]
        self._agents = selected + [None] * (MAX_AGENTS - len(selected))

    def has_agent(self, agent: Agent) -> bool:
        return agent in self._agents

    def is_full(self) -> bool:
        return all(slot is not None for slot in self._agents)

    def selected_agents(self) -> list[Agent]:
        return [a for a in self._agents if a is not None]

    def swap_with(self, other: "Team") -> None:
        """Swap name and agents with another team."""
        self.name, other.name = other.name, self.name
        self._agents, other._agents = other._agents, self._agents