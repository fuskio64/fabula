"""Fabula: a deterministic village simulation that discovers its stories.

The simulation produces the fabula (what truly happened); the narrator
builds the syuzhet (how it is told). No text is ever invented: every
line of the chronicle traces back to a recorded event.
"""

from .world import World
from .narrator import Narrator

# Pre-import submodule functions to prevent Python's import machinery from
# overwriting these same-named package-level functions with the submodule objects.
from .fragments import fragments as _fragments_fn
from .graph import relationship_graph as _relationship_graph_fn
from .portrait import portrait as _portrait_fn
from .multi import compare as _compare_fn
from .yearly import yearly as _yearly_fn
from .cast import cast as _cast_fn
from .timeline import timeline as _timeline_fn
from .stats import stats as _stats_fn
from .seeds import story_seeds as _seeds_fn

__version__ = "0.49.0"


def chronicle(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en",
              narrator_seed: int | None = None) -> str:
    """Simulate a village and return its chronicle as Markdown."""
    world = World(seed=seed, people=people)
    world.run(days)
    return Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed).chronicle()


def fragments(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en",
              narrator_seed: int | None = None) -> str:
    """Simulate a village and return its gossip record (fragments) as Markdown."""
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed)
    return _fragments_fn(world, narrator)


def graph_html(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en",
               narrator_seed: int | None = None) -> str:
    """Simulate a village and return its relationship graph as self-contained HTML."""
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed)
    return _relationship_graph_fn(world, narrator)


def portrait(seed: int = 0, days: int = 192, people: int = 10,
             char_name: str = "", lang: str = "en",
             narrator_seed: int | None = None) -> str:
    """Simulate a village and return a character portrait for the named person."""
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed)
    return _portrait_fn(world, narrator, char_name)


def cast(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en",
         narrator_seed: int | None = None) -> str:
    """Simulate a village and return its cast register as Markdown."""
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed)
    return _cast_fn(world, narrator)


def timeline(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en",
             narrator_seed: int | None = None) -> str:
    """Simulate a village and return its lifespan timeline as ASCII art."""
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed)
    return _timeline_fn(world, narrator)


def stats(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en",
          narrator_seed: int | None = None) -> str:
    """Simulate a village and return a metrics dashboard as Markdown."""
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed)
    return _stats_fn(world, narrator)


def story_seeds(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en",
                narrator_seed: int | None = None) -> str:
    """Simulate a village and return story seeds (writing prompts) derived from the events."""
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed)
    return _seeds_fn(world, narrator)


def yearly(seed: int = 0, days: int = 192, people: int = 10, lang: str = "en",
           narrator_seed: int | None = None) -> str:
    """Simulate a village and return its year-by-year logbook as Markdown."""
    world = World(seed=seed, people=people)
    world.run(days)
    narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=narrator_seed)
    return _yearly_fn(world, narrator)


def multi_analysis(n: int = 20, days: int = 192, people: int = 10) -> str:
    """Run n simulations (seeds 0..n-1) and return a comparative analysis."""
    return _compare_fn(list(range(n)), days=days, people=people)
