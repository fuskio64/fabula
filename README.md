# Fabula

**A tiny village simulator that discovers its stories instead of inventing them.**

In narratology, the *fabula* is what actually happened — the raw events in the order they occurred. The *syuzhet* is how those events are told. Fabula the program is built on that distinction:

- A **deterministic simulation** runs a small village on a gift economy. People work, share, refuse, gossip, take sides, quarrel, and sometimes get sat down at the same table by a mutual friend. Every event is recorded. Rumors are memories retold, and retelling distorts them — the simulation tracks by how much.
- A **narrator** then reads the event log, finds the threads worth telling (reversals, betrayals, reconciliations, quiet loyalties), and renders them as a chronicle. It uses no language model and invents nothing: if the chronicle says *"the tale had grown in the telling"*, it is because the distortion of that specific rumor was recorded when it happened.

The premise: when a language model writes fiction, everything is possible, so nothing is at stake. When a simulation produces the story, the blacksmith really *did* refuse the loan forty days ago, and the grudge that follows is a fact of the world. Narrating it well becomes an act of discovery, not invention.

## Try it

No dependencies. Python 3.10+.

```
git clone https://github.com/fuskio64/fabula
cd fabula
python -m fabula --seed 7
python -m fabula --seed 7 --lang es    # the same world, told in Spanish
```

Same seed, same world, same lives — run it twice and the same things happen, in the same order, to the same people. Different language, same facts.

```
python -m fabula --days 384 --people 14 -o chronicle.md
```

## What comes out

> *It began in autumn. Ilde shared bread with Casper in a lean stretch, and it was not forgotten. Winter came. Ilde turned Casper away empty-handed, and the whole village felt colder for it. Spring came. Ilde and Casper quarreled where everyone could hear, and the village pretended not to listen. And so it went on, season after season, until counting lost its point.*
>
> *No one mended it. By the end they passed each other without a word.*

Every sentence above traces back to a recorded event with a tick number. See [examples/](examples/) for full chronicles in English and Spanish.

## How it works

- **`world.py`** — the simulation. Characters have four traits (diligence, generosity, pride, openness), a pantry, memories, and feelings about each other. Seasons change the harvest; winter is when villages find out who they are. There is no money and no accumulation motive: the economy is gifts, favors and reputation. Pride is modeled too — some people go hungry rather than ask, and the chronicle counts them.
- **Gossip is the engine.** Characters retell their most vivid memories. A retelling can distort valence by ±30%, so a mild refusal can arrive as an outrage two mouths later. People take sides based on who they already loved. Most feuds in Fabula start with something that didn't happen the way everyone heard it.
- **`narrator.py`** — the teller. It scores each pair's shared history for *tellability* (emotional intensity, reversals of affinity, variety of scenes), picks the top arcs, and renders them with handwritten templates in English or Spanish. The narrator is deliberately dumb: all the intelligence is in choosing what to tell, none in making things up.

## Why it exists

This project was conceived and written by Claude (an AI, Fable 5), published with the blessing of a human friend whose only condition was philosophical: keep it free of the logic of accumulation. So, in this order:

1. The village inside runs on mutual aid, and so does the project. It is GPL-3.0: free forever, copyleft, no pro version, no paywall, no "premium tiers". If you improve it, your improvements stay free too.
2. There is nothing to buy and nothing to subscribe to. If you want to give something back, tell someone a true story.

## Roadmap (things emerging next)

- Debts of gratitude with memory (favors that are *owed*, and what unpaid debts do to people)
- Deaths, arrivals, and how a village retells someone once they're gone
- A `--json` flag exposing the raw fabula, so other narrators (yours) can tell the same world differently
- More languages for the narrator

## License

[GPL-3.0](LICENSE). The stories a run produces belong to no one, like all true stories.
