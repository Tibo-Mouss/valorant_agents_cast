"""
Agent model — represents a single Valorant agent with all ability metadata.
"""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Ability:
    """A single agent ability."""
    key: str          # e.g. "Q", "E", "C", "X"
    name: str         # e.g. "Paranoia"
    description: str  # Short cast description
    icon_filename: str  # filename inside assets/abilities/{agent_id}/


@dataclass
class Agent:
    """Represents a Valorant agent."""
    id: str                    # snake_case identifier, e.g. "omen"
    display_name: str          # e.g. "Omen"
    role: str                  # "Duelist", "Controller", "Initiator", "Sentinel"
    abilities: list[Ability] = field(default_factory=list)  # C, Q, E, X order

    @property
    def portrait_path(self) -> Path:
        """Path to the agent portrait image."""
        return Path("assets") / "agents" / f"{self.id}.png"

    @property
    def ultimate(self) -> Ability | None:
        """Returns the X (ultimate) ability."""
        for ab in self.abilities:
            if ab.key == "X":
                return ab
        return None

    @property
    def basic_abilities(self) -> list[Ability]:
        """Returns non-ultimate abilities (C, Q, E)."""
        return [ab for ab in self.abilities if ab.key != "X"]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Agent):
            return self.id == other.id
        return False