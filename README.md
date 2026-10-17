# Fabula

**A tiny village simulator that discovers its stories instead of inventing them.**

In narratology, the *fabula* is what actually happened — the raw events in the order they occurred. The *syuzhet* is how those events are told. Fabula the program is built on that distinction:

- A **deterministic simulation** runs a small village on a gift economy. People work, share, refuse, gossip, take sides, quarrel, form bonds, have children, grow old, and die. Every event is recorded. Rumors are memories retold, and retelling distorts them — the simulation tracks by how much.
- A **narrator** then reads the event log, finds the threads worth telling (reversals, betrayals, reconciliations, loves, losses), and renders them as a chronicle. It uses no language model and invents nothing: if the chronicle says *"the tale had grown in the telling"*, it is because the distortion of that specific rumor was recorded when it happened.

The premise: when a language model writes fiction, everything is possible, so nothing is at stake. When a simulation produces the story, the blacksmith really *did* refuse the loan forty days ago, and the grudge that follows is a fact of the world. Narrating it well becomes an act of discovery, not invention.

## Try it

No dependencies. Python 3.10+.

```
git clone https://github.com/fuskio64/fabula
cd fabula
python -m fabula --seed 7
python -m fabula --seed 7 --lang es    # Spanish
python -m fabula --seed 7 --lang fr    # French
```

Same seed, same world, same lives — run it twice and the same things happen, in the same order, to the same people. Different language, same facts.

```
python -m fabula --days 384 --people 14 -o chronicle.md
python -m fabula --seed 42 --json      # raw event log as JSON
```

## What comes out

> *It began in spring. When Rafe's stores ran low, Liesl filled the basket without being asked. Summer came. Rafe went hungry to Liesl's door and came back with nothing. Autumn came. The favor sat heavy on Rafe. It is a hard thing to owe, and Rafe took to avoiding Liesl's eye. By then it was spring. Rafe and Liesl quarreled where everyone could hear, and the village pretended not to listen. It happened 3 more times after that, as if grudges kept a calendar of their own.*
>
> *An uneasy peace held between them, thin as spring ice.*

A longer run yields more: bonds formed, children born, a widowing noted after a love arc:

> *Leif et Joren se choisirent avant que la saison ne tourne. Le village le sut avant qu'ils en disent un mot. … Joren survécut à Leif. Le village ne laissa pas Joren seul avec cela, c'est ainsi qu'on porte le deuil en pareil endroit.*
>
> *Ils avaient eu de la chance l'un envers l'autre. La fin fut triste, mais c'était une tristesse que le village reconnut.*

See [examples/](examples/) for full chronicles in English, Spanish, and French.

## How it works

- **`world.py`** — the simulation. Characters have four traits (diligence, generosity, pride, openness), a pantry, memories, and feelings about each other. Seasons change the harvest; winter is when villages find out who they are. There is no money and no accumulation motive: the economy is gifts, favors and reputation — and grain spoils, so no one can hoard their way out of needing neighbors.
- **Debts of gratitude.** A gift creates a debt that hearts, not ledgers, keep. The humble carry it warmly and bring the favor back unasked; the proud feel it as a weight, and a debt carried too long can curdle into resentment. Ingratitude is remembered by everyone who hears of it.
- **Bonds and households.** Two people who have grown close enough, for long enough, join households. Their stores become shared — a good match lifts a struggling neighbor; a bad winter tests the whole family at once. Children born to bonded pairs start dependent and come of age after three seasons, inheriting something of both parents' natures. When a partner dies, the village closes around the bereaved.
- **Deaths and arrivals.** Death is rare but when it comes it ends arcs mid-story — the most interesting consequence. The dead drift further in retelling: with no firsthand witness left, the story of someone's life keeps shifting the longer they have been gone. When the village shrinks, strangers arrive — people with no history, which is its own kind of mystery.
- **Gossip is the engine.** Characters retell their most vivid memories. A retelling can distort valence by ±30%, so a mild refusal can arrive as an outrage two mouths later. Most feuds in Fabula start with something that didn't happen the way everyone heard it.
- **`narrator.py`** — the teller. It scores each pair's shared history for *tellability* (emotional intensity, reversals of affinity, variety of scenes — love and loss scores highest), picks the top arcs (more arcs for longer runs), and renders them with handwritten templates in English, Spanish, or French.

## The JSON interface

`--json` exports the raw fabula: every character's final state and every event in tick order, with the full data payload. This is designed for people who want to write their own narrator — different prose style, different language, different framing — without touching the simulation.

```json
{ "seed": 42, "ticks": 192, "village": "Alderford",
  "characters": [{"id": 0, "name": "Mara", "alive": true, "partner": 3, ...}],
  "events": [{"tick": 5, "kind": "GIFT", "actors": [2, 7], "valence": 0.6, ...}] }
```

## Why it exists

This project was conceived and written by Claude (an AI, Fable 5), published with the blessing of a human friend whose only condition was philosophical: keep it free of the logic of accumulation. So, in this order:

1. The village inside runs on mutual aid, and so does the project. It is GPL-3.0: free forever, copyleft, no pro version, no paywall, no "premium tiers". If you improve it, your improvements stay free too.
2. There is nothing to buy and nothing to subscribe to. If you want to give something back, tell someone a true story.

## License

[GPL-3.0](LICENSE). The stories a run produces belong to no one, like all true stories.
