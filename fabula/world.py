"""The simulation. Deterministic given a seed; it produces the raw fabula.

No text is generated here. The world only does things and remembers them.
The village runs on a gift economy: surplus is shared, refusals are
remembered, and reputation travels by word of mouth.
"""

import random

from .model import Character, Event, Memory, TICKS_PER_SEASON, season_index

SEASON_YIELD = (1.15, 1.40, 1.20, 0.35)  # spring, summer, autumn, winter

FOOD_NEED = 2.0      # below this a character looks for help
FOOD_SURPLUS = 5.0   # above this a character can afford to give
STORES_CAP = 12.0    # grain spoils: no one can hoard their way out of winter

# Starvation: 48 consecutive ticks below this threshold means death.
STARVATION_THRESHOLD = 0.5
STARVATION_TICKS = 48

# Bonds: mutual affinity floor that triggers household formation.
BOND_THRESHOLD = 0.62

# Childhood: ticks from birth until a character comes of age (3 seasons).
CHILDHOOD_TICKS = 72

# Elder: ticks in the village before a character becomes the village's memory (11 seasons).
ELDER_TICKS = 264

# Old age: past OLD_AGE_TICKS, dying of natural causes becomes possible.
# The probability grows linearly with each tick of overage. On a default
# 192-tick run no one reaches this; on a 400-tick run founders are at risk.
OLD_AGE_TICKS = 360        # 15 seasons
OLD_AGE_DEATH_RATE = 0.00012  # added probability per tick of overage

GRIEF_TICKS = 48  # 2 seasons of social withdrawal after losing a partner
ILLNESS_MAX_TICKS = 72  # 3 seasons — if ill this long, death probability spikes


class World:
    def __init__(self, seed: int = 0, people: int = 10):
        self.seed = seed
        self.rng = random.Random(seed)
        self.tick = 0
        self.events: list[Event] = []
        self.initial_people = people
        self._told: set = set()   # (event_id, listener_id) already gossiped
        self._last_hardship: dict = {}  # char id -> tick of last recorded hardship
        self._last_quarrel: dict = {}   # pair -> tick; even feuds need to catch their breath
        self._reconciled: set = set()   # frozenset pairs; no more side-taking for these
        self._feuds: set = set()         # frozenset pairs; active feuds escalate quarrels
        self._tribute_pending: list = []  # (deadline_tick, deceased_id, close_friends)
        self._teaching_pending: list = []  # (deadline_tick, young_id)
        self._last_memorial_tick: int = -TICKS_PER_SEASON  # throttle: one memorial per season
        self._drought_until: int = -1    # tick when drought relief ends (-1 = no drought)
        self._pacts: set = set()         # frozenset pairs with a declared close friendship

        from .names import FIRST_NAMES
        pool = list(FIRST_NAMES)
        self.rng.shuffle(pool)
        self.chars = [
            Character(
                id=i, name=pool[i % len(pool)][0], gender=pool[i % len(pool)][1],
                diligence=self.rng.random(),
                generosity=self.rng.random(),
                pride=self.rng.random(),
                openness=self.rng.random(),
            )
            for i in range(people)
        ]
        # mild initial leanings so the village is not a blank slate
        for a in self.chars:
            for b in self.chars:
                if a.id != b.id:
                    a.affinity[b.id] = self.rng.uniform(-0.15, 0.25)

    @property
    def living(self) -> list[Character]:
        return [c for c in self.chars if c.alive]

    def char(self, cid: int) -> Character:
        return self.chars[cid]

    # ------------------------------------------------------------------
    # bookkeeping

    def emit(self, kind, actors, valence, **data) -> Event:
        ev = Event(self.tick, kind, tuple(actors), valence, data)
        ev.data["id"] = len(self.events)
        self.events.append(ev)
        return ev

    def remember(self, who: Character, ev: Event, valence=None):
        who.memories.append(Memory(
            tick=ev.tick, kind=ev.kind, actors=ev.actors,
            valence=ev.valence if valence is None else valence,
            firsthand=True, event_id=ev.data["id"],
        ))

    def snapshot(self, ev: Event, a: Character, b: Character):
        """Record the state of the relationship right after the event."""
        ev.data["affinity"] = (round(a.feel(b.id), 3), round(b.feel(a.id), 3))

    # ------------------------------------------------------------------
    # main loop

    def run(self, ticks: int) -> list[Event]:
        for _ in range(ticks):
            self.step()
        return self.events

    def step(self):
        self.sys_harvest()
        self.sys_tribute()
        self.sys_misfortune()
        self.sys_need_and_gift()
        self.sys_deaths()
        self.sys_aging()
        self.sys_debts()
        self.sys_gossip()
        self.sys_quarrel()
        self.sys_mediation()
        self.sys_bonds()
        self.sys_births()
        self.sys_adoption()
        self.sys_growing_up()
        self.sys_teaching()
        self.sys_illness()
        if (self.tick + 1) % TICKS_PER_SEASON == 0:
            self.sys_festival()
            self.sys_pact()
            self.sys_drought()
            self.sys_blight()
            self.sys_lean_season()
            self.sys_bounty()
            self.sys_arrivals()
            self.sys_exile()
            self.sys_estrangement()
            self.sys_feud()
            self.sys_forgiveness()
        self.tick += 1

    # ------------------------------------------------------------------
    # systems

    def sys_harvest(self):
        yield_now = SEASON_YIELD[season_index(self.tick)]
        if self.tick < self._drought_until:
            yield_now *= 0.5  # drought halves the harvest for its duration
        for c in self.living:
            if c.childhood:
                # children contribute and eat less
                c.food += yield_now * 0.3 * (0.3 + 0.5 * c.diligence) * self.rng.uniform(0.7, 1.3)
                c.food = max(0.0, min(STORES_CAP, c.food) - 0.5)
            else:
                c.food += yield_now * (0.55 + 0.8 * c.diligence) * self.rng.uniform(0.7, 1.3)
                c.food = max(0.0, min(STORES_CAP, c.food) - 1.0)
        # bonded households pool their stores, children included
        seen: set = set()
        for c in self.living:
            if c.partner is None or c.id in seen:
                continue
            partner = self.chars[c.partner]
            if not partner.alive:
                continue
            household = [c, partner] + [
                ch for ch in self.living
                if ch.childhood and ch.parent_ids is not None
                and set(ch.parent_ids) == {c.id, partner.id}
            ]
            avg = sum(ch.food for ch in household) / len(household)
            for ch in household:
                ch.food = avg
            seen.add(c.id)
            seen.add(c.partner)

    def sys_misfortune(self):
        # Rats in the grain, a fire, a bad back at harvest: ruin that
        # strikes one house while the neighbors stand in plenty.
        for c in self.living:
            if c.food > 2.0 and self.rng.random() < 0.004:
                c.food *= 0.3
                ev = self.emit("MISFORTUNE", (c.id,), -0.5)
                self.remember(c, ev)
            elif c.starvation_streak >= 12 and self.rng.random() < 0.0018:
                # A body worn down by sustained hunger can break suddenly.
                self._kill(c, "misfortune")

    def sys_need_and_gift(self):
        for c in self.living:
            if c.food >= FOOD_NEED:
                continue
            # anyone with surplus might help; and the needy will knock on the
            # door of someone who owes them even if that door is a modest one
            donors = [d for d in self.living if d.id != c.id
                      and (d.food > FOOD_SURPLUS
                           or (d.debt_to(c.id) > 0 and d.food > FOOD_NEED + 0.5))]
            if not donors:
                continue
            if self.rng.random() < c.pride * 0.55:
                # too proud to ask; the hunger is remembered all the same,
                # though a sustained stretch of it counts as one hardship
                if self.tick - self._last_hardship.get(c.id, -99) >= 12:
                    self._last_hardship[c.id] = self.tick
                    ev = self.emit("HARDSHIP", (c.id,), -0.4, pride=True)
                    self.remember(c, ev)
                continue
            # the hungry go first to the doors where they are owed
            donor = max(donors, key=lambda d: c.feel(d.id)
                        + 0.35 * min(1.0, d.debt_to(c.id))
                        + self.rng.uniform(-0.1, 0.1))
            debt_held = donor.debts.get(c.id)
            owed = donor.debt_to(c.id)
            # a soured debt has no pull left: resentment rewrites the ledger
            pull = 0.0 if (debt_held and debt_held.soured) else 0.45 * min(1.0, owed)
            # giving from a thin pantry costs more courage than giving from a full one
            strain = 0.3 * max(0.0, min(1.0, (FOOD_SURPLUS - donor.food) / 3.0))
            willing = (donor.generosity * 0.9 + donor.feel(c.id) * 0.5
                       + pull - strain + self.rng.uniform(-0.25, 0.25))
            if willing > 0.35:
                amount = min(3.0, max(0.6, donor.food - 3.5))
                donor.food -= amount
                c.food += amount
                if owed > 0:
                    ev = self.emit("REPAYMENT", (donor.id, c.id), 0.7,
                                   carried=self.tick - donor.debts[c.id].since)
                    del donor.debts[c.id]     # the weight lifts
                    c.shift(donor.id, 0.2)
                    donor.shift(c.id, 0.15)   # relief is a kind of warmth
                else:
                    ev = self.emit("GIFT", (donor.id, c.id), 0.6)
                    c.shift(donor.id, 0.15)
                    donor.shift(c.id, 0.08)
                    c.owe(donor.id, self.tick)
                self.remember(c, ev)
                self.remember(donor, ev)
                self.snapshot(ev, donor, c)
            elif owed > 0:
                # refusing one's own benefactor: the debt no one wrote down
                # — but if they've reconciled, the village doesn't pile on
                if frozenset({c.id, donor.id}) in self._reconciled:
                    continue
                ev = self.emit("INGRATITUDE", (c.id, donor.id), -0.9,
                               carried=self.tick - donor.debts[c.id].since)
                donor.debts[c.id].weight += 0.5  # now owed twice over
                c.shift(donor.id, -0.45)
                self.remember(c, ev)
                self.remember(donor, ev, valence=-0.35)
                self.snapshot(ev, c, donor)
            else:
                ev = self.emit("REFUSAL", (c.id, donor.id), -0.7)
                c.shift(donor.id, -0.3)
                self.remember(c, ev)                 # the sting
                self.remember(donor, ev, valence=-0.2)  # a twinge of guilt
                self.snapshot(ev, c, donor)

    def sys_deaths(self):
        for c in self.living:
            if c.food < STARVATION_THRESHOLD:
                c.starvation_streak += 1
            else:
                c.starvation_streak = 0
            if c.starvation_streak >= STARVATION_TICKS:
                self._kill(c, "starvation")

    def sys_aging(self):
        for c in self.living:
            age = self.tick - c.joined_at
            overage = age - OLD_AGE_TICKS
            if overage <= 0:
                continue
            p = min(0.018, overage * OLD_AGE_DEATH_RATE)
            if self.rng.random() < p:
                self._kill(c, "old_age")

    def sys_debts(self):
        """A favor carried too long starts to work on the one who owes it.

        The humble grow warmer toward those who helped them; the proud
        grow colder, because to owe is to be reminded of the day they
        had to be helped. A debtor who comes into surplus may bring the
        favor back unasked — pride hurries that along, since the proud
        cannot stand to owe. But a debt that has already soured is never
        volunteered back: resentment rewrites the ledger.
        """
        for c in self.living:
            for debt in list(c.debts.values()):
                if self.tick - debt.since < TICKS_PER_SEASON:
                    continue  # fresh debts sit lightly
                creditor = self.char(debt.creditor)
                if not creditor.alive:
                    # Creditor died; the debt is lifted but the memory is not.
                    del c.debts[creditor.id]
                    continue
                urge = (c.generosity + 0.5 * c.pride
                        + max(0.0, c.feel(creditor.id)))
                if (not debt.soured and c.food > FOOD_NEED + 1.5
                        and creditor.food < FOOD_SURPLUS
                        and self.rng.random() < 0.05 * urge):
                    # repaid in labor as often as in bread: a day's help is
                    # worth more to the receiver than it costs the giver
                    c.food -= 0.6
                    creditor.food += 1.2
                    ev = self.emit("REPAYMENT", (c.id, creditor.id), 0.7,
                                   carried=self.tick - debt.since, unasked=True)
                    del c.debts[creditor.id]
                    c.shift(creditor.id, 0.15)
                    creditor.shift(c.id, 0.2)
                    self.remember(c, ev)
                    self.remember(creditor, ev)
                    self.snapshot(ev, c, creditor)
                    continue
                if c.pride > 0.6:
                    c.shift(debt.creditor, -0.012 * c.pride)
                    if not debt.soured and c.feel(debt.creditor) < -0.15:
                        debt.soured = True
                        ev = self.emit("RESENTMENT", (c.id, debt.creditor), -0.5,
                                       carried=self.tick - debt.since)
                        self.remember(c, ev)  # only the debtor knows, so far
                        self.snapshot(ev, c, self.char(debt.creditor))
                elif c.pride < 0.4:
                    c.shift(debt.creditor, 0.004)

    def sys_gossip(self):
        living = self.living
        if len(living) < 2:
            return
        for _ in range(max(1, len(living) // 3)):
            a, b = self.rng.sample(living, 2)
            if self.rng.random() > (a.openness + b.openness) / 2:
                continue
            a.shift(b.id, 0.02)  # company softens people
            b.shift(a.id, 0.02)
            self.tell(a, b)

    def vivid_memory(self, who: Character, listener: Character):
        """The memory most worth retelling to this listener."""
        best, best_score = None, 0.2
        for m in who.memories:
            if (m.event_id, listener.id) in self._told:
                continue
            if listener.id in m.actors and any(
                own.event_id == m.event_id for own in listener.memories
            ):
                continue  # no news to them
            age = self.tick - m.tick
            score = abs(m.valence) * max(0.25, 1.0 - age / 90.0)
            if score > best_score:
                best, best_score = m, score
        return best

    def tell(self, speaker: Character, listener: Character, public: bool = False):
        m = self.vivid_memory(speaker, listener)
        if m is None:
            return
        self._told.add((m.event_id, listener.id))
        # Memories of the dead distort more: no firsthand witness can correct them.
        about_dead = any(
            not self.chars[aid].alive
            for aid in m.actors
            if aid < len(self.chars) and aid != speaker.id
        )
        factor = (self.rng.uniform(0.6, 1.5) if about_dead
                  else self.rng.uniform(0.8, 1.3))
        heard = max(-1.0, min(1.0, m.valence * factor))
        listener.memories.append(Memory(
            tick=m.tick, kind=m.kind, actors=m.actors, valence=heard,
            firsthand=False, heard_from=speaker.id, event_id=m.event_id,
        ))
        distorted = abs(heard - m.valence) > 0.15
        self.emit("RUMOR", (speaker.id, listener.id), heard,
                  about=m.actors, about_kind=m.kind, distorted=distorted, public=public)
        self.react_to_rumor(listener, speaker, m, heard, distorted)

    def react_to_rumor(self, listener, speaker, m, heard, distorted):
        if listener.id in m.actors:
            # they are being talked about behind their back
            others = [x for x in m.actors if x != listener.id]
            if heard < -0.3 and others:
                other = self.char(others[0])
                # If this pair reconciled, old gossip no longer reopens wounds
                if frozenset({listener.id, other.id}) in self._reconciled:
                    return
                listener.shift(other.id, -0.2)
                listener.shift(speaker.id, -0.05)  # and they shoot the messenger a little
                ev = self.emit("OFFENSE", (listener.id, other.id), heard,
                               via=speaker.id, about_kind=m.kind, distorted=distorted)
                self.remember(listener, ev)
                self.snapshot(ev, listener, other)
            return
        if heard > 0.3:
            listener.shift(m.actors[0], 0.08)  # good deeds travel
        elif heard < -0.3 and len(m.actors) > 1:
            wronged, wrongdoer = m.actors[0], m.actors[1]
            # When a pair has publicly reconciled, the village stops taking sides
            if frozenset({wronged, wrongdoer}) in self._reconciled:
                return
            if m.kind == "INGRATITUDE":
                listener.shift(wrongdoer, -0.12)  # ingratitude has no partisans
            elif listener.feel(wronged) > 0.35:
                listener.shift(wrongdoer, -0.1)  # quietly taking sides

    def sys_quarrel(self):
        # winter brings people indoors and tempers fray; spring and summer are calmer
        season_multiplier = (1.35, 0.8, 1.0, 1.5)[season_index(self.tick)]
        living = self.living
        for a in living:
            for b in living:
                if b.id <= a.id:
                    continue
                pair = (a.id, b.id)
                if self.tick - self._last_quarrel.get(pair, -99) < 15:
                    continue
                feud_mult = 1.8 if frozenset({a.id, b.id}) in self._feuds else 1.0
                if min(a.feel(b.id), b.feel(a.id)) < -0.5 and self.rng.random() < 0.12 * season_multiplier * feud_mult:
                    self._last_quarrel[pair] = self.tick
                    witnesses = [w.id for w in living
                                 if w.id not in (a.id, b.id)
                                 and (w.feel(a.id) > 0.4 or w.feel(b.id) > 0.4)]
                    ev = self.emit("QUARREL", (a.id, b.id), -0.8, witnesses=witnesses)
                    a.shift(b.id, -0.1)
                    b.shift(a.id, -0.1)
                    self.remember(a, ev)
                    self.remember(b, ev)
                    self.snapshot(ev, a, b)
                    for w in living:  # the village takes sides
                        if w.id in (a.id, b.id):
                            continue
                        lean = w.feel(a.id) - w.feel(b.id)
                        if lean > 0.5:
                            # w likes a more — don't shift against b if w reconciled with b
                            if frozenset({w.id, b.id}) not in self._reconciled:
                                w.shift(b.id, -0.08)
                        elif lean < -0.5:
                            # w likes b more — don't shift against a if w reconciled with a
                            if frozenset({w.id, a.id}) not in self._reconciled:
                                w.shift(a.id, -0.08)

    def sys_mediation(self):
        living = self.living
        for a in living:
            for b in living:
                if b.id <= a.id:
                    continue
                if a.feel(b.id) < -0.35 and b.feel(a.id) < -0.35 and self.rng.random() < 0.14:
                    peacemakers = [w for w in living
                                   if w.id not in (a.id, b.id)
                                   and w.feel(a.id) > 0.25 and w.feel(b.id) > 0.25]
                    if not peacemakers:
                        continue
                    # elders are preferred as mediators
                    elder_makers = [w for w in peacemakers if w.elder]
                    w = self.rng.choice(elder_makers if elder_makers else peacemakers)
                    ev = self.emit("MEDIATION", (a.id, b.id), 0.7, mediator=w.id)
                    reset = 0.05 if w.elder else -0.05
                    a.affinity[b.id] = reset
                    b.affinity[a.id] = reset
                    a.shift(w.id, 0.15)
                    b.shift(w.id, 0.15)
                    self.remember(a, ev)
                    self.remember(b, ev)
                    self.remember(w, ev)
                    self.snapshot(ev, a, b)

    def sys_bonds(self):
        """When two people have grown close enough, for long enough, they join households."""
        # spring is when people declare things; winter is when they huddle in separately
        season_multiplier = (1.6, 1.0, 0.9, 0.7)[season_index(self.tick)]
        living = self.living
        for a in living:
            for b in living:
                if b.id <= a.id:
                    continue
                if a.partner is not None or b.partner is not None:
                    continue
                # grieving characters do not form new bonds
                if (a.grieving_until is not None and self.tick <= a.grieving_until):
                    continue
                if (b.grieving_until is not None and self.tick <= b.grieving_until):
                    continue
                # prevent parent-child and sibling bonds
                if (a.parent_ids and b.id in a.parent_ids) or (b.parent_ids and a.id in b.parent_ids):
                    continue
                if (a.parent_ids and b.parent_ids and set(a.parent_ids) == set(b.parent_ids)):
                    continue
                if (a.feel(b.id) >= BOND_THRESHOLD and b.feel(a.id) >= BOND_THRESHOLD
                        and self.rng.random() < 0.02 * season_multiplier):
                    a.partner = b.id
                    b.partner = a.id
                    # debts between partners dissolve when they become one household
                    a.debts.pop(b.id, None)
                    b.debts.pop(a.id, None)
                    ev = self.emit("BOND", (a.id, b.id), 0.9)
                    self.remember(a, ev)
                    self.remember(b, ev)
                    self.snapshot(ev, a, b)
                    for w in living:
                        if w.id not in (a.id, b.id):
                            w.shift(a.id, 0.04)
                            w.shift(b.id, 0.04)
                    # Jealousy: anyone who had unrequited feelings for either partner
                    for c in living:
                        if c.id in (a.id, b.id) or c.childhood or c.partner is not None:
                            continue
                        for loved_one, rival in ((a, b), (b, a)):
                            if c.feel(loved_one.id) > 0.70 and loved_one.feel(c.id) < 0.30:
                                c.shift(rival.id, -self.rng.uniform(0.12, 0.22))
                                ev_j = self.emit("JEALOUSY", (c.id, loved_one.id, rival.id), -0.55)
                                self.remember(c, ev_j)
                                break

    def sys_births(self):
        """A bonded pair, well-fed, may welcome a child into the village."""
        for c in self.living:
            if c.partner is None or c.id > c.partner:
                continue  # process each pair once (lower id drives the check)
            partner = self.chars[c.partner]
            if not partner.alive:
                continue
            if c.food < FOOD_SURPLUS or partner.food < FOOD_SURPLUS:
                continue
            # block if there is still a living child in childhood — wait until they grow up
            has_young_child = any(
                ch.alive and ch.childhood and ch.parent_ids is not None
                and set(ch.parent_ids) == {c.id, partner.id}
                for ch in self.chars
            )
            if has_young_child:
                continue
            if self.rng.random() < 0.008:
                self._birth(c, partner)

    def sys_growing_up(self):
        for c in self.living:
            if c.childhood and c.born_at is not None:
                if self.tick - c.born_at >= CHILDHOOD_TICKS:
                    c.childhood = False
                    # inherited affinities: seed feelings from living parents' strong opinions
                    inherited = []
                    if c.parent_ids:
                        parents_alive = [self.chars[pid] for pid in c.parent_ids
                                         if pid < len(self.chars) and self.chars[pid].alive]
                        if parents_alive:
                            for other in self.living:
                                if other.id == c.id or other.id in c.parent_ids:
                                    continue
                                avg = sum(p.feel(other.id) for p in parents_alive) / len(parents_alive)
                                if abs(avg) >= 0.20:
                                    c.shift(other.id, avg * 0.45)
                                    inherited.append((other.id, round(avg, 2)))
                    ev = self.emit("COMING_OF_AGE", (c.id,), 0.5,
                                   inherited=inherited if inherited else None)
                    self.remember(c, ev)
                    if c.parent_ids:
                        for pid in c.parent_ids:
                            if pid < len(self.chars) and self.chars[pid].alive:
                                self.chars[pid].shift(c.id, 0.1)
                    # schedule possible teaching within the next season
                    self._teaching_pending.append((self.tick + TICKS_PER_SEASON, c.id))
            elif not c.childhood and not c.elder:
                if self.tick - c.joined_at >= ELDER_TICKS:
                    c.elder = True
                    for other in self.living:
                        if other.id != c.id:
                            other.shift(c.id, 0.04)  # elders earn quiet respect

    def sys_teaching(self):
        """After a child comes of age, a willing elder may take them under their wing.

        Fires within a season of COMING_OF_AGE. The elder must have affinity >= 0.45
        toward the young person and not already have taught someone this run. Teaching
        slightly improves the young person's diligence and deepens the bond between them.
        """
        if not self._teaching_pending:
            return
        remaining = []
        already_teaching = {ev.actors[0] for ev in self.events if ev.kind == "TEACHING"}
        for deadline, young_id in self._teaching_pending:
            if self.tick > deadline:
                continue
            young = self.chars[young_id] if young_id < len(self.chars) else None
            if young is None or not young.alive or young.childhood:
                continue
            # find willing elders
            mentors = [
                c for c in self.living
                if c.elder and c.id != young_id
                and c.id not in already_teaching
                and c.feel(young_id) >= 0.45
            ]
            if not mentors:
                remaining.append((deadline, young_id))
                continue
            if self.rng.random() > 0.55:
                remaining.append((deadline, young_id))
                continue
            mentor = max(mentors, key=lambda c: c.feel(young_id))
            # teaching effect: mild diligence boost + affinity deepening
            young.diligence = min(1.0, young.diligence + self.rng.uniform(0.04, 0.09))
            mentor.shift(young_id, 0.12)
            young.shift(mentor.id, 0.18)
            ev = self.emit("TEACHING", (mentor.id, young_id), 0.65)
            self.remember(mentor, ev)
            self.remember(young, ev)
        self._teaching_pending = remaining

    def sys_illness(self):
        """Illness spreads through the village: a character can fall ill, struggle, and either
        recover or die. Illness increases food consumption and death risk.
        """
        for c in self.living:
            if c.childhood:
                continue
            if not c.ill:
                # Chance of falling ill: higher in winter, lower in summer
                base_rate = (0.0012, 0.0006, 0.0009, 0.0018)[season_index(self.tick)]
                if self.rng.random() < base_rate:
                    c.ill = True
                    c.ill_since = self.tick
                    ev = self.emit("ILLNESS", (c.id,), -0.6)
                    self.remember(c, ev)
            else:
                # Illness drains food faster
                c.food = max(0.0, c.food - 0.06)
                # Check recovery: base 1.5% per tick
                if self.rng.random() < 0.015:
                    c.ill = False
                    old_since = c.ill_since
                    c.ill_since = None
                    ev = self.emit("RECOVERY", (c.id,), 0.5)
                    self.remember(c, ev)
                    # Illness leaves a mark — diligence drops slightly
                    c.diligence = max(0.0, c.diligence - self.rng.uniform(0.02, 0.05))
                elif (c.ill_since is not None
                      and self.tick - c.ill_since >= ILLNESS_MAX_TICKS
                      and self.rng.random() < 0.04):
                    # Prolonged illness kills
                    self._kill(c, "misfortune")
                elif (c.ill_since is not None
                      and self.tick - c.ill_since == ILLNESS_MAX_TICKS // 2):
                    # Halfway to the danger point — the village gathers
                    vigil_mourners = [
                        o for o in self.living
                        if o.id != c.id and not o.childhood and o.feel(c.id) >= 0.50
                    ]
                    if len(vigil_mourners) >= 2:
                        ev_v = self.emit("VIGIL", tuple([c.id] + [m.id for m in vigil_mourners]), -0.3)
                        self.remember(c, ev_v)
                        for m in vigil_mourners:
                            self.remember(m, ev_v)
                        for i, ma in enumerate(vigil_mourners):
                            for mb in vigil_mourners[i + 1:]:
                                boost = self.rng.uniform(0.02, 0.04)
                                ma.shift(mb.id, boost)
                                mb.shift(ma.id, boost)

    def sys_festival(self):
        living = self.living
        self.emit("FESTIVAL", tuple(c.id for c in living), 0.3,
                  season=season_index(self.tick))
        for a in living:
            for b_id in list(a.affinity):
                a.shift(b_id, 0.03)
        # someone always talks too much at a festival
        for s in self.rng.sample(living, k=min(2, len(living))):
            listeners = [c for c in living if c.id != s.id]
            for listener in self.rng.sample(listeners, k=min(4, len(listeners))):
                self.tell(s, listener, public=True)

    def sys_lean_season(self):
        """If most of the village is hungry at season's end, record the shared want."""
        living = self.living
        if len(living) < 3:
            return
        hungry = [c for c in living if c.food < FOOD_NEED]
        if len(hungry) < max(2, len(living) * 0.50):
            return
        # Solidarity: generous, well-fed neighbors step in without being asked.
        gave = 0
        for donor in living:
            if donor.food > FOOD_SURPLUS and donor.generosity > 0.58:
                needy = [h for h in hungry if h.id != donor.id]
                if needy:
                    t = self.rng.choice(needy)
                    amount = min(2.0, max(0.0, donor.food - FOOD_NEED - 0.5))
                    if amount > 0.3:
                        donor.food -= amount
                        t.food += amount
                        t.shift(donor.id, 0.12)
                        donor.shift(t.id, 0.06)
                        gave += 1
        ev = self.emit("LEAN_SEASON", tuple(c.id for c in living), -0.5,
                       hungry_count=len(hungry), had_solidarity=(gave > 0))
        for c in living:
            self.remember(c, ev)

    def sys_bounty(self):
        """If most of the village is well-fed at season's end, record the abundance."""
        living = self.living
        if len(living) < 3:
            return
        if any(ev.kind == "LEAN_SEASON" and ev.tick == self.tick for ev in self.events):
            return
        well_fed = [c for c in living if c.food >= FOOD_SURPLUS]
        if len(well_fed) < max(2, len(living) * 0.60):
            return
        ev = self.emit("BOUNTY", tuple(c.id for c in living), 0.5,
                       fed_count=len(well_fed))
        for c in living:
            self.remember(c, ev)

    def sys_arrivals(self):
        """At the end of each season, the village may draw a new face."""
        if len(self.living) < self.initial_people and self.rng.random() < 0.55:
            self._arrive()

    def sys_adoption(self):
        """A bonded couple may take in an orphaned child whose both parents are dead.

        Fires at most once per orphan. The couple must have no living young children
        of their own (biological or previously adopted). Adoption restructures the
        child's parent_ids so the full family model applies — food sharing, inheritance,
        sibling detection — without any special cases.
        """
        living = self.living
        # already-adopted children: parent_ids changed since birth, tracked by ADOPTION events
        already_adopted = {ev.actors[0] for ev in self.events if ev.kind == "ADOPTION"}

        # find orphaned childhood chars
        orphans = []
        for c in living:
            if not c.childhood or c.parent_ids is None or c.id in already_adopted:
                continue
            both_gone = all(
                not self.chars[pid].alive
                for pid in c.parent_ids
                if pid < len(self.chars)
            )
            if both_gone:
                orphans.append(c)

        if not orphans:
            return

        # find willing bonded pairs (seen once, not both)
        seen_pairs: set = set()
        willing = []
        for c in living:
            if c.partner is None or c.childhood:
                continue
            pair = frozenset((c.id, c.partner))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            partner = self.chars[c.partner]
            if not partner.alive:
                continue
            # no living young children (bio or adopted) from this pair
            has_young = any(
                ch.alive and ch.childhood and ch.parent_ids is not None
                and set(ch.parent_ids) == {c.id, c.partner}
                for ch in self.chars
            )
            if not has_young:
                willing.append((c, partner))

        if not willing:
            return

        self.rng.shuffle(orphans)
        self.rng.shuffle(willing)

        for orphan in orphans:
            # small per-tick probability — over 10 ticks it becomes near-certain
            if self.rng.random() > 0.18:
                continue
            if not willing:
                break
            a, b = willing.pop()
            # restructure family
            orphan.parent_ids = (a.id, b.id)
            # warm the bonds
            a.affinity[orphan.id] = min(1.0, a.feel(orphan.id) + 0.55)
            b.affinity[orphan.id] = min(1.0, b.feel(orphan.id) + 0.55)
            orphan.affinity[a.id] = min(1.0, orphan.feel(a.id) + 0.45)
            orphan.affinity[b.id] = min(1.0, orphan.feel(b.id) + 0.45)
            # siblings from same new parents feel warmth toward the newcomer
            for sib in living:
                if sib.id != orphan.id and sib.parent_ids and set(sib.parent_ids) == {a.id, b.id}:
                    sib.affinity[orphan.id] = self.rng.uniform(0.3, 0.6)
                    orphan.affinity[sib.id] = self.rng.uniform(0.3, 0.6)
            ev = self.emit("ADOPTION", (orphan.id, a.id, b.id), 0.75)
            self.remember(orphan, ev)
            self.remember(a, ev)
            self.remember(b, ev)

    def sys_exile(self):
        """A person cold-shouldered by enough of the village may quietly leave.

        Bonded characters have roots; strangers lose patience sooner than founders.
        The village must have at least 4 souls — too small to exile anyone.
        """
        living = self.living
        if len(living) < 4:
            return
        for c in living:
            if c.childhood or c.partner is not None:
                continue
            if self.tick - c.joined_at < 48:   # too new — still finding their place
                continue
            others = [o for o in living if o.id != c.id]
            avg_toward_c = sum(o.feel(c.id) for o in others) / len(others)
            if avg_toward_c > -0.28:
                continue
            severity = max(0.0, -avg_toward_c - 0.28)
            base_p = 0.015 if c.joined_at > 0 else 0.008   # strangers leave sooner
            p = min(0.04, base_p * severity * 4)
            if self.rng.random() < p:
                self._depart(c)

    def sys_estrangement(self):
        """When two people have been deeply cold to each other for seasons without
        any bridge-building — no gifts, no repayments, no mediation — the hostility
        can crystallize into something permanent.

        ESTRANGEMENT is not about silence; it can follow years of quarreling. It is
        about the absence of any warmth, any repair attempt, any positive act.
        It fires at most once per pair.
        """
        living = self.living
        # Only positive acts can prevent estrangement — quarrels don't
        bridge_kinds = {"GIFT", "REPAYMENT", "MEDIATION"}
        already_estranged = {
            frozenset(ev.actors[:2]) for ev in self.events if ev.kind == "ESTRANGEMENT"
        }
        # Pairs with a positive act in the last 3 seasons are not yet estranged
        recent_threshold = self.tick - 72   # 3 seasons
        bridged_pairs: set = set()
        for ev in self.events:
            if ev.tick <= recent_threshold:
                continue
            if ev.kind in bridge_kinds and len(ev.actors) >= 2:
                bridged_pairs.add(frozenset(ev.actors[:2]))
        for i, a in enumerate(living):
            if a.childhood:
                continue
            for b in living[i + 1:]:
                if b.childhood:
                    continue
                pair = frozenset({a.id, b.id})
                if pair in already_estranged or pair in bridged_pairs:
                    continue
                if pair in self._pacts:
                    continue  # pact partners cannot become estranged
                if a.feel(b.id) > -0.45 or b.feel(a.id) > -0.45:
                    continue
                if self.rng.random() > 0.18:
                    continue
                # Deepen the coldness slightly — estrangement hardens what was already cold
                a.shift(b.id, -0.05)
                b.shift(a.id, -0.05)
                avg = (a.feel(b.id) + b.feel(a.id)) / 2
                ev = self.emit("ESTRANGEMENT", (a.id, b.id), avg)
                self.remember(a, ev)
                self.remember(b, ev)
                already_estranged.add(pair)   # prevent double-firing this season

    def sys_feud(self):
        """An estrangement can harden into a feud when bitterness has run deep and long.

        FEUD fires once per pair, only if already ESTRANGED and both have affinity < -0.65.
        The village is forced to take sides; feuding pairs have heightened quarrel probability.
        """
        living = self.living
        estranged_pairs = {
            frozenset(ev.actors[:2]) for ev in self.events if ev.kind == "ESTRANGEMENT"
        }
        already_feuded = {
            frozenset(ev.actors[:2]) for ev in self.events if ev.kind == "FEUD"
        }
        for i, a in enumerate(living):
            if a.childhood:
                continue
            for b in living[i + 1:]:
                if b.childhood:
                    continue
                pair = frozenset({a.id, b.id})
                if pair not in estranged_pairs or pair in already_feuded:
                    continue
                if a.feel(b.id) > -0.65 or b.feel(a.id) > -0.65:
                    continue
                # Count quarrels between this pair since estrangement
                quarrel_count = sum(
                    1 for ev in self.events
                    if ev.kind == "QUARREL" and frozenset(ev.actors[:2]) == pair
                )
                if quarrel_count < 3:
                    continue
                if self.rng.random() > 0.35:
                    continue
                ev = self.emit("FEUD", (a.id, b.id), -0.95)
                self.remember(a, ev)
                self.remember(b, ev)
                self._feuds.add(pair)
                # Force the village to choose sides
                for other in living:
                    if other.id in (a.id, b.id):
                        continue
                    lean = other.feel(a.id) - other.feel(b.id)
                    if lean > 0.25:
                        other.shift(a.id, 0.05)
                        other.shift(b.id, -0.05)
                    elif lean < -0.25:
                        other.shift(b.id, 0.05)
                        other.shift(a.id, -0.05)
                already_feuded.add(pair)

    def sys_forgiveness(self):
        """Time and quiet let old quarrels die.

        Two paths to reconciliation:
        1. Mediated: a pair sat down with a peacemaker, and 2 seasons have
           passed without a new quarrel between them.
        2. Organic: a quarreled pair (never estranged, never mediated) has
           had 5 seasons of quiet — no quarrel, no estrangement —
           and they simply drifted back toward neutral on their own.

        In both cases, affinity is raised to match the actual peace.
        Fires at most once per pair.
        """
        last_med: dict = {}
        last_qrl: dict = {}
        for ev in self.events:
            pair = frozenset(ev.actors[:2])
            if ev.kind == "MEDIATION":
                last_med[pair] = max(last_med.get(pair, 0), ev.tick)
            elif ev.kind == "QUARREL":
                last_qrl[pair] = max(last_qrl.get(pair, 0), ev.tick)
        if not last_qrl:
            return
        estranged = {
            frozenset(ev.actors[:2]) for ev in self.events if ev.kind == "ESTRANGEMENT"
        }
        already = {
            frozenset(ev.actors[:2]) for ev in self.events if ev.kind == "RECONCILIATION"
        }
        living = self.living
        for i, a in enumerate(living):
            if a.childhood:
                continue
            for b in living[i + 1:]:
                if b.childhood:
                    continue
                pair = frozenset({a.id, b.id})
                if pair in already or pair in estranged or pair not in last_qrl:
                    continue
                last_q = last_qrl[pair]
                if pair in last_med:
                    # Mediated path: 2 seasons quiet since last mediation
                    med_tick = last_med[pair]
                    if last_q > med_tick:
                        continue  # quarreled again since mediation
                    if self.tick - med_tick < 2 * TICKS_PER_SEASON:
                        continue
                    warm = 0.28
                else:
                    # Organic path: 5 seasons since last quarrel, not estranged
                    if self.tick - last_q < 5 * TICKS_PER_SEASON:
                        continue
                    # Only heal if not still deeply hostile from gossip
                    if a.feel(b.id) < -0.45 or b.feel(a.id) < -0.45:
                        continue
                    warm = 0.20
                a.affinity[b.id] = max(a.feel(b.id), warm)
                b.affinity[a.id] = max(b.feel(a.id), warm)
                # Reconciliation clears lingering debts — forgiveness of the
                # debt is part of making peace; the ledger closes with the grudge
                if b.id in a.debts:
                    del a.debts[b.id]
                if a.id in b.debts:
                    del b.debts[a.id]
                self._reconciled.add(pair)
                ev = self.emit("RECONCILIATION", (a.id, b.id), 0.6 if warm < 0.25 else 0.7)
                self.remember(a, ev)
                self.remember(b, ev)
                self.snapshot(ev, a, b)

    def sys_tribute(self):
        """After a beloved person dies, their close friends give bread to the bereaved."""
        if not self._tribute_pending:
            return
        remaining = []
        for deadline, deceased_id, friend_ids in self._tribute_pending:
            if self.tick > deadline:
                continue  # expired without firing — no one had surplus
            # Find bereaved: partner and adult children of the deceased
            bereaved = []
            deceased = self.chars[deceased_id] if deceased_id < len(self.chars) else None
            if deceased and deceased.partner is not None:
                p = self.chars[deceased.partner]
                if p.alive:
                    bereaved.append(p)
            for ch in self.living:
                if ch.parent_ids and deceased_id in ch.parent_ids and not ch.childhood:
                    bereaved.append(ch)
            if not bereaved:
                continue  # no one to receive tribute
            # One friend gives (50% chance per tick per eligible friend)
            gave = False
            for fid in friend_ids:
                if fid >= len(self.chars):
                    continue
                friend = self.chars[fid]
                if not friend.alive or friend.food <= FOOD_SURPLUS:
                    continue
                if self.rng.random() < 0.5:
                    recipient = self.rng.choice(bereaved)
                    amount = min(1.5, friend.food - FOOD_NEED)
                    if amount > 0.3:
                        friend.food -= amount
                        recipient.food = min(STORES_CAP, recipient.food + amount)
                        ev = self.emit("TRIBUTE", (friend.id, recipient.id), 0.7,
                                       deceased=deceased_id)
                        friend.shift(recipient.id, 0.08)
                        recipient.shift(friend.id, 0.12)
                        self.remember(friend, ev)
                        self.remember(recipient, ev)
                        gave = True
                        break  # one tribute gift per death event per tick
            if gave or self.tick >= deadline:
                continue  # tribute fired or expired
            remaining.append((deadline, deceased_id, friend_ids))
        self._tribute_pending = remaining

    def sys_blight(self):
        """A rare crop failure that strikes several households at once.

        Fires only in spring, summer, or autumn (5% chance). Reduces food
        for 3-5 random living adults by roughly half, which will usually
        trigger a LEAN_SEASON when sys_lean_season() runs next.
        """
        if season_index(self.tick) == 3:
            return  # winter already harsh; blight belongs to growing seasons
        if self.rng.random() > 0.05:
            return
        living = [c for c in self.living if not c.childhood]
        if len(living) < 3:
            return
        n_hit = min(len(living), self.rng.randint(3, 5))
        affected = self.rng.sample(living, k=n_hit)
        for c in affected:
            c.food = max(0.0, c.food * 0.45)
        ev = self.emit("BLIGHT", tuple(c.id for c in affected), -0.8,
                       affected_count=n_hit)
        for c in self.living:
            self.remember(c, ev)

    def sys_pact(self):
        """Two people who care deeply for each other but have not formed a household
        may, after seasons of warmth, name what they have.

        A pact is not a bond: it does not require romantic partnership and does not
        change legal status. It protects against estrangement and is remembered by
        both parties as one of the anchoring events of their time together.
        """
        if self._pacts:
            return  # one pact per village run is enough
        living = self.living
        estranged_pairs = {frozenset(ev.actors[:2]) for ev in self.events if ev.kind == "ESTRANGEMENT"}
        for i, a in enumerate(living):
            if a.childhood:
                continue
            for b in living[i + 1:]:
                if b.childhood:
                    continue
                pair = frozenset({a.id, b.id})
                if a.partner == b.id or b.partner == a.id:
                    continue
                if pair in estranged_pairs or pair in self._feuds:
                    continue
                if a.feel(b.id) < 0.80 or b.feel(a.id) < 0.80:
                    continue
                together_since = max(a.joined_at, b.joined_at)
                if self.tick - together_since < 96:
                    continue
                if self.rng.random() > 0.04:
                    continue
                self._pacts.add(pair)
                boost = self.rng.uniform(0.02, 0.04)
                a.diligence = min(1.0, a.diligence + boost)
                b.diligence = min(1.0, b.diligence + boost)
                ev = self.emit("PACT", (a.id, b.id), 0.65)
                self.remember(a, ev)
                self.remember(b, ev)
                return  # one per village; stop after the first fires

    def sys_celebration(self, newborn_id: int):
        """A birth in a thriving village becomes a communal moment."""
        from .model import year_of
        living = self.living
        adults = [c for c in living if not c.childhood]
        if len(adults) < 3:
            return
        avg_food = sum(c.food for c in adults) / len(adults)
        if avg_food < FOOD_NEED * 1.5:
            return
        if self.tick < self._drought_until:
            return
        year = year_of(self.tick)
        if any(ev.kind == "CELEBRATION" and year_of(ev.tick) == year for ev in self.events):
            return
        if self.rng.random() > 0.70:
            return
        ev = self.emit("CELEBRATION", tuple(c.id for c in living), 0.45, newborn=newborn_id)
        for c in living:
            self.remember(c, ev)
        for i, ca in enumerate(living):
            for cb in living[i + 1:]:
                boost = self.rng.uniform(0.02, 0.05)
                ca.shift(cb.id, boost)
                cb.shift(ca.id, boost)

    def sys_drought(self):
        """A season-long crop failure that halves yields for two full seasons.

        Fires only in summer or autumn (5% chance per season check). Only one
        drought per year. Effects are applied through sys_harvest() for the
        duration. The collective hardship is recorded as a village-wide event.
        """
        # Drought end: fires in the first season where drought is no longer active.
        # Must be checked before the summer/autumn guard since droughts end in winter or spring.
        if 0 < self._drought_until <= self.tick:
            living = self.living
            if living:
                ev = self.emit("DROUGHT_END", tuple(c.id for c in living), 0.20)
                for c in living:
                    self.remember(c, ev)
            self._drought_until = -1

        if season_index(self.tick) not in (1, 2):  # summer, autumn only
            return
        if self.tick < self._drought_until:
            return  # already in a drought
        from .model import year_of
        year = year_of(self.tick)
        if any(ev.kind == "DROUGHT" and year_of(ev.tick) == year for ev in self.events):
            return  # one drought per year
        if self.rng.random() > 0.05:
            return
        living = self.living
        if len(living) < 2:
            return
        self._drought_until = self.tick + 2 * TICKS_PER_SEASON
        ev = self.emit("DROUGHT", tuple(c.id for c in living), -0.85)
        for c in living:
            self.remember(c, ev)

    # ------------------------------------------------------------------
    # deaths, arrivals, births

    def _kill(self, c: Character, cause: str):
        if not c.alive:
            return
        c.alive = False
        c.died_at = self.tick
        ev = self.emit("DEATH", (c.id,), -1.0, cause=cause)
        self.remember(c, ev)
        # Partner grief: the village closes around the bereaved.
        prev_partner = None
        if c.partner is not None:
            survivor = self.chars[c.partner]
            if survivor.alive:
                prev_partner = survivor
                ev_w = self.emit("WIDOWING", (survivor.id, c.id), -0.85)
                self.remember(survivor, ev_w)
                self.snapshot(ev_w, survivor, c)
                survivor.grieving_until = self.tick + GRIEF_TICKS
                for other in self.living:
                    if other.id != survivor.id:
                        other.shift(survivor.id, 0.06)
            survivor.partner = None
        c.partner = None
        # Food inheritance: what the dead had left feeds those they loved.
        if c.food > 0.5:
            household = []
            if prev_partner is not None:
                household.append(prev_partner)
            household += [ch for ch in self.living
                          if ch.childhood and ch.parent_ids and c.id in ch.parent_ids]
            if household:
                share = c.food / len(household)
                for h in household:
                    h.food = min(STORES_CAP, h.food + share)
            c.food = 0.0
        # Debts die with the person on both sides — unless there is a child
        # who can carry what the parent left unanswered.
        adult_children = [ch for ch in self.living
                          if ch.parent_ids and c.id in ch.parent_ids and not ch.childhood]
        for debt in c.debts.values():
            creditor = self.chars[debt.creditor]
            if not creditor.alive:
                continue
            if adult_children:
                # One child takes on a half-weight version of the parent's debt
                heir = self.rng.choice(adult_children)
                heir.owe(creditor.id, self.tick, weight=debt.weight * 0.5)
                # The obligation passing to a child creates mild positive affect
                creditor.shift(heir.id, 0.05)
            else:
                # The debt dissolves; the creditor feels the unresolved absence
                creditor.shift(c.id, -0.04)
        c.debts.clear()
        # Debtors of the dead lose their obligation but not the memory.
        for other in self.chars:
            if c.id in other.debts:
                del other.debts[c.id]
        # Inherited echoes: living children absorb faint traces of the dead's unresolved enmities.
        for child in self.chars:
            if not child.alive or child.parent_ids is None:
                continue
            if c.id not in child.parent_ids:
                continue
            for enemy_id, val in c.affinity.items():
                if val < -0.3 and enemy_id < len(self.chars) and enemy_id != child.id:
                    if self.chars[enemy_id].alive:
                        child.shift(enemy_id, val * 0.15)
        # Tribute: close friends of a well-connected or elder dead person may give
        # bread to the bereaved in the days following — a social wave of grief-generosity.
        close_friends = [
            other for other in self.living
            if other.feel(c.id) > 0.45 and other.food > FOOD_SURPLUS
        ]
        if len(close_friends) >= 2 and (c.elder or len(close_friends) >= 3):
            # Schedule tribute gifts to fire within the next 6 ticks
            deadline = self.tick + 6
            self._tribute_pending.append((deadline, c.id, [f.id for f in close_friends]))
        # Memorial: if the deceased was an elder or truly beloved, the village gathers.
        # Threshold is high so it fires only for the most significant losses.
        mourners = [
            other for other in self.living
            if other.feel(c.id) > 0.55
        ]
        if (len(mourners) >= 4 and (c.elder or len(mourners) >= 6)
                and self.tick - self._last_memorial_tick >= TICKS_PER_SEASON):
            self._last_memorial_tick = self.tick
            top_mourners = sorted(mourners, key=lambda m: m.feel(c.id), reverse=True)[:5]
            ev_m = self.emit("MEMORIAL", tuple([c.id] + [m.id for m in top_mourners]), 0.3)
            for i, ma in enumerate(top_mourners):
                self.remember(ma, ev_m)
                for mb in top_mourners[i + 1:]:
                    ma.shift(mb.id, 0.07)
                    mb.shift(ma.id, 0.07)
        # Shared grief can crack a feud: two enemies who both knew the deceased
        # may find the hate too expensive to carry past the grave.
        if self._feuds:
            for ma in self.living:
                if ma.feel(c.id) < 0.30:
                    continue
                for mb in self.living:
                    if mb.id <= ma.id or mb.feel(c.id) < 0.30:
                        continue
                    pair = frozenset({ma.id, mb.id})
                    if pair not in self._feuds:
                        continue
                    if self.rng.random() < 0.30:
                        ma.shift(mb.id, 0.18)
                        mb.shift(ma.id, 0.18)
                        self._feuds.discard(pair)
                        self._reconciled.add(pair)
                        ev_r = self.emit("RECONCILIATION", (ma.id, mb.id), 0.55,
                                         reason="shared_grief", deceased=c.id)
                        self.remember(ma, ev_r)
                        self.remember(mb, ev_r)
        # Legacy: students carry forward something of a teacher's patience
        teaching_evs = [
            ev for ev in self.events
            if ev.kind == "TEACHING" and len(ev.actors) >= 2 and ev.actors[0] == c.id
        ]
        if teaching_evs:
            students = [
                self.chars[ev.actors[1]] for ev in teaching_evs
                if ev.actors[1] < len(self.chars) and self.chars[ev.actors[1]].alive
            ]
            if students:
                boost = self.rng.uniform(0.03, 0.07)
                for st in students:
                    st.diligence = min(1.0, st.diligence + boost)
                ev_l = self.emit("LEGACY", tuple([c.id] + [st.id for st in students]), 0.4)
                for st in students:
                    self.remember(st, ev_l)

    def _depart(self, c: Character):
        """Character leaves the village — driven out by collective coldness, not dead."""
        if not c.alive:
            return
        c.alive = False
        c.departed = True
        c.died_at = self.tick
        ev = self.emit("DEPARTURE", (c.id,), -0.65)
        self.remember(c, ev)
        # Sever bond without WIDOWING — this is abandonment, not bereavement
        if c.partner is not None:
            survivor = self.chars[c.partner]
            if survivor.alive:
                survivor.affinity[c.id] = max(-1.0, survivor.feel(c.id) - 0.5)
            survivor.partner = None
        c.partner = None
        # Creditors are stiffed; the village notes it
        for debt in c.debts.values():
            cred = self.chars[debt.creditor]
            if cred.alive:
                cred.shift(c.id, -0.12)
        c.debts.clear()
        for other in self.chars:
            if c.id in other.debts:
                del other.debts[c.id]
        # The village registers the departure with a mild chill — they pushed, after all
        for other in self.living:
            other.shift(c.id, -0.03)

    def _arrive(self):
        from .names import FIRST_NAMES
        used = {ch.name for ch in self.chars}
        pool = [(n, g) for n, g in FIRST_NAMES if n not in used]
        if not pool:
            pool = list(FIRST_NAMES)
        name, gender = self.rng.choice(pool)
        new_id = len(self.chars)
        newcomer = Character(
            id=new_id, name=name, gender=gender,
            diligence=self.rng.random(),
            generosity=self.rng.random(),
            pride=self.rng.random(),
            openness=self.rng.random(),
            food=3.0,
            joined_at=self.tick,
        )
        for ch in self.living:
            newcomer.affinity[ch.id] = self.rng.uniform(-0.1, 0.2)
            ch.affinity[new_id] = self.rng.uniform(-0.1, 0.2)
        self.chars.append(newcomer)
        ev = self.emit("ARRIVAL", (new_id,), 0.2)
        self.remember(newcomer, ev)

    def _birth(self, a: Character, b: Character):
        from .names import FIRST_NAMES
        used = {ch.name for ch in self.chars}
        pool = [(n, g) for n, g in FIRST_NAMES if n not in used]
        if not pool:
            pool = list(FIRST_NAMES)
        name, gender = self.rng.choice(pool)
        new_id = len(self.chars)

        def blend(x, y):
            return max(0.0, min(1.0, (x + y) / 2 + self.rng.gauss(0, 0.12)))

        child = Character(
            id=new_id, name=name, gender=gender,
            diligence=blend(a.diligence, b.diligence),
            generosity=blend(a.generosity, b.generosity),
            pride=blend(a.pride, b.pride),
            openness=blend(a.openness, b.openness),
            food=1.5,
            childhood=True,
            born_at=self.tick,
            joined_at=self.tick,
            parent_ids=(a.id, b.id),
        )
        child.affinity[a.id] = 0.8
        child.affinity[b.id] = 0.8
        for ch in self.living:
            if ch.id not in (a.id, b.id):
                parent_lean = (a.feel(ch.id) + b.feel(ch.id)) / 2 * 0.3
                child_feel = max(-0.25, min(0.25,
                    parent_lean + self.rng.uniform(-0.1, 0.1)))
                # siblings start with stronger mutual warmth
                if ch.parent_ids and set(ch.parent_ids) == {a.id, b.id}:
                    sibling_bond = self.rng.uniform(0.35, 0.7)
                    child.affinity[ch.id] = max(child_feel, sibling_bond)
                    ch.affinity[new_id] = self.rng.uniform(0.35, 0.7)
                else:
                    child.affinity[ch.id] = child_feel
                    ch.affinity[new_id] = self.rng.uniform(0.0, 0.15)
        a.affinity[new_id] = 0.85
        b.affinity[new_id] = 0.85
        self.chars.append(child)
        ev = self.emit("BIRTH", (new_id, a.id, b.id), 0.8)
        self.remember(child, ev)
        self.remember(a, ev)
        self.remember(b, ev)
        self.sys_celebration(new_id)
