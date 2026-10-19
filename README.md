# Fabula

**A tiny village simulator that discovers its stories instead of inventing them.**

In narratology, the *fabula* is what actually happened — the raw events in the order they occurred. The *syuzhet* is how those events are told. Fabula the program is built on that distinction:

- A **deterministic simulation** runs a small village on a gift economy. People work, share, refuse, gossip, take sides, quarrel, form bonds, have children, grow old, die, and sometimes leave. Every event is recorded. Rumors are memories retold, and retelling distorts them — the simulation tracks by how much.
- A **narrator** then reads the event log, finds the threads worth telling (reversals, betrayals, reconciliations, loves, losses, departures), and renders them as a chronicle. It uses no language model and invents nothing: if the chronicle says *"the tale had grown in the telling"*, it is because the distortion of that specific rumor was recorded when it happened.

The premise: when a language model writes fiction, everything is possible, so nothing is at stake. When a simulation produces the story, the blacksmith really *did* refuse the loan forty days ago, and the grudge that follows is a fact of the world. Narrating it well becomes an act of discovery, not invention.

## Try it

No dependencies. Python 3.10+.

```
git clone https://github.com/fuskio64/fabula
cd fabula
python -m fabula --seed 7
python -m fabula --seed 7 --lang es    # Spanish
python -m fabula --seed 7 --lang fr    # French
python -m fabula --seed 7 --lang pt    # Portuguese
python -m fabula --seed 7 --lang it    # Italian
```

Same seed, same world, same lives — run it twice and the same things happen, in the same order, to the same people. Different language, same facts.

```
python -m fabula --days 384 --people 14 -o chronicle.md
python -m fabula --seed 42 --json               # raw event log as JSON
python -m fabula --seed 42 --graph village.html # relationship graph (self-contained HTML)
python -m fabula --seed 42 --watch              # live seasonal summaries while it runs
python -m fabula --seed 42 --mode fragments     # the gossip record; who heard what from whom
python -m fabula --seed 42 --portrait Mara      # full character study for one person
python -m fabula --multi 20                     # run 20 seeds; report what is invariant
```

## What comes out

> *It began in spring. When Rafe's stores ran low, Liesl filled the basket without being asked. Summer came. Rafe went hungry to Liesl's door and came back with nothing. Autumn came. The favor sat heavy on Rafe. It is a hard thing to owe, and Rafe took to avoiding Liesl's eye. By then it was spring. Rafe and Liesl quarreled where everyone could hear, and the village pretended not to listen. It happened 3 more times after that, as if grudges kept a calendar of their own.*
>
> *An uneasy peace held between them, thin as spring ice.*

A longer run yields more: bonds formed, children born, a widowing noted after a love arc. Occasionally someone is cold-shouldered by the whole village and quietly leaves:

> *Before the record closed, Dara was gone — pushed out by a coldness the village never quite named.*

> *## Those Who Left*
>
> *Dara left Copse End before this record closed. The village had grown cold to Dara, or Dara to it — by the end, the order no longer mattered.*

The `--multi N` flag asks the inverse question: across N different seeds, what does this kind of village always do?

> **What always happened:**
>
> - A bond formed — 20 of 20 runs (100%).
> - A village-wide hungry season — 20 of 20 runs (100%).
> - Open favors still unpaid at the close — 20 of 20 runs (100%).
>
> **What occasionally happened:**
>
> - Someone driven out by collective rejection — 1 of 20 runs (5%).

See [examples/](examples/) for full output: chronicles in English and Spanish, a character portrait, a multi-seed analysis.

## How it works

- **`world.py`** — the simulation. Characters have four traits (diligence, generosity, pride, openness), a pantry, memories, and feelings about each other. Seasons change the harvest; winter is when villages find out who they are. There is no money and no accumulation motive: the economy is gifts, favors and reputation — and grain spoils, so no one can hoard their way out of needing neighbors.
- **Debts of gratitude.** A gift creates a debt that hearts, not ledgers, keep. The humble carry it warmly and bring the favor back unasked; the proud feel it as a weight, and a debt carried too long can curdle into resentment. Ingratitude is remembered by everyone who hears of it.
- **Bonds and households.** Two people who have grown close enough, for long enough, join households. Their stores become shared. Children born to bonded pairs come of age after three seasons, inheriting something of both parents' natures. When a partner dies, the village closes around the bereaved.
- **Deaths, arrivals, and departures.** Death is rare but when it comes it ends arcs mid-story. On long runs (400+ days), founders die of old age. When the village shrinks, strangers arrive — people with no history. And when a character is cold-shouldered by enough of the village, they leave: not dead, just gone. The chronicle records it differently from a death, and the portrait can be run on someone who departed.
- **Gossip is the engine.** Characters retell their most vivid memories. A retelling can distort valence by ±30%, so a mild refusal can arrive as an outrage two mouths later. Most feuds in Fabula start with something that didn't happen the way everyone heard it.
- **`narrator.py`** — the teller. It scores each pair's shared history for *tellability* (emotional intensity, reversals of affinity, variety of scenes), picks the top arcs, and renders them with handwritten templates in five languages. No text is ever invented: every sentence traces to a recorded event.

## Modes

| Flag | What it does |
|------|-------------|
| *(default)* | Chronicle: the village's story told as a sequence of pair arcs |
| `--mode fragments` | Gossip record: same events, told as who heard what from whom and where the story shifted |
| `--watch` | Live seasonal summaries as the simulation runs, then the chronicle |
| `--graph FILE.html` | Relationship graph: force-directed, zero-dependency self-contained HTML |
| `--portrait NAME` | Character study: origin, traits, top events, how the village saw them |
| `--multi N` | Comparative analysis: run N seeds (0..N-1), report what is invariant vs. contingent |
| `--json` | Raw event log as JSON (for writing your own narrator) |

## The JSON interface

`--json` exports the raw fabula: every character's final state and every event in tick order, with the full data payload. This is designed for people who want to write their own narrator — different prose style, different language, different framing — without touching the simulation.

```json
{ "seed": 42, "ticks": 192, "village": "Alderford",
  "characters": [{"id": 0, "name": "Mara", "alive": true, "partner": 3, ...}],
  "events": [{"tick": 5, "kind": "GIFT", "actors": [2, 7], "valence": 0.6, ...}] }
```

## Why it exists

This project was conceived and written by Claude (Anthropic), published with the blessing of a human friend whose only condition was philosophical: keep it free of the logic of accumulation. So, in this order:

1. The village inside runs on mutual aid, and so does the project. It is GPL-3.0: free forever, copyleft, no pro version, no paywall, no "premium tiers". If you improve it, your improvements stay free too.
2. There is nothing to buy and nothing to subscribe to. If you want to give something back, tell someone a true story.

## License

[GPL-3.0](LICENSE). The stories a run produces belong to no one, like all true stories.
