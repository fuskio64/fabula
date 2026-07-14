"""Fabula: a deterministic village simulation that discovers its stories.

The simulation produces the fabula (what truly happened); the narrator
builds the syuzhet (how it is told). No text is ever invented: every
line of the chronicle traces back to a recorded event.
"""

from .world import World
from .narrator import Narrator

__version__ = "0.2.0"


def chronicle(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en") -> str:
    """Simulate a village and return its chronicle as Markdown."""
    world = World(seed=seed, people=people)
    world.run(days)
    return Narrator(world, lang=lang, seed=seed).chronicle()
