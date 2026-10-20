import argparse
import random
import sys
import time

from . import World
from .narrator import Narrator
from .names import VILLAGE_NAMES


def _ansi(code: str, text: str) -> str:
    """Wrap text in an ANSI code, but only when writing to a real terminal."""
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def _watch_run(world: World, days: int, lang: str = "en"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    """Run the simulation interactively, printing a seasonal summary each season."""
    from .model import TICKS_PER_SEASON, season_index, year_of
    from .narrator import TEXT

    _t = TEXT.get(lang, TEXT["en"])
    raw_seasons = _t["seasons"]
    seasons = tuple(s[0].upper() + s[1:] for s in raw_seasons)
    season_events: list = []

    for tick in range(days):
        # record events before the step
        prev_count = len(world.events)
        world.step()
        new_events = world.events[prev_count:]
        season_events.extend(new_events)

        if (tick + 1) % TICKS_PER_SEASON != 0:
            continue

        # end of season — print summary
        s = season_index(tick)
        y = year_of(tick)
        header = f"\n  {seasons[s]}, year {y}"
        print(_ansi("33", header))

        deaths = [ev for ev in season_events if ev.kind == "DEATH"]
        births = [ev for ev in season_events if ev.kind == "BIRTH"]
        bonds  = [ev for ev in season_events if ev.kind == "BOND"]
        quarrels = [ev for ev in season_events if ev.kind == "QUARREL"]
        gifts  = [ev for ev in season_events if ev.kind == "GIFT"]
        ingrat = [ev for ev in season_events if ev.kind == "INGRATITUDE"]

        alive = sum(1 for c in world.chars if c.alive)
        hungry = sum(1 for c in world.chars if c.alive and c.food < 2.0)

        status = f"  {alive} souls"
        if hungry:
            status += _ansi("31", f"  ·  {hungry} hungry")
        print(status)

        for ev in deaths:
            c = world.char(ev.actors[0])
            cause = ev.data.get("cause", "")
            cause_note = {"starvation": "hunger", "misfortune": "sudden blow",
                          "old_age": "old age"}.get(cause, cause)
            print(_ansi("31", f"  * {c.name} died ({cause_note})"))
        for ev in births:
            child = world.char(ev.actors[0])
            pa = world.char(ev.actors[1]).name
            pb = world.char(ev.actors[2]).name
            print(_ansi("32", f"  * {child.name} born to {pa} and {pb}"))
        for ev in bonds:
            a, b = world.char(ev.actors[0]).name, world.char(ev.actors[1]).name
            print(_ansi("32", f"  * {a} and {b} bonded"))
        for ev in ingrat:
            a, b = world.char(ev.actors[0]).name, world.char(ev.actors[1]).name
            print(_ansi("31", f"  * {a} turned {b} away — though {b} had given first"))
        if quarrels and not deaths:
            ev = quarrels[0]
            a, b = world.char(ev.actors[0]).name, world.char(ev.actors[1]).name
            note = f"  * {a} and {b} quarreled"
            if len(quarrels) > 1:
                note += f" (and {len(quarrels) - 1} other quarrel{'s' if len(quarrels) > 2 else ''})"
            print(_ansi("33", note))
        if gifts and not births and not bonds:
            print(_ansi("32", f"  * {len(gifts)} gift{'s' if len(gifts) > 1 else ''} given"))

        season_events = []
        time.sleep(0.18)

    print()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="fabula",
        description="Simulate a village; tell what truly happened in it.")
    parser.add_argument("--seed", type=int, default=None,
                        help="world seed (random if omitted)")
    parser.add_argument("--days", type=int, default=192,
                        help="days to simulate (a season is 24 days)")
    parser.add_argument("--people", type=int, default=10,
                        help="souls in the village")
    parser.add_argument("--lang", choices=("en", "es", "fr", "pt", "it"), default="en",
                        help="language of the chronicle")
    parser.add_argument("--narrator-seed", type=int, default=None,
                        help="seed for narrative choices (village name, template variants); "
                             "same world, different voice")
    parser.add_argument("--mode", choices=("chronicle", "fragments", "years", "cast", "timeline", "stats", "seeds"), default="chronicle",
                        help="output mode: chronicle (default), fragments, years (logbook), cast (register), timeline (lifespan chart), stats (metrics dashboard), or seeds (story prompts)")
    parser.add_argument("--json", action="store_true",
                        help="output raw event log as JSON instead of a narrative chronicle")
    parser.add_argument("--watch", action="store_true",
                        help="run the simulation live with seasonal summaries, then output the chronicle")
    parser.add_argument("--graph", metavar="FILE", default=None,
                        help="write a relationship graph to this HTML file (use - for stdout)")
    parser.add_argument("--portrait", metavar="NAME", default=None,
                        help="write a portrait of a character by name and exit")
    parser.add_argument("--multi", metavar="N", type=int, default=None,
                        help="run N simulations (seeds 0..N-1) and report what is invariant")
    parser.add_argument("-o", "--out", default=None,
                        help="write the chronicle/JSON output to a file instead of stdout")
    args = parser.parse_args(argv)

    # --multi: run N seeds independently and compare
    if args.multi is not None:
        from .multi import compare as _compare
        seeds = list(range(args.multi))
        text = _compare(seeds, days=args.days, people=args.people)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            sys.stdout.write(text)
        return

    seed = args.seed if args.seed is not None else random.randrange(1_000_000)

    # --- build the world ---
    world = World(seed=seed, people=args.people)

    if args.watch and not args.json:
        _watch_run(world, args.days, lang=args.lang)
    else:
        world.run(args.days)

    # --portrait: character study for one named person
    if args.portrait is not None:
        from .portrait import portrait as _portrait
        lang = args.lang if not args.json else "en"
        narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=args.narrator_seed)
        text = _portrait(world, narrator, args.portrait)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            sys.stdout.write(text)
        return

    # --- produce text output ---
    if args.json:
        import json as _json
        nseed = args.narrator_seed if args.narrator_seed is not None else (seed ^ 0xFAB)
        narrator_rng = random.Random(nseed)
        village = narrator_rng.choice(VILLAGE_NAMES.get(args.lang, VILLAGE_NAMES["en"]))
        data = {
            "seed": seed,
            "ticks": world.tick,
            "lang": args.lang,
            "village": village,
            "characters": [
                {
                    "id": c.id,
                    "name": c.name,
                    "gender": c.gender,
                    "alive": c.alive,
                    "diligence": round(c.diligence, 4),
                    "generosity": round(c.generosity, 4),
                    "pride": round(c.pride, 4),
                    "openness": round(c.openness, 4),
                    "food": round(c.food, 2),
                    "partner": c.partner,
                    "parent_ids": list(c.parent_ids) if c.parent_ids else None,
                    "childhood": c.childhood,
                    "died_at": c.died_at,
                    "affinity": {str(k): round(v, 3) for k, v in c.affinity.items()},
                }
                for c in world.chars
            ],
            "events": [
                {
                    "id": ev.data["id"],
                    "tick": ev.tick,
                    "kind": ev.kind,
                    "actors": list(ev.actors),
                    "valence": round(ev.valence, 3),
                    "data": {k: v for k, v in ev.data.items() if k != "id"},
                }
                for ev in world.events
            ],
        }
        text = _json.dumps(data, indent=2, ensure_ascii=False)

    elif args.mode == "fragments":
        from .fragments import fragments as _frag
        narrator = Narrator(world, lang=args.lang, seed=seed, narrator_seed=args.narrator_seed)
        text = _frag(world, narrator)

    elif args.mode == "years":
        from .yearly import yearly as _yearly
        narrator = Narrator(world, lang=args.lang, seed=seed, narrator_seed=args.narrator_seed)
        text = _yearly(world, narrator)

    elif args.mode == "cast":
        from .cast import cast as _cast
        narrator = Narrator(world, lang=args.lang, seed=seed, narrator_seed=args.narrator_seed)
        text = _cast(world, narrator)

    elif args.mode == "timeline":
        from .timeline import timeline as _timeline
        narrator = Narrator(world, lang=args.lang, seed=seed, narrator_seed=args.narrator_seed)
        text = _timeline(world, narrator)

    elif args.mode == "stats":
        from .stats import stats as _stats
        narrator = Narrator(world, lang=args.lang, seed=seed, narrator_seed=args.narrator_seed)
        text = _stats(world, narrator)

    elif args.mode == "seeds":
        from .seeds import story_seeds as _seeds
        narrator = Narrator(world, lang=args.lang, seed=seed, narrator_seed=args.narrator_seed)
        text = _seeds(world, narrator)

    else:
        lang = args.lang if args.lang in ("en", "es", "fr", "pt", "it") else "en"
        narrator = Narrator(world, lang=lang, seed=seed, narrator_seed=args.narrator_seed)
        text = narrator.chronicle()

    # --- write text output ---
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(text)

    # --- write relationship graph ---
    if args.graph:
        from .graph import relationship_graph
        lang = args.lang if not args.json else "en"
        if args.mode == "fragments" or args.json:
            # need a narrator for the graph even if we didn't make one above
            _nseed = args.narrator_seed
            gr_narrator = Narrator(world, lang="en", seed=seed, narrator_seed=_nseed)
        else:
            gr_narrator = narrator  # type: ignore[possibly-undefined]
        graph_html = relationship_graph(world, gr_narrator)
        if args.graph == "-":
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            sys.stdout.write(graph_html)
        else:
            with open(args.graph, "w", encoding="utf-8") as f:
                f.write(graph_html)


if __name__ == "__main__":
    main()
