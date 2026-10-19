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
        self.sys_growing_up()
        if (self.tick + 1) % TICKS_PER_SEASON == 0:
            self.sys_festival()
            self.sys_lean_season()
            self.sys_bounty()
            self.sys_arrivals()
            self.sys_exile()
        self.tick += 1

    # ------------------------------------------------------------------
    # systems

    def sys_harvest(self):
        yield_now = SEASON_YIELD[season_index(self.tick)]
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
                if min(a.feel(b.id), b.feel(a.id)) < -0.5 and self.rng.random() < 0.12 * season_multiplier:
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
                            w.shift(b.id, -0.08)
                        elif lean < -0.5:
                            w.shift(a.id, -0.08)

    def sys_mediation(self):
        living = self.living
        for a in living:
            for b in living:
                if b.id <= a.id:
                    continue
                if a.feel(b.id) < -0.4 and b.feel(a.id) < -0.4 and self.rng.random() < 0.12:
                    peacemakers = [w for w in living
                                   if w.id not in (a.id, b.id)
                                   and w.feel(a.id) > 0.3 and w.feel(b.id) > 0.3]
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
            has_child = any(
                ch.alive and ch.parent_ids is not None
                and set(ch.parent_ids) == {c.id, partner.id}
                for ch in self.chars
            )
            if has_child:
                continue
            if self.rng.random() < 0.008:
                self._birth(c, partner)

    def sys_growing_up(self):
        for c in self.living:
            if c.childhood and c.born_at is not None:
                if self.tick - c.born_at >= CHILDHOOD_TICKS:
                    c.childhood = False
                    ev = self.emit("COMING_OF_AGE", (c.id,), 0.5)
                    self.remember(c, ev)
                    if c.parent_ids:
                        for pid in c.parent_ids:
                            if pid < len(self.chars) and self.chars[pid].alive:
                                self.chars[pid].shift(c.id, 0.1)
            elif not c.childhood and not c.elder:
                if self.tick - c.joined_at >= ELDER_TICKS:
                    c.elder = True
                    for other in self.living:
                        if other.id != c.id:
                            other.shift(c.id, 0.04)  # elders earn quiet respect

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
        # Debts die with the person on both sides.
        # A creditor who outlives their debtor feels a strange unresolved
        # lightness — the debt is gone, but by the wrong door.
        for debt in c.debts.values():
            creditor = self.chars[debt.creditor]
            if creditor.alive:
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
            parent_ids=(a.id, b.id),
        )
        child.affinity[a.id] = 0.8
        child.affinity[b.id] = 0.8
        for ch in self.living:
            if ch.id not in (a.id, b.id):
                # a child grows up hearing their parents' stories:
                # inherit a mild version of each parent's lean toward neighbors
                parent_lean = (a.feel(ch.id) + b.feel(ch.id)) / 2 * 0.3
                child.affinity[ch.id] = max(-0.25, min(0.25,
                    parent_lean + self.rng.uniform(-0.1, 0.1)))
                ch.affinity[new_id] = self.rng.uniform(0.0, 0.15)
        a.affinity[new_id] = 0.85
        b.affinity[new_id] = 0.85
        self.chars.append(child)
        ev = self.emit("BIRTH", (new_id, a.id, b.id), 0.8)
        self.remember(child, ev)
        self.remember(a, ev)
        self.remember(b, ev)
