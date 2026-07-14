"""The narrator. It turns the fabula into a syuzhet.

Nothing here invents anything. The narrator reads the event log, picks
the threads worth telling (reversals, betrayals, reconciliations) and
renders them with templates. If the chronicle says the tale had grown
in the telling, it is because the simulation recorded the distortion.
"""

import random

from .model import TICKS_PER_SEASON, season_index, year_of
from .names import VILLAGE_NAMES

ARC_KINDS = {"GIFT", "REFUSAL", "OFFENSE", "QUARREL", "MEDIATION",
             "REPAYMENT", "INGRATITUDE", "RESENTMENT"}

TEXT = {
    "en": {
        "seasons": ("spring", "summer", "autumn", "winter"),
        "traits": {
            "diligence": ("tireless", "idle"),
            "generosity": ("open-handed", "tight-fisted"),
            "pride": ("proud", "humble"),
            "openness": ("talkative", "reserved"),
        },
        "intro": ["{name} was {adjs}.",
                  "{name}, {adjs}, was known to everyone."],
        "and": "and",
        "opening": ["It began in {season}.",
                    "The first anyone knew of it was in {season}."],
        "later_season": ["{season} came.", "By then it was {season}."],
        "soon_after": ["Not many days passed.", "Soon afterwards."],
        "GIFT": ["When {b}'s stores ran low, {a} filled the basket without being asked.",
                 "{a} shared bread with {b} in a lean stretch, and it was not forgotten."],
        "REFUSAL": ["{a} went hungry to {b}'s door and came back with nothing.",
                    "{b} turned {a} away empty-handed, and the whole village felt colder for it."],
        "OFFENSE": ["Word reached {a} that {b} had been speaking of the matter behind closed doors.",
                    "Someone let {a} know what {b} had been saying."],
        "QUARREL": ["{a} and {b} quarreled where everyone could hear, and the village pretended not to listen.",
                    "It came to hard words between {a} and {b}, in the open street."],
        "MEDIATION": ["{c} sat them both at one table and would not let either leave angry. Something loosened.",
                      "It took {c}, whom they both trusted, to make them speak again."],
        "REPAYMENT": ["{a} had not forgotten the old kindness, and when want came to {b}'s house, it was returned without a word about it.",
                      "The bread {b} once gave came back to {b}'s own door, and it was {a} who carried it."],
        "INGRATITUDE": ["{a} had once filled {b}'s basket; when {a}'s own ran empty, {b}'s door stayed shut. The village keeps accounts no ledger ever sees, and that one was entered in every head in it.",
                        "{b} owed {a} the kind of debt nobody writes down, and paid it with a closed door. Nobody said anything. Everybody counted it."],
        "RESENTMENT": ["The favor sat heavy on {a}. It is a hard thing to owe, and {a} took to avoiding {b}'s eye.",
                       "{a} had never returned what {b} once gave, and the owing curdled, the way gratitude does when it is carried too long."],
        "carried_by": " It was {c} who carried the tale.",
        "grown": " The tale had grown in the telling.",
        "repeat_one": "It happened once more after that.",
        "repeat_many": "It happened {n} more times after that, as if grudges kept a calendar of their own.",
        "repeat_good_one": "And it happened again, quietly, when it was needed.",
        "repeat_good_many": "And it happened {n} more times, without anyone making a fuss of it; kindness keeps a calendar too.",
        "repeat_endless": "And so it went on, season after season, until counting lost its point.",
        "repeat_good_endless": "And so it went on, season after season; some things do not need remarking to continue.",
        "close_relapse": "The peace that was made did not keep; some cracks want to stay open.",
        "close_broken": "No one mended it. By the end they passed each other without a word.",
        "close_uneasy": "An uneasy peace held between them, thin as spring ice.",
        "close_mended": "Whatever had been broken, they mended it better than new.",
        "close_warm": "They were lucky in each other, and they knew it.",
        "title_reconciliation": "{a} and {b}: a reconciliation",
        "title_estrangement": "{a} and {b}: an estrangement",
        "title_feud": "{a} and {b}: a feud",
        "title_bond": "{a} and {b}: a friendship",
        "title_open": "{a} and {b}: an unfinished business",
        "title_debt": "{a} and {b}: a debt unpaid",
        "chronicle_title": "The Chronicle of {village}",
        "prologue": ("{village} held {n} souls, and this record covers {days} days of them. "
                     "Nothing in it was invented; it was only watched, and told."),
        "pride_note": "{count} times, someone in {village} went hungry rather than ask for help. Pride is its own kind of famine.",
        "debt_note": "When the record closes, {count} favors in {village} had still not been returned. The village kept those accounts in no book, which is why none of them were ever lost.",
        "epilogue": ("When the record ends, {a} and {b} were as close as two people get in {village}; "
                     "{c} and {d} still were not speaking."),
        "colophon": "*(world seed {seed} — run it again and the same things will happen, in the same order, to the same people)*",
    },
    "es": {
        "seasons": ("la primavera", "el verano", "el otoño", "el invierno"),
        "seasons_in": ("primavera", "verano", "otoño", "invierno"),
        "traits": {
            "diligence": (("incansable", "incansable"), ("holgazán", "holgazana")),
            "generosity": (("desprendido", "desprendida"), ("agarrado", "agarrada")),
            "pride": (("orgulloso", "orgullosa"), ("humilde", "humilde")),
            "openness": (("parlanchín", "parlanchina"), ("reservado", "reservada")),
        },
        "intro": ["{name} era {adjs}.",
                  "A {name}, {adjs}, la conocía todo el mundo."],
        "intro_m": ["{name} era {adjs}.",
                    "A {name}, {adjs}, lo conocía todo el mundo."],
        "and": "y",
        "opening": ["Todo empezó en {season}.",
                    "Lo primero que se supo fue en {season}."],
        "later_season": ["Llegó {season}.", "Para entonces ya era {season}."],
        "soon_after": ["No pasaron muchos días.", "Poco después."],
        "GIFT": ["Cuando a {b} se le vació la despensa, {a} le llenó el cesto sin que nadie se lo pidiera.",
                 "{a} compartió el pan con {b} en una mala racha, y no se olvidó."],
        "REFUSAL": ["{a} llamó con hambre a la puerta de {b} y volvió con las manos vacías.",
                    "{b} despidió a {a} sin nada, y toda la aldea se sintió más fría."],
        "OFFENSE": ["A {a} le llegó el cuento de que {b} andaba hablando del asunto a puerta cerrada.",
                    "Alguien se encargó de que {a} supiera lo que {b} iba diciendo."],
        "QUARREL": ["{a} y {b} discutieron donde todos podían oírlos, y la aldea fingió no escuchar.",
                    "Entre {a} y {b} hubo palabras mayores, en mitad de la calle."],
        "MEDIATION": ["{c} los sentó a los dos a la misma mesa y no dejó que ninguno se levantara enfadado. Algo se aflojó.",
                      "Hizo falta {c}, de quien ambos se fiaban, para que volvieran a hablarse."],
        "REPAYMENT": ["{a} no había olvidado aquel favor, y cuando la necesidad llamó a casa de {b}, lo devolvió sin decir una palabra.",
                      "El pan que {b} dio un día volvió a su propia puerta, y fue {a} quien lo trajo."],
        "INGRATITUDE": ["{a} le había llenado el cesto a {b} una vez; cuando el suyo quedó vacío, la puerta de {b} no se abrió. La aldea lleva cuentas que ningún libro ve, y esa quedó apuntada en todas las cabezas.",
                        "{b} le debía a {a} una de esas deudas que nadie escribe, y la pagó con la puerta cerrada. Nadie dijo nada. Todos la contaron."],
        "RESENTMENT": ["El favor le pesaba a {a}. Deber es cosa dura, y {a} empezó a esquivarle la mirada a {b}.",
                       "{a} nunca devolvió lo que {b} le dio un día, y la deuda se agrió, como se agria la gratitud cuando se carga demasiado tiempo."],
        "carried_by": " Fue {c} quien trajo el cuento.",
        "grown": " El cuento había engordado por el camino.",
        "repeat_one": "Volvió a pasar una vez más.",
        "repeat_many": "Volvió a pasar {n} veces más, como si los rencores llevaran su propio calendario.",
        "repeat_good_one": "Y volvió a pasar, sin ruido, cuando hizo falta.",
        "repeat_good_many": "Y volvió a pasar {n} veces más, sin que nadie le diera importancia; también la bondad lleva su calendario.",
        "repeat_endless": "Y así siguió, estación tras estación, hasta que contar dejó de tener sentido.",
        "repeat_good_endless": "Y así siguió, estación tras estación; hay cosas que no necesitan que nadie las señale para continuar.",
        "close_relapse": "La paz que se hizo no se sostuvo; hay grietas que quieren seguir abiertas.",
        "close_broken": "Nadie lo arregló. Al final pasaban el uno junto al otro sin mediar palabra.",
        "close_uneasy": "Quedó entre ellos una paz incómoda, fina como el hielo de marzo.",
        "close_mended": "Lo que se había roto, lo remendaron mejor que nuevo.",
        "close_warm": "Tuvieron suerte el uno con el otro, y lo sabían.",
        "title_reconciliation": "{a} y {b}: una reconciliación",
        "title_estrangement": "{a} y {b}: un distanciamiento",
        "title_feud": "{a} y {b}: una enemistad",
        "title_bond": "{a} y {b}: una amistad",
        "title_open": "{a} y {b}: un asunto sin cerrar",
        "title_debt": "{a} y {b}: una deuda impagada",
        "chronicle_title": "Crónica de {village}",
        "prologue": ("En {village} vivían {n} almas, y este registro abarca {days} de sus días. "
                     "Nada de lo que sigue es inventado; solo se miró, y se contó."),
        "pride_note": "{count} veces alguien en {village} pasó hambre antes que pedir ayuda. El orgullo es otra clase de hambruna.",
        "debt_note": "Al cerrarse el registro quedaban en {village} {count} favores sin devolver. Esas cuentas no las llevaba la aldea en libro alguno, y por eso no se perdió ninguna.",
        "epilogue": ("Cuando el registro se cierra, {a} y {b} eran lo más parecido a inseparables que hay en {village}; "
                     "{c} y {d} seguían sin hablarse."),
        "colophon": "*(semilla del mundo: {seed} — vuelve a ejecutarla y pasarán las mismas cosas, en el mismo orden, a la misma gente)*",
    },
}


class Narrator:
    def __init__(self, world, lang: str = "en", seed: int = 0):
        self.world = world
        self.lang = lang
        self.t = TEXT[lang]
        self.rng = random.Random(seed ^ 0xFAB)
        self.village = self.rng.choice(VILLAGE_NAMES[lang])
        self._introduced: set = set()

    # ------------------------------------------------------------------
    # picking what deserves telling

    def arcs(self):
        pairs: dict = {}
        for ev in self.world.events:
            if ev.kind in ARC_KINDS:
                key = frozenset(ev.actors[:2])
                pairs.setdefault(key, []).append(ev)
        scored = []
        for key, events in pairs.items():
            if len(events) < 2:
                continue
            scored.append((self.drama(events), key, events))
        scored.sort(key=lambda item: -item[0])
        chosen, appearances = [], {}
        for score, key, events in scored:
            if score < 1.0 or len(chosen) == 3:
                break
            if any(appearances.get(cid, 0) >= 2 for cid in key):
                continue  # no one gets to star in every story
            for cid in key:
                appearances[cid] = appearances.get(cid, 0) + 1
            chosen.append((key, events))
        return chosen

    def drama(self, events):
        score = sum(abs(ev.valence) for ev in events)
        means = [sum(ev.data["affinity"]) / 2 for ev in events if "affinity" in ev.data]
        poles = [1 if m > 0.1 else -1 for m in means if abs(m) > 0.1]
        flips = sum(1 for x, y in zip(poles, poles[1:]) if x != y)
        score += 2.0 * flips
        kinds = {ev.kind for ev in events}
        score += 0.75 * len(kinds)  # varied arcs read better than one scene on repeat
        if "MEDIATION" in kinds:
            score += 1.5
        if "GIFT" in kinds and ("QUARREL" in kinds or "OFFENSE" in kinds):
            score += 1.0
        if "INGRATITUDE" in kinds:
            score += 1.5  # a kindness betrayed is the oldest story there is
        if "RESENTMENT" in kinds or "REPAYMENT" in kinds:
            score += 1.0  # what a debt does to people, either way it goes
        return score

    # ------------------------------------------------------------------
    # rendering helpers

    def pick(self, key, **fields):
        return self.rng.choice(self.t[key]).format(**fields)

    def season_name(self, tick):
        return self.t["seasons"][season_index(tick)]

    def name(self, cid):
        return self.world.char(cid).name

    def adjectives(self, char):
        traits = {
            "diligence": char.diligence, "generosity": char.generosity,
            "pride": char.pride, "openness": char.openness,
        }
        chosen = sorted(traits, key=lambda k: -abs(traits[k] - 0.5))[:2]
        out = []
        for key in chosen:
            pair = self.t["traits"][key]
            adj = pair[0] if traits[key] >= 0.5 else pair[1]
            if isinstance(adj, tuple):  # gendered language
                adj = adj[0] if char.gender == "m" else adj[1]
            out.append(adj)
        return out

    def introduce(self, char):
        if char.id in self._introduced:
            return None
        self._introduced.add(char.id)
        adj1, adj2 = self.adjectives(char)
        conj = self.t["and"]
        if self.lang == "es" and (adj2[:1] == "i" or adj2[:2] == "hi"):
            conj = "e"
        key = "intro_m" if (self.lang == "es" and char.gender == "m"
                            and "intro_m" in self.t) else "intro"
        return self.pick(key, name=char.name, adjs=f"{adj1} {conj} {adj2}")

    def connector(self, prev, ev):
        if prev is None:
            bare = self.t.get("seasons_in", self.t["seasons"])
            return self.pick("opening", season=bare[season_index(ev.tick)])
        prev_season = (prev.tick // TICKS_PER_SEASON)
        if ev.tick // TICKS_PER_SEASON != prev_season:
            text = self.pick("later_season", season=self.season_name(ev.tick))
            return text[0].upper() + text[1:]
        return self.pick("soon_after")

    def beat(self, ev):
        a, b = ev.actors[0], ev.actors[1]
        fields = {"a": self.name(a), "b": self.name(b)}
        if ev.kind == "MEDIATION":
            fields["c"] = self.name(ev.data["mediator"])
        text = self.pick(ev.kind, **fields)
        if ev.kind == "OFFENSE":
            if ev.data.get("via") is not None:
                text += self.t["carried_by"].format(c=self.name(ev.data["via"]))
            if ev.data.get("distorted"):
                text += self.t["grown"]
        return text

    # ------------------------------------------------------------------
    # assembling the chronicle

    def arc_title(self, key, events):
        a_id, b_id = sorted(key)
        a, b = self.world.char(a_id), self.world.char(b_id)
        first = sum(events[0].data.get("affinity", (0, 0))) / 2
        final = (a.feel(b.id) + b.feel(a.id)) / 2
        kinds = {ev.kind for ev in events}
        if final > 0.2 and (first < -0.05 or "MEDIATION" in kinds or "QUARREL" in kinds):
            shape = "reconciliation"
        elif final < -0.1 and kinds & {"INGRATITUDE", "RESENTMENT"} and "REPAYMENT" not in kinds:
            shape = "debt"
        elif final < -0.3 and first > 0.05:
            shape = "estrangement"
        elif final < -0.3:
            shape = "feud"
        elif final > 0.2:
            shape = "bond"
        else:
            shape = "open"
        return self.t["title_" + shape].format(a=a.name, b=b.name), final, kinds

    def closing(self, final, kinds):
        if final < -0.35:
            if "MEDIATION" in kinds:
                return self.t["close_relapse"]
            return self.t["close_broken"]
        if final < 0.2:
            return self.t["close_uneasy"]
        if kinds & {"QUARREL", "OFFENSE", "REFUSAL", "MEDIATION"}:
            return self.t["close_mended"]
        return self.t["close_warm"]

    def tell_arc(self, key, events):
        title, final, kinds = self.arc_title(key, events)
        lines = ["## " + title, ""]
        intro = []
        for cid in sorted(key):
            sentence = self.introduce(self.world.char(cid))
            if sentence:
                intro.append(sentence)
        if intro:
            lines.append(" ".join(intro))
            lines.append("")
        body, prev, told_kinds, skipped = [], None, {}, []
        for ev in events:
            # each kind of scene is told once; repeats become a single note
            if ev.kind in told_kinds and ev.kind != "MEDIATION":
                skipped.append(ev)
                continue
            told_kinds[ev.kind] = True
            body.append(self.connector(prev, ev) + " " + self.beat(ev))
            prev = ev
        if skipped:
            tone = "repeat_good" if sum(ev.valence for ev in skipped) > 0 else "repeat"
            if len(skipped) == 1:
                suffix = "_one"
            elif len(skipped) <= 6:
                suffix = "_many"
            else:
                suffix = "_endless"
            body.append(self.t[tone + suffix].format(n=len(skipped)))
        lines.append(" ".join(body))
        lines.append("")
        lines.append(self.closing(final, kinds))
        return "\n".join(lines)

    def chronicle(self):
        w = self.world
        parts = ["# " + self.t["chronicle_title"].format(village=self.village), ""]
        parts.append(self.t["prologue"].format(
            village=self.village, n=len(w.chars), days=w.tick))
        pride_count = sum(1 for ev in w.events
                          if ev.kind == "HARDSHIP" and ev.data.get("pride"))
        if pride_count >= 3:
            parts.append("")
            parts.append(self.t["pride_note"].format(count=pride_count, village=self.village))
        debt_count = sum(len(c.debts) for c in w.chars)
        if debt_count >= 3:
            parts.append("")
            parts.append(self.t["debt_note"].format(count=debt_count, village=self.village))
        parts.append("")
        arcs = self.arcs()
        for key, events in arcs:
            parts.append(self.tell_arc(key, events))
            parts.append("")
        best, worst = self.extremes()
        if best and worst:
            parts.append(self.t["epilogue"].format(
                a=self.name(best[0]), b=self.name(best[1]),
                c=self.name(worst[0]), d=self.name(worst[1]),
                village=self.village))
            parts.append("")
        parts.append(self.t["colophon"].format(seed=w.seed))
        parts.append("")
        return "\n".join(parts)

    def extremes(self):
        best = worst = None
        best_v, worst_v = -10.0, 10.0
        for a in self.world.chars:
            for b in self.world.chars:
                if b.id <= a.id:
                    continue
                mutual = a.feel(b.id) + b.feel(a.id)
                if mutual > best_v:
                    best, best_v = (a.id, b.id), mutual
                if mutual < worst_v:
                    worst, worst_v = (a.id, b.id), mutual
        return best, worst
