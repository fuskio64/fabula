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


class World:
    def __init__(self, seed: int = 0, people: int = 10):
        self.seed = seed
        self.rng = random.Random(seed)
        self.tick = 0
        self.events: list[Event] = []
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
        self.sys_need_and_gift()
        self.sys_gossip()
        self.sys_quarrel()
        self.sys_mediation()
        if (self.tick + 1) % TICKS_PER_SEASON == 0:
            self.sys_festival()
        self.tick += 1

    # ------------------------------------------------------------------
    # systems

    def sys_harvest(self):
        yield_now = SEASON_YIELD[season_index(self.tick)]
        for c in self.chars:
            c.food += yield_now * (0.55 + 0.8 * c.diligence) * self.rng.uniform(0.7, 1.3)
            c.food = max(0.0, c.food - 1.0)  # everyone eats

    def sys_need_and_gift(self):
        for c in self.chars:
            if c.food >= FOOD_NEED:
                continue
            donors = [d for d in self.chars if d.id != c.id and d.food > FOOD_SURPLUS]
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
            donor = max(donors, key=lambda d: c.feel(d.id) + self.rng.uniform(-0.1, 0.1))
            willing = donor.generosity * 0.9 + donor.feel(c.id) * 0.5 + self.rng.uniform(-0.25, 0.25)
            if willing > 0.35:
                amount = min(3.0, donor.food - 3.5)
                donor.food -= amount
                c.food += amount
                ev = self.emit("GIFT", (donor.id, c.id), 0.6)
                c.shift(donor.id, 0.15)
                donor.shift(c.id, 0.08)
                self.remember(c, ev)
                self.remember(donor, ev)
                self.snapshot(ev, donor, c)
            else:
                ev = self.emit("REFUSAL", (c.id, donor.id), -0.7)
                c.shift(donor.id, -0.3)
                self.remember(c, ev)                 # the sting
                self.remember(donor, ev, valence=-0.2)  # a twinge of guilt
                self.snapshot(ev, c, donor)

    def sys_gossip(self):
        for _ in range(max(1, len(self.chars) // 3)):
            a, b = self.rng.sample(self.chars, 2)
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
        heard = max(-1.0, min(1.0, m.valence * self.rng.uniform(0.8, 1.3)))
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
            if listener.feel(wronged) > 0.35:
                listener.shift(wrongdoer, -0.1)  # quietly taking sides

    def sys_quarrel(self):
        for a in self.chars:
            for b in self.chars:
                if b.id <= a.id:
                    continue
                pair = (a.id, b.id)
                if self.tick - self._last_quarrel.get(pair, -99) < 15:
                    continue
                if min(a.feel(b.id), b.feel(a.id)) < -0.5 and self.rng.random() < 0.12:
                    self._last_quarrel[pair] = self.tick
                    ev = self.emit("QUARREL", (a.id, b.id), -0.8)
                    a.shift(b.id, -0.1)
                    b.shift(a.id, -0.1)
                    self.remember(a, ev)
                    self.remember(b, ev)
                    self.snapshot(ev, a, b)
                    for w in self.chars:  # the village takes sides
                        if w.id in (a.id, b.id):
                            continue
                        lean = w.feel(a.id) - w.feel(b.id)
                        if lean > 0.5:
                            w.shift(b.id, -0.08)
                        elif lean < -0.5:
                            w.shift(a.id, -0.08)

    def sys_mediation(self):
        for a in self.chars:
            for b in self.chars:
                if b.id <= a.id:
                    continue
                if a.feel(b.id) < -0.4 and b.feel(a.id) < -0.4 and self.rng.random() < 0.12:
                    peacemakers = [w for w in self.chars
                                   if w.id not in (a.id, b.id)
                                   and w.feel(a.id) > 0.3 and w.feel(b.id) > 0.3]
                    if not peacemakers:
                        continue
                    w = self.rng.choice(peacemakers)
                    ev = self.emit("MEDIATION", (a.id, b.id), 0.7, mediator=w.id)
                    a.affinity[b.id] = -0.05
                    b.affinity[a.id] = -0.05
                    a.shift(w.id, 0.15)
                    b.shift(w.id, 0.15)
                    self.remember(a, ev)
                    self.remember(b, ev)
                    self.remember(w, ev)
                    self.snapshot(ev, a, b)

    def sys_festival(self):
        self.emit("FESTIVAL", tuple(c.id for c in self.chars), 0.3,
                  season=season_index(self.tick))
        for a in self.chars:
            for b_id in list(a.affinity):
                a.shift(b_id, 0.03)
        # someone always talks too much at a festival
        for s in self.rng.sample(self.chars, k=min(2, len(self.chars))):
            listeners = [c for c in self.chars if c.id != s.id]
            for listener in self.rng.sample(listeners, k=min(4, len(listeners))):
                self.tell(s, listener, public=True)
