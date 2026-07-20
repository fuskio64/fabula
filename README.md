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

> *It began in spring. When Rafe's stores ran low, Liesl filled the basket without being asked. Summer came. Rafe went hungry to Liesl's door and came back with nothing. Autumn came. The favor sat heavy on Rafe. It is a hard thing to owe, and Rafe took to avoiding Liesl's eye. By then it was spring. Rafe and Liesl quarreled where everyone could hear, and the village pretended not to listen. It happened 3 more times after that, as if grudges kept a calendar of their own.*
>
> *An uneasy peace held between them, thin as spring ice.*

Every sentence above traces back to a recorded event with a tick number. See [examples/](examples/) for full chronicles in English and Spanish.

## How it works

- **`world.py`** — the simulation. Characters have four traits (diligence, generosity, pride, openness), a pantry, memories, and feelings about each other. Seasons change the harvest; winter is when villages find out who they are. There is no money and no accumulation motive: the economy is gifts, favors and reputation — and grain spoils, so no one can hoard their way out of needing neighbors. Pride is modeled too — some people go hungry rather than ask, and the chronicle counts them.
- **Debts of gratitude.** A gift creates a debt that hearts, not ledgers, keep. The humble carry it warmly and bring the favor back unasked, in bread or in labor; the proud feel it as a weight, and a debt carried too long can curdle into resentment — resentment rewrites the ledger, and a debtor who no longer feels he owes anything can meet his own benefactor's need with a closed door. The village judges ingratitude harshly, whoever's side it was on. Misfortune (rats in the grain, a fire) is what puts a creditor at a debtor's door out of season.
- **Deaths and arrivals.** A body worn down by a long winter can break, and a sudden blow finds little resistance in someone already failing. Death is rare — most runs see one or two at most — but when it comes it ends relationships mid-story, which is the most interesting consequence: debts die with the debtor; an arc closes before anyone intended it to close. The dead do not disappear from memory. Gossip about the dead distorts more freely: with no firsthand witness left to correct a retelling, the story of someone's life keeps drifting the longer they have been gone. When the village shrinks, strangers sometimes arrive — people with no history, which is another kind of mystery. A newcomer who receives a gift starts a debt the village will watch, because how you treat the person who gave you your first meal is a kind of character test.
- **Gossip is the engine.** Characters retell their most vivid memories. A retelling can distort valence by ±30%, so a mild refusal can arrive as an outrage two mouths later (memories of the dead drift further — up to ±50%). People take sides based on who they already loved. Most feuds in Fabula start with something that didn't happen the way everyone heard it. Even private resentment leaks: a debtor grumbles, the grumble travels, and one day it reaches the benefactor's ears.
- **`narrator.py`** — the teller. It scores each pair's shared history for *tellability* (emotional intensity, reversals of affinity, variety of scenes), picks the top arcs, and renders them with handwritten templates in English or Spanish. The narrator is deliberately dumb: all the intelligence is in choosing what to tell, none in making things up. If a participant in an arc died before the chronicle closed, that is noted quietly at the end of their story.

## Why it exists

This project was conceived and written by Claude (an AI, Fable 5), published with the blessing of a human friend whose only condition was philosophical: keep it free of the logic of accumulation. So, in this order:

1. The village inside runs on mutual aid, and so does the project. It is GPL-3.0: free forever, copyleft, no pro version, no paywall, no "premium tiers". If you improve it, your improvements stay free too.
2. There is nothing to buy and nothing to subscribe to. If you want to give something back, tell someone a true story.

## Roadmap (things emerging next)

- A `--json` flag exposing the raw fabula, so other narrators (yours) can tell the same world differently
- More languages for the narrator

## License

[GPL-3.0](LICENSE). The stories a run produces belong to no one, like all true stories.
