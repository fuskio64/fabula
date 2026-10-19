"""Multi-seed analysis: what is invariant, what is contingent.

`compare(seeds, days, people)` runs the same simulation with different seeds
and asks: what does this kind of village always do? What only sometimes happens?
What is rare?

The chronicle tells one story. This tells you the shape of all stories.
"""

from .world import World


def _pct(n: int, total: int) -> str:
    return f"{round(100 * n / total)}%" if total else "—"


def _avg(vals: list) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def _word_fraction(k: int, n: int) -> str:
    if n == 0:
        return "never"
    p = k / n
    if p == 1.0:
        return "always"
    if p >= 0.9:
        return "almost always"
    if p >= 0.7:
        return "usually"
    if p >= 0.5:
        return "often"
    if p >= 0.3:
        return "sometimes"
    if p >= 0.1:
        return "occasionally"
    return "rarely"


def compare(seeds: list, days: int = 192, people: int = 10) -> str:
    """Run simulations for each seed and return a comparative analysis."""
    n = len(seeds)
    if n == 0:
        return "# No runs to compare.\n"

    worlds = []
    for seed in seeds:
        w = World(seed=seed, people=people)
        w.run(days)
        worlds.append(w)

    # --- per-run counts ---
    def count(worlds, kind):
        return [sum(1 for ev in w.events if ev.kind == kind) for w in worlds]

    def count_if(worlds, kind, pred):
        return [sum(1 for ev in w.events if ev.kind == kind and pred(ev)) for w in worlds]

    deaths   = count(worlds, "DEATH")
    bonds    = count(worlds, "BOND")
    births   = count(worlds, "BIRTH")
    quarrels = count(worlds, "QUARREL")
    mediations = count(worlds, "MEDIATION")
    ingrats  = count(worlds, "INGRATITUDE")
    resentments = count(worlds, "RESENTMENT")
    gifts    = count(worlds, "GIFT")
    refusals = count(worlds, "REFUSAL")
    repays   = count(worlds, "REPAYMENT")
    lean     = count(worlds, "LEAN_SEASON")
    bounty   = count(worlds, "BOUNTY")
    arrivals = count(worlds, "ARRIVAL")
    departures = count(worlds, "DEPARTURE")
    pride_hardships = count_if(
        worlds, "HARDSHIP", lambda ev: ev.data.get("pride", False)
    )
    old_age_deaths = count_if(
        worlds, "DEATH", lambda ev: ev.data.get("cause") == "old_age"
    )

    # --- binary (did it happen at all) ---
    def at_least_one(counts):
        return sum(1 for c in counts if c > 0)

    b_death   = at_least_one(deaths)
    b_bond    = at_least_one(bonds)
    b_birth   = at_least_one(births)
    b_quarrel = at_least_one(quarrels)
    b_mediation = at_least_one(mediations)
    b_ingrat  = at_least_one(ingrats)
    b_resent  = at_least_one(resentments)
    b_lean    = at_least_one(lean)
    b_bounty  = at_least_one(bounty)
    b_pride   = at_least_one(pride_hardships)
    b_arrival = at_least_one(arrivals)
    b_departure = at_least_one(departures)
    b_old_age = at_least_one(old_age_deaths)

    # open debts at end of run
    open_debts = [sum(len(c.debts) for c in w.chars) for w in worlds]
    b_debt = at_least_one(open_debts)

    # social topology at close: hub (one person significantly more connected)
    # and fracture (one person significantly more isolated)
    def _mutual_avgs(w):
        living = w.living
        if len(living) < 4:
            return []
        def m_avg(c):
            others = [o for o in living if o.id != c.id]
            return sum((c.feel(o.id) + o.feel(c.id)) / 2 for o in others) / len(others)
        return [m_avg(c) for c in living]

    def has_hub(w):
        scores = _mutual_avgs(w)
        if not scores:
            return False
        mean = sum(scores) / len(scores)
        return max(scores) >= 0.2 and max(scores) >= mean + 0.1

    def has_fracture(w):
        scores = _mutual_avgs(w)
        if not scores:
            return False
        mean = sum(scores) / len(scores)
        return min(scores) <= -0.1 and min(scores) <= mean - 0.1

    b_hub = sum(1 for w in worlds if has_hub(w))
    b_fracture = sum(1 for w in worlds if has_fracture(w))

    # founding persistence: did most founders survive?
    def founders_mostly_gone(w):
        orig = [c for c in w.chars if c.joined_at == 0 and c.parent_ids is None]
        if len(orig) < 6:
            return False
        rem = sum(1 for c in orig if c.alive)
        return rem < len(orig) * 0.6

    b_founders_gone = sum(1 for w in worlds if founders_mostly_gone(w))

    # population net change
    grew = sum(1 for w in worlds if len(w.living) > w.initial_people)
    shrank = sum(1 for w in worlds if len(w.living) < w.initial_people)
    same = n - grew - shrank

    # quarrel resolution rate
    total_q = sum(quarrels)
    total_m = sum(mediations)
    resolution_rate = total_m / total_q if total_q > 0 else 0.0

    # debt repayment rate (repayments / (gifts + repayments))
    total_g = sum(gifts)
    total_r = sum(repays)
    repay_rate = total_r / (total_g + total_r) if (total_g + total_r) > 0 else 0.0

    # --- build report ---
    seed_range = (
        f"seeds {seeds[0]}–{seeds[-1]}"
        if seeds[-1] == seeds[0] + len(seeds) - 1
        else f"{n} seeds"
    )
    parts = [
        f"# The Character of These Villages",
        "",
        f"*{n} {'run' if n == 1 else 'runs'} · {days} days each · "
        f"{people} souls each · {seed_range}*",
        "",
        "---",
        "",
    ]

    # Opening observation
    avg_gifts = _avg(gifts)
    avg_refusals = _avg(refusals)
    if avg_gifts > 5:
        parts.append(
            f"The bread moved. On average, {avg_gifts:.0f} gifts were given per run — "
            f"neighbors sharing surplus without being asked, or hungry ones knocking on doors. "
            f"This world is not generous by nature; it is just small enough that hunger is visible."
        )
    else:
        parts.append(
            f"The bread moved, but not freely. Only {avg_gifts:.1f} gifts per run on average. "
            f"These were careful villages."
        )
    parts.append("")

    # Sorted events by how often they occurred, to build a natural-language tier list
    events_with_counts = [
        ("at least one death", b_death),
        ("a bond formed", b_bond),
        ("a child born", b_birth),
        ("a quarrel", b_quarrel),
        ("a quarrel resolved by a third party", b_mediation),
        ("an act of ingratitude", b_ingrat),
        ("resentment turned a debt sour", b_resent),
        ("a village-wide hungry season", b_lean),
        ("a season of abundance most of the village shared", b_bounty),
        ("someone went hungry rather than ask for help", b_pride),
        ("a stranger arrived", b_arrival),
        ("someone driven out by collective rejection", b_departure),
        ("open favors still unpaid at the close", b_debt),
        ("a clear social hub at close — one person most others kept near", b_hub),
        ("a socially isolated person at close — one person nobody kept near", b_fracture),
    ]
    if days >= 360:
        events_with_counts.append(("someone died of old age", b_old_age))
    if days >= 480:
        events_with_counts.append(("most of the founding generation gone by close", b_founders_gone))

    # Group by threshold
    always   = [(desc, k) for desc, k in events_with_counts if k == n]
    usually  = [(desc, k) for desc, k in events_with_counts if n * 0.6 <= k < n]
    sometimes = [(desc, k) for desc, k in events_with_counts if n * 0.25 <= k < n * 0.6]
    rarely   = [(desc, k) for desc, k in events_with_counts if 0 < k < n * 0.25]
    never    = [(desc, k) for desc, k in events_with_counts if k == 0]

    def fmt_list(items):
        lines = []
        for desc, k in items:
            if n == 1:
                lines.append(f"- {desc.capitalize()}.")
            else:
                lines.append(f"- {desc.capitalize()} — {k} of {n} runs ({_pct(k, n)}).")
        return lines

    if always:
        parts.append("**What always happened:**")
        parts.append("")
        parts.extend(fmt_list(always))
        parts.append("")

    if usually:
        parts.append("**What usually happened:**")
        parts.append("")
        parts.extend(fmt_list(usually))
        parts.append("")

    if sometimes:
        parts.append("**What sometimes happened:**")
        parts.append("")
        parts.extend(fmt_list(sometimes))
        parts.append("")

    if rarely:
        parts.append("**What occasionally happened:**")
        parts.append("")
        parts.extend(fmt_list(rarely))
        parts.append("")

    if never:
        parts.append("**What never happened:**")
        parts.append("")
        parts.extend(fmt_list(never))
        parts.append("")

    # Averages
    parts.append("---")
    parts.append("")
    parts.append("**On average across these runs:**")
    parts.append("")
    avg_lines = [
        f"{avg_gifts:.1f} gifts given",
        f"{_avg(quarrels):.1f} quarrels",
        f"{_avg(bonds):.1f} bonds formed",
        f"{_avg(deaths):.1f} deaths",
    ]
    if days >= 96:
        avg_lines.append(f"{_avg(lean):.1f} lean seasons")
    parts.append("  ·  ".join(avg_lines))
    parts.append("")

    # Population fate
    if n > 1:
        parts.append("**Population at close:**")
        parts.append("")
        fates = []
        if grew:
            fates.append(f"grew in {grew} of {n} runs")
        if same:
            fates.append(f"stayed the same in {same} of {n} runs")
        if shrank:
            fates.append(f"shrank in {shrank} of {n} runs")
        parts.append(", ".join(f.capitalize() for f in fates) + "." if fates else "")
        parts.append("")

    # Structural observations
    obs = []
    if resolution_rate > 0.4:
        obs.append(
            f"Quarrels got mediated in {_pct(total_m, total_q)} of cases — "
            f"this is a world where third parties feel responsible for what happens between neighbors."
        )
    elif resolution_rate > 0 and total_q > 2:
        obs.append(
            f"Most quarrels here went unmediated. Villages find it easier to take sides than to sit people down."
        )
    if repay_rate > 0.5:
        obs.append(
            f"More than half of all debts were eventually repaid ({_pct(int(total_r), total_g + total_r)}). "
            f"In a gift economy, most people carry the weight seriously."
        )
    elif repay_rate < 0.2 and total_g > 5:
        obs.append(
            f"Only {_pct(int(total_r), total_g + total_r)} of gifts were ever returned. "
            f"The ledger of unspoken obligations grew faster than it shrank."
        )
    if b_pride > n * 0.6:
        obs.append(
            f"In most runs, someone went hungry rather than ask for help. "
            f"Pride is not an aberration here; it is a feature of the world."
        )

    if obs:
        parts.append("---")
        parts.append("")
        for o in obs:
            parts.append(o)
            parts.append("")

    # Closing
    parts.append("---")
    parts.append("")
    parts.append(
        "The structure persists. Different seeds, different names, the same shape of things. "
        "What varies is the particular — who refused whom, which winter was hard, "
        "whose pride cost them most. What holds is the world."
    )
    parts.append("")
    parts.append(
        f"*(parameters: --days {days} --people {people} · "
        f"variation comes from the seed alone)*"
    )
    parts.append("")

    return "\n".join(parts)
