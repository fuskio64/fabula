import argparse
import random
import sys

from . import chronicle, World
from .names import VILLAGE_NAMES


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
    parser.add_argument("--lang", choices=("en", "es", "fr", "pt"), default="en",
                        help="language of the chronicle")
    parser.add_argument("--json", action="store_true",
                        help="output raw event log as JSON instead of a narrative chronicle")
    parser.add_argument("-o", "--out", default=None,
                        help="write the output to a file instead of stdout")
    args = parser.parse_args(argv)

    seed = args.seed if args.seed is not None else random.randrange(1_000_000)

    if args.json:
        import json as _json
        w = World(seed=seed, people=args.people)
        w.run(args.days)
        narrator_rng = random.Random(seed ^ 0xFAB)
        village = narrator_rng.choice(VILLAGE_NAMES.get(args.lang, VILLAGE_NAMES["en"]))
        data = {
            "seed": seed,
            "ticks": w.tick,
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
                for c in w.chars
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
                for ev in w.events
            ],
        }
        text = _json.dumps(data, indent=2, ensure_ascii=False)
    else:
        text = chronicle(seed=seed, days=args.days, people=args.people, lang=args.lang)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
