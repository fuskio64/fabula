"""The fragments narrator.

Tells what the village carries in memory — not a crafted chronicle of what
happened, but the gossip record: who knew what, from whom, and how much it
changed in the telling. Uses the rumor and memory data the simulation already
tracks.

The chronicle's narrator is omniscient and selective. This narrator is a
village archivist who only knows what was passed on, and who cannot verify
what they've been told against what actually occurred. The records are
honest about that.

Currently English-only.
"""

from .model import TICKS_PER_SEASON, season_index, year_of


_EVENT_DESC = {
    "GIFT":        lambda a, b: f"{a} gave {b} bread",
    "REFUSAL":     lambda a, b: f"{a} turned {b} away empty-handed",
    "QUARREL":     lambda a, b: f"{a} and {b} quarreled openly",
    "INGRATITUDE": lambda a, b: f"{b} turned {a} away — though {a} had filled {b}'s basket once",
    "RESENTMENT":  lambda a, b: f"{a} had grown to resent {b} for a debt never returned",
    "REPAYMENT":   lambda a, b: f"{a} returned what they had owed to {b}",
    "BOND":        lambda a, b: f"{a} and {b} chose each other before the season turned",
    "OFFENSE":     lambda a, b: f"word of {b}'s talk reached {a}",
    "MEDIATION":   lambda a, b: f"{a} and {b} were brought to speak again",
    "WIDOWING":    lambda a, b: f"{a} outlived {b}",
}


def _season_year(tick: int) -> str:
    seasons = ("spring", "summer", "autumn", "winter")
    return f"{seasons[season_index(tick)]}, year {year_of(tick)}"


def _time_gap_prose(delta: int) -> str:
    if delta <= 2:
        return "that same day"
    if delta <= 8:
        return "a few days later"
    if delta <= 20:
        return "some days after"
    if delta < TICKS_PER_SEASON:
        return "a few weeks on"
    if delta < TICKS_PER_SEASON * 2:
        return "a season later"
    return "some time later"


def _distortion_note(prev_val: float, curr_val: float) -> str:
    delta = curr_val - prev_val
    if abs(delta) < 0.05:
        return "The story arrived intact."
    if abs(delta) < 0.18:
        return "The story shifted slightly in the telling."
    # sign flip: the moral of the story reversed
    if prev_val * curr_val < 0:
        if curr_val < 0:
            return "What had been a kindness arrived as a wrong. The meaning had reversed."
        return "What had been a wrong arrived as a kindness. The meaning had reversed."
    if delta > 0.35:
        return "The story had grown considerably in the telling."
    if delta > 0:
        return "Something had been added. The story was larger than when it left."
    if delta < -0.35:
        return "The story had shrunken considerably in the telling."
    return "Something had been lost. The story was smaller than when it left."


def _valence_word(v: float) -> str:
    if v > 0.65:  return "something remarkable"
    if v > 0.35:  return "something good"
    if v > 0.05:  return "a small kindness"
    if v > -0.05: return "something unremarkable"
    if v > -0.35: return "a small wrong"
    if v > -0.65: return "something bad"
    return "something grave"


def _chain_for(world, event_id: int) -> list:
    """Return [(char, memory), ...] for event_id. Firsthand first, then by tick."""
    found = []
    for char in world.chars:
        for m in char.memories:
            if m.event_id == event_id:
                found.append((char, m))
                break  # one memory per char per event
    found.sort(key=lambda x: (0 if x[1].firsthand else 1, x[1].tick))
    return found


def _score(world, ev) -> float:
    eid = ev.data.get("id", -1)
    chain = _chain_for(world, eid)
    secondhand = [(c, m) for c, m in chain if not m.firsthand]
    if not secondhand:
        return 0.0
    char_mem = {c.id: m for c, m in chain}
    drift = sum(
        abs(m.valence - char_mem[m.heard_from].valence)
        for c, m in secondhand
        if m.heard_from is not None and m.heard_from in char_mem
    )
    return len(secondhand) * (1.0 + drift) * abs(ev.valence)


_NOTABLE = {
    "GIFT", "REFUSAL", "QUARREL", "INGRATITUDE",
    "RESENTMENT", "REPAYMENT", "BOND", "OFFENSE", "WIDOWING",
}


def fragments(world, narrator, max_events: int = 5) -> str:
    """Render the village's gossip record as Markdown."""
    village = narrator.village

    candidates = [
        ev for ev in world.events
        if ev.kind in _NOTABLE and len(ev.actors) >= 2
    ]
    chosen = sorted(
        (ev for ev in candidates if _score(world, ev) > 0.0),
        key=lambda ev: -_score(world, ev),
    )[:max_events]

    if not chosen:
        return (
            f"# What {village} Carries\n\n"
            "*The stories in this run did not travel far enough to leave "
            "a fragments record. Try a longer run or more people.*\n"
        )

    parts = [
        f"# What {village} Carries",
        "",
        (
            "*A record of the same events, but as they traveled.*  \n"
            "*The chronicle tells what happened. "
            "This tells what the village remembers — "
            "which is not always the same thing.*"
        ),
        "",
        "---",
        "",
    ]

    for ev in chosen:
        eid = ev.data.get("id", -1)
        a_name = narrator.name(ev.actors[0])
        b_name = narrator.name(ev.actors[1])

        desc = _EVENT_DESC.get(ev.kind, lambda a, b: f"something between {a} and {b}")
        parts.append(f"## Of {a_name} and {b_name}")
        parts.append("")
        parts.append(
            f"*{_season_year(ev.tick).capitalize()}. "
            f"What happened: {desc(a_name, b_name)}.*"
        )
        parts.append("")

        chain = _chain_for(world, eid)
        char_mem = {c.id: m for c, m in chain}
        firsthand = [(c, m) for c, m in chain if m.firsthand]
        secondhand = [(c, m) for c, m in chain if not m.firsthand]

        # Who knew it firsthand
        if not firsthand:
            parts.append(
                "No one who was there left a trace of remembering it."
            )
        elif len(firsthand) == 1:
            c, m = firsthand[0]
            parts.append(
                f"{c.name} was there. "
                f"They remembered it as {_valence_word(m.valence)}."
            )
        else:
            names_str = " and ".join(c.name for c, _ in firsthand)
            val_words = [_valence_word(m.valence) for _, m in firsthand]
            if len(set(val_words)) == 1:
                parts.append(
                    f"Both {names_str} carried it firsthand "
                    f"and both remembered it as {val_words[0]}."
                )
            else:
                remembered = "; ".join(
                    f"{c.name} as {_valence_word(m.valence)}"
                    for c, m in firsthand
                )
                parts.append(
                    f"{names_str} were both there, "
                    f"and they did not remember it the same way: {remembered}."
                )

        # The transmission chain
        if secondhand:
            parts.append("")
            count_word = "one other person" if len(secondhand) == 1 else f"{len(secondhand)} others"
            parts.append(f"It reached {count_word}.")
            parts.append("")

            for c, m in secondhand:
                gap = m.tick - ev.tick
                gap_prose = _time_gap_prose(gap)
                teller_name = (narrator.name(m.heard_from)
                               if m.heard_from is not None else "someone")

                if m.heard_from is not None and m.heard_from in char_mem:
                    prev_val = char_mem[m.heard_from].valence
                    note = _distortion_note(prev_val, m.valence)
                    parts.append(
                        f"{gap_prose.capitalize()}, "
                        f"{c.name} heard it from {teller_name}. "
                        f"{note}"
                    )
                else:
                    parts.append(
                        f"{gap_prose.capitalize()}, "
                        f"{c.name} heard about it — "
                        f"from whom exactly is not recorded. "
                        f"They remembered it as {_valence_word(m.valence)}."
                    )

        # Closing distortion summary
        if secondhand and firsthand:
            first_val = firsthand[0][1].valence
            last_val = secondhand[-1][1].valence
            n = len(secondhand)
            mouth_word = "one telling" if n == 1 else f"{n} tellings"
            drift = abs(last_val - first_val)

            if drift < 0.05:
                summary = f"*{mouth_word.capitalize()}, and the story held.*"
            elif first_val * last_val < 0:
                summary = (
                    f"*{mouth_word.capitalize()}, and the story had turned over. "
                    f"What it was: {_valence_word(first_val)}. "
                    f"What the last ear received: {_valence_word(last_val)}.*"
                )
            else:
                grew = "grew" if last_val > first_val else "shrank"
                summary = (
                    f"*{mouth_word.capitalize()}, and the story {grew}. "
                    f"What it was: {_valence_word(first_val)}. "
                    f"What the last ear received: {_valence_word(last_val)}.*"
                )
            parts.append("")
            parts.append(summary)

        parts += ["", "---", ""]

    parts.append(
        f"*(world seed {world.seed} — "
        "the same run of events, seen through the village's imperfect memory)*"
    )
    parts.append("")

    return "\n".join(parts)
