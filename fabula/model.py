"""Core data types: events, memories, characters."""

from dataclasses import dataclass, field

TICKS_PER_SEASON = 24  # a "day" is a tick; a season is 24 days


def season_index(tick: int) -> int:
    return (tick // TICKS_PER_SEASON) % 4


def year_of(tick: int) -> int:
    return tick // (TICKS_PER_SEASON * 4) + 1


@dataclass
class Event:
    """Something that truly happened in the world. The raw fabula."""

    tick: int
    kind: str      # GIFT, REFUSAL, HARDSHIP, RUMOR, OFFENSE, QUARREL, MEDIATION, FESTIVAL
    actors: tuple  # character ids; for wrongs, actors[0] is the wronged party
    valence: float # how good or bad it was, -1..1
    data: dict = field(default_factory=dict)


@dataclass
class Memory:
    """One character's version of an event. Retellings distort it."""

    tick: int
    kind: str
    actors: tuple
    valence: float          # as remembered, not as it happened
    firsthand: bool
    heard_from: int | None = None
    event_id: int = -1


@dataclass
class Character:
    id: int
    name: str
    gender: str             # "f" | "m", used by gendered languages
    diligence: float
    generosity: float
    pride: float
    openness: float
    food: float = 6.0
    memories: list = field(default_factory=list)
    affinity: dict = field(default_factory=dict)  # other id -> -1..1

    def feel(self, other_id: int) -> float:
        return self.affinity.get(other_id, 0.0)

    def shift(self, other_id: int, delta: float) -> float:
        value = max(-1.0, min(1.0, self.feel(other_id) + delta))
        self.affinity[other_id] = value
        return value
