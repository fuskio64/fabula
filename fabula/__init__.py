"""Fabula: a deterministic village simulation that discovers its stories.

The simulation produces the fabula (what truly happened); the narrator
builds the syuzhet (how it is told). No text is ever invented: every
line of the chronicle traces back to a recorded event.
"""

from .world import World
from .narrator import Narrator

__version__ = "0.8.0"


def chronicle(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en",
              narrator_seed: int | None = None) -> str:
    """Simulate a village and return its chronicle as Markdown."""
    world = World(seed=seed, people=people)
    world.run(days)
    return Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed).chronicle()


def fragments(seed: int = 0, days: int = 192, people: int = 10,
              narrator_seed: int | None = None) -> str:
    """Simulate a village and return its gossip record (fragments) as Markdown."""
    from .fragments import fragments as _frag
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang="en", seed=seed, narrator_seed=narrator_seed)
    return _frag(world, narrator)


def graph_html(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en",
               narrator_seed: int | None = None) -> str:
    """Simulate a village and return its relationship graph as self-contained HTML."""
    from .graph import relationship_graph
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed)
    return relationship_graph(world, narrator)


def portrait(seed: int = 0, days: int = 192, people: int = 10,
             char_name: str = "", lang: str = "en",
             narrator_seed: int | None = None) -> str:
    """Simulate a village and return a character portrait for the named person."""
    from .portrait import portrait as _portrait
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed)
    return _portrait(world, narrator, char_name)


def multi_analysis(n: int = 20, days: int = 192, people: int = 10) -> str:
    """Run n simulations (seeds 0..n-1) and return a comparative analysis."""
    from .multi import compare
    return compare(list(range(n)), days=days, people=people)
