"""Character portrait: a single person's story in full.

`portrait(world, narrator, name)` returns a Markdown document focused on one
character — their traits, the significant moments they lived through, how the
village saw them at the close of the record, and if they died, what was left.
"""

from .model import TICKS_PER_SEASON, season_index, year_of


_EVENT_LINES = {
    "GIFT":        (lambda ev, cid, w: f"gave {w.char([a for a in ev.actors if a != cid][0]).name} bread"
                    if ev.actors[0] == cid
                    else f"received bread from {w.char([a for a in ev.actors if a != cid][0]).name}"),
    "REFUSAL":     (lambda ev, cid, w: f"turned {w.char([a for a in ev.actors if a != cid][0]).name} away empty-handed"
                    if ev.actors[0] == cid
                    else f"was turned away by {w.char([a for a in ev.actors if a != cid][0]).name}"),
    "QUARREL":     (lambda ev, cid, w: f"quarreled with {w.char([a for a in ev.actors if a != cid][0]).name}"),
    "BOND":        (lambda ev, cid, w: f"bonded with {w.char([a for a in ev.actors if a != cid][0]).name}"),
    "WIDOWING":    (lambda ev, cid, w: f"outlived {w.char([a for a in ev.actors if a != cid][0]).name}"
                    if ev.actors[0] == cid else ""),
    "INGRATITUDE": (lambda ev, cid, w: f"closed the door on {w.char([a for a in ev.actors if a != cid][0]).name} — though they had once given"
                    if ev.actors[0] == cid
                    else f"was turned away by {w.char([a for a in ev.actors if a != cid][0]).name}, after having helped them"),
    "RESENTMENT":  (lambda ev, cid, w: f"came to resent {w.char([a for a in ev.actors if a != cid][0]).name} for a debt that curdled"),
    "REPAYMENT":   (lambda ev, cid, w: f"returned what was owed to {w.char([a for a in ev.actors if a != cid][0]).name}, without being asked"
                    if ev.actors[0] == cid
                    else f"received back what was owed by {w.char([a for a in ev.actors if a != cid][0]).name}"),
    "MEDIATION":   (lambda ev, cid, w: f"was brought back to speaking terms with {w.char([a for a in ev.actors if a != cid][0]).name}"
                    if cid in ev.actors[:2] else ""),
    "OFFENSE":     (lambda ev, cid, w: f"took offense at what {w.char([a for a in ev.actors if a != cid][0]).name} had been saying"
                    if ev.actors[0] == cid else ""),
    "DEATH":       (lambda ev, cid, w: f"died ({ev.data.get('cause', '').replace('_', ' ')})"),
    "COMING_OF_AGE": (lambda ev, cid, w: "came of age in the village"),
}


def portrait(world, narrator, char_name: str) -> str:
    char = next(
        (c for c in world.chars if c.name.lower() == char_name.lower()), None
    )
    if char is None:
        return (
            f"# No record of {char_name}\n\n"
            f"*No character by that name was found in {narrator.village} "
            f"(seed {world.seed}).*\n"
        )

    village = narrator.village
    adjs = narrator.adjectives(char)
    adj_str = " and ".join(adjs)

    if not char.alive:
        if char.departed:
            status = "left the village"
        else:
            cause = narrator.death_cause(char.id)
            status = f"died ({cause.replace('_', ' ')})" if cause else "dead"
    elif char.elder:
        status = "living, elder"
    elif char.childhood:
        status = "living, still a child"
    else:
        status = "living"

    if char.parent_ids:
        origin = f"born in {village}"
    elif char.joined_at > 0:
        origin = f"arrived in {village} as a stranger"
    else:
        origin = f"founder of {village}"

    def _cap(s: str) -> str:
        return s[0].upper() + s[1:] if s else s

    parts = [f"# {char.name}", "", f"*{_cap(origin)}. {_cap(adj_str)}. {_cap(status)}.*", ""]

    # --- Traits section ---
    trait_notes = []
    if char.diligence > 0.65:
        trait_notes.append("tireless in the fields — the kind of person who works without being watched")
    elif char.diligence < 0.35:
        trait_notes.append("not known for their industry; other things occupied them")
    if char.generosity > 0.65:
        trait_notes.append("open-handed, with a surplus or without")
    elif char.generosity < 0.35:
        trait_notes.append("reluctant to give; not cruel, but counted their stores")
    if char.pride > 0.65:
        trait_notes.append("proud — the kind of person who would rather go hungry than ask")
    elif char.pride < 0.35:
        trait_notes.append("not proud; could receive help without it costing them something")
    if char.openness > 0.65:
        trait_notes.append("talkative, always the first to know what was being said")
    elif char.openness < 0.35:
        trait_notes.append("reserved; kept what they knew to themselves")

    if trait_notes:
        parts.append("## Character")
        parts.append("")
        for note in trait_notes:
            parts.append(f"- {note.capitalize()}.")
        parts.append("")

    # --- Significant events ---
    _SKIP = {"RUMOR", "FESTIVAL", "HARVEST", "LEAN_SEASON", "BOUNTY",
             "HARDSHIP", "MISFORTUNE", "ARRIVAL", "DEPARTURE"}
    involved = [
        ev for ev in world.events
        if char.id in ev.actors and ev.kind not in _SKIP
    ]
    # Group by (kind, other_id) — keep the most valenced event per pair-interaction
    # so "quarreled with X 5 times" collapses into one entry
    groups: dict = {}
    for ev in involved:
        others = [a for a in ev.actors if a != char.id]
        other_id = others[0] if others else -1
        key = (ev.kind, other_id)
        if key not in groups or abs(ev.valence) > abs(groups[key].valence):
            groups[key] = ev
    top = sorted(groups.values(), key=lambda e: -abs(e.valence))[:7]
    top_sorted = sorted(top, key=lambda e: e.tick)

    if top_sorted:
        parts.append("## What Happened")
        parts.append("")
        seasons = ("spring", "summer", "autumn", "winter")
        for ev in top_sorted:
            when = f"{seasons[season_index(ev.tick)]}, year {year_of(ev.tick)}"
            fn = _EVENT_LINES.get(ev.kind)
            if fn is None:
                continue
            desc = fn(ev, char.id, world)
            if desc:
                parts.append(f"- *{when.capitalize()}:* {desc}.")
        parts.append("")

    # --- How the village saw them ---
    living_others = [c for c in world.chars if c.id != char.id and c.alive]
    if living_others:
        avg_in = sum(c.feel(char.id) for c in living_others) / len(living_others)
        avg_out = sum(char.feel(c.id) for c in living_others) / len(living_others)

        if avg_in > 0.3:
            regard = "warmly regarded by those still living"
        elif avg_in > 0.05:
            regard = "regarded well enough"
        elif avg_in > -0.1:
            regard = "regarded with neither warmth nor coldness"
        elif avg_in > -0.3:
            regard = "regarded with some suspicion"
        else:
            regard = "poorly regarded by most of the village"

        parts.append("## How the Village Saw Them")
        parts.append("")
        if not char.alive and char.departed:
            parts.append(f"At the time {char.name} left, they were {regard}.")
        else:
            parts.append(f"At the close of this record, {char.name} was {regard}.")

        # closest and most estranged
        def mutual(c):
            return (c.feel(char.id) + char.feel(c.id)) / 2

        best = max(living_others, key=mutual)
        worst = min(living_others, key=mutual)
        best_val = mutual(best)
        worst_val = mutual(worst)

        if best_val > 0.25 and char.partner != best.id:
            parts.append(f"Closest to {best.name}.")
        if worst_val < -0.15:
            parts.append(f"Most estranged from {worst.name}.")

        if avg_out < -0.05 and abs(avg_in - avg_out) > 0.15:
            if avg_out < avg_in:
                parts.append(
                    f"They held others in colder regard than the village held them — "
                    f"a common asymmetry in people who have been disappointed."
                )
            else:
                parts.append(
                    f"They thought better of their neighbors than their neighbors thought of them."
                )
        parts.append("")

    # --- Bond and family ---
    bond_lines = []
    if char.partner is not None:
        partner = world.char(char.partner)
        line = f"Bonded with {partner.name}"
        if not partner.alive:
            line += " — now widowed"
        bond_lines.append(line + ".")
    elif any(ev.kind == "BOND" and char.id in ev.actors for ev in world.events):
        bond_lines.append("Was once bonded; their partner did not outlive them.")

    children = [c for c in world.chars if c.parent_ids and char.id in c.parent_ids]
    if children:
        names = ", ".join(c.name for c in children)
        bond_lines.append(f"{'Parent' if len(children) == 1 else 'Parent'} of {names}.")

    if bond_lines:
        parts += bond_lines + [""]

    # --- Debts ---
    debt_lines = []
    if char.debts:
        cred = [narrator.name(d.creditor) for d in char.debts.values()]
        debt_lines.append(f"Still owed {'a favor' if len(cred) == 1 else 'favors'} to {', '.join(cred)}.")
    owed_by = [c for c in world.chars if char.id in c.debts]
    if owed_by:
        names = ", ".join(c.name for c in owed_by)
        debt_lines.append(
            f"{names} still {'owed' if len(owed_by) == 1 else 'owed'} "
            f"{'a favor' if len(owed_by) == 1 else 'favors'} to {char.name}."
        )
    if debt_lines:
        parts += debt_lines + [""]

    # --- Death/departure legacy ---
    if not char.alive:
        if char.departed:
            legacy = narrator.death_legacy(char.id)
            if legacy:
                parts += ["## What the Village Lost", "", legacy, ""]
        else:
            legacy = narrator.death_legacy(char.id)
            if legacy:
                parts += ["## What Was Left", "", legacy, ""]

    parts.append(f"*(world seed {world.seed} · {narrator.village})*")
    parts.append("")
    return "\n".join(parts)
