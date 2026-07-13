import argparse
import random
import sys

from . import chronicle


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
    parser.add_argument("--lang", choices=("en", "es"), default="en",
                        help="language of the chronicle")
    parser.add_argument("-o", "--out", default=None,
                        help="write the chronicle to a file instead of stdout")
    args = parser.parse_args(argv)

    seed = args.seed if args.seed is not None else random.randrange(1_000_000)
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
