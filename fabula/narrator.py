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
             "REPAYMENT", "INGRATITUDE", "RESENTMENT", "BOND", "WIDOWING"}

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
        "BOND": ["{a} and {b} chose each other before the season turned. The village knew before either of them said a word about it.",
                 "What had grown between {a} and {b} became something declared. They shared bread and hearth after that."],
        "WIDOWING": ["{a} outlived {b}. The village did not leave {a} alone with it, which is how grief is carried in a place like that.",
                     "When {b} died, {a} lost more than a person loses when what remains is only loneliness."],
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
        "close_widowed": "They had been lucky in each other. The ending was a sad one, but it was a sadness the village recognized.",
        "title_reconciliation": "{a} and {b}: a reconciliation",
        "title_estrangement": "{a} and {b}: an estrangement",
        "title_feud": "{a} and {b}: a feud",
        "title_bond": "{a} and {b}: a friendship",
        "title_love": "{a} and {b}: a love",
        "title_open": "{a} and {b}: an unfinished business",
        "title_debt": "{a} and {b}: a debt unpaid",
        "chronicle_title": "The Chronicle of {village}",
        "prologue": ("{village} held {n} souls at the opening of this record, "
                     "and it covers {days} days of them. "
                     "Nothing in it was invented; it was only watched, and told."),
        "pride_note": "{count} times, someone in {village} went hungry rather than ask for help. Pride is its own kind of famine.",
        "debt_note": "When the record closes, {count} favors in {village} had still not been returned. The village kept those accounts in no book, which is why none of them were ever lost.",
        "deaths_note_1": "One soul in {village} did not live through these years. A village carries its dead quietly, which is how the dead end up carrying the village.",
        "deaths_note_n": "{count} souls in {village} did not live through these years. A village carries its dead quietly, which is how the dead end up carrying the village.",
        "arrivals_note_1": "One stranger came to {village} in this time. The village is always uncertain what to make of someone with no history.",
        "arrivals_note_n": "{count} strangers came to {village} in this time. The village is always uncertain what to make of someone with no history.",
        "bonds_note_1": "One bond was made in {village} in this time. Most lasting things begin without anyone marking the moment.",
        "bonds_note_n": "{count} bonds were made in {village} in this time. Most lasting things begin without anyone marking the moment.",
        "births_note_1": "One child was born in {village} in this time.",
        "births_note_n": "{count} children were born in {village} in this time.",
        "died_starvation": "{a} did not outlive this chronicle. A long winter took them before the account closed.",
        "died_misfortune": "{a} did not outlive this chronicle; a sudden blow, when there was nothing left to absorb it.",
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
        "BOND": ["{a} y {b} se eligieron mutuamente antes de que cambiara la estación. La aldea lo supo antes de que ninguno de los dos dijera una palabra al respecto.",
                 "Lo que había crecido entre {a} y {b} se convirtió en algo declarado. Compartieron pan y lumbre a partir de entonces."],
        "WIDOWING": ["{a} sobrevivió a {b}. La aldea no dejó a {a} solo con ello, que es como se lleva el duelo en un lugar así.",
                     "Cuando {b} murió, {a} perdió algo que va más allá de lo que se pierde cuando lo que queda es solo la soledad."],
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
        "close_widowed": "Habían tenido suerte el uno con el otro. El final fue triste, pero era una tristeza que la aldea reconocía.",
        "title_reconciliation": "{a} y {b}: una reconciliación",
        "title_estrangement": "{a} y {b}: un distanciamiento",
        "title_feud": "{a} y {b}: una enemistad",
        "title_bond": "{a} y {b}: una amistad",
        "title_love": "{a} y {b}: un amor",
        "title_open": "{a} y {b}: un asunto sin cerrar",
        "title_debt": "{a} y {b}: una deuda impagada",
        "chronicle_title": "Crónica de {village}",
        "prologue": ("En {village} vivían {n} almas al abrir este registro, "
                     "y abarca {days} de sus días. "
                     "Nada de lo que sigue es inventado; solo se miró, y se contó."),
        "pride_note": "{count} veces alguien en {village} pasó hambre antes que pedir ayuda. El orgullo es otra clase de hambruna.",
        "debt_note": "Al cerrarse el registro quedaban en {village} {count} favores sin devolver. Esas cuentas no las llevaba la aldea en libro alguno, y por eso no se perdió ninguna.",
        "deaths_note_1": "Una persona de {village} no sobrevivió a estos años. Una aldea lleva a sus muertos en silencio, que es la manera en que los muertos acaban cargando con la aldea.",
        "deaths_note_n": "{count} personas de {village} no sobrevivieron a estos años. Una aldea lleva a sus muertos en silencio, que es la manera en que los muertos acaban cargando con la aldea.",
        "arrivals_note_1": "Un forastero llegó a {village} en este tiempo. La aldea nunca sabe bien qué hacer con alguien que no tiene historia.",
        "arrivals_note_n": "{count} forasteros llegaron a {village} en este tiempo. La aldea nunca sabe bien qué hacer con alguien que no tiene historia.",
        "bonds_note_1": "Un vínculo se forjó en {village} en este tiempo. La mayoría de las cosas duraderas empiezan sin que nadie señale el momento.",
        "bonds_note_n": "{count} vínculos se forjaron en {village} en este tiempo. La mayoría de las cosas duraderas empiezan sin que nadie señale el momento.",
        "births_note_1": "Un niño nació en {village} en este tiempo.",
        "births_note_n": "{count} niños nacieron en {village} en este tiempo.",
        "died_starvation": "{a} no sobrevivió a esta crónica. Un invierno largo puso fin a sus días antes de que el relato cerrara.",
        "died_misfortune": "{a} no sobrevivió a esta crónica; un golpe repentino, cuando ya no quedaba nada con que resistirlo.",
        "epilogue": ("Cuando el registro se cierra, {a} y {b} eran lo más parecido a inseparables que hay en {village}; "
                     "{c} y {d} seguían sin hablarse."),
        "colophon": "*(semilla del mundo: {seed} — vuelve a ejecutarla y pasarán las mismas cosas, en el mismo orden, a la misma gente)*",
    },
    "fr": {
        "seasons": ("le printemps", "l'été", "l'automne", "l'hiver"),
        "seasons_in": ("au printemps", "en été", "en automne", "en hiver"),
        "traits": {
            "diligence": (("infatigable", "infatigable"), ("fainéant", "fainéante")),
            "generosity": (("généreux", "généreuse"), ("avare", "avare")),
            "pride": (("fier", "fière"), ("humble", "humble")),
            "openness": (("bavard", "bavarde"), ("taciturne", "taciturne")),
        },
        "intro": ["{name} était {adjs}.",
                  "Tout le monde connaissait {name}, {adjs}."],
        "and": "et",
        "opening": ["Tout commença {season}.",
                    "On en entendit parler pour la première fois {season}."],
        "later_season": ["{season} arriva.", "C'était déjà {season}."],
        "soon_after": ["Les jours qui suivirent furent courts.", "Peu après."],
        "GIFT": ["Quand les réserves de {b} vinrent à manquer, {a} remplit le panier sans qu'on le lui demande.",
                 "{a} partagea son pain avec {b} dans les mauvais temps, et {b} ne l'oublia pas."],
        "REFUSAL": ["{a} frappa à la porte de {b} le ventre creux et repartit les mains vides.",
                    "{b} renvoya {a} sans rien, et tout le village en fut refroidi."],
        "OFFENSE": ["Il parvint aux oreilles de {a} que {b} parlait de l'affaire derrière des portes closes.",
                    "Quelqu'un se chargea de rapporter à {a} ce que {b} allait disant."],
        "QUARREL": ["{a} et {b} se disputèrent là où tout le monde pouvait entendre, et le village fit semblant de ne pas écouter.",
                    "Il y eut des mots durs entre {a} et {b}, en pleine rue."],
        "MEDIATION": ["{c} les fit asseoir à la même table et ne laissa ni l'un ni l'autre repartir en colère. Quelque chose se dénoua.",
                      "Il fallut {c}, en qui ils avaient tous deux confiance, pour qu'ils se parlent de nouveau."],
        "REPAYMENT": ["{a} n'avait pas oublié l'ancienne gentillesse, et quand le besoin frappa chez {b}, il la rendit sans un mot.",
                      "Le pain que {b} avait donné revint à sa propre porte, porté par {a}."],
        "INGRATITUDE": ["{a} avait rempli le panier de {b} ; quand le sien se vida, la porte de {b} resta close. Le village tient des comptes qu'aucun registre ne voit, et celui-là fut inscrit dans toutes les mémoires.",
                        "{b} devait à {a} le genre de dette que personne n'écrit, et la solda par une porte fermée. Personne ne dit rien. Tout le monde compta."],
        "RESENTMENT": ["La faveur pesait à {a}. C'est chose difficile que de devoir, et {a} se mit à éviter le regard de {b}.",
                       "{a} n'avait jamais rendu ce que {b} lui avait donné, et la dette s'aigrit, comme la gratitude s'aigrit quand on la porte trop longtemps."],
        "BOND": ["{a} et {b} se choisirent avant que la saison ne tourne. Le village le sut avant qu'ils en disent un mot.",
                 "Ce qui avait grandi entre {a} et {b} devint quelque chose d'assumé. Ils partagèrent pain et foyer après cela."],
        "WIDOWING": ["{a} survécut à {b}. Le village ne laissa pas {a} seul avec cela, c'est ainsi qu'on porte le deuil en pareil endroit.",
                     "Quand {b} mourut, {a} perdit quelque chose que l'on ne perd pas de la même façon que le reste."],
        "carried_by": " C'est {c} qui porta le récit.",
        "grown": " Le récit avait grossi en chemin.",
        "repeat_one": "Cela se reproduisit une fois encore.",
        "repeat_many": "Cela se reproduisit {n} fois encore, comme si les rancœurs tenaient leur propre calendrier.",
        "repeat_good_one": "Et cela se reproduisit, discrètement, quand il le fallut.",
        "repeat_good_many": "Et cela se reproduisit {n} fois encore, sans que personne en fasse grand cas ; la bonté aussi tient son calendrier.",
        "repeat_endless": "Et ainsi de suite, saison après saison, jusqu'à ce que compter perde son sens.",
        "repeat_good_endless": "Et ainsi de suite, saison après saison ; certaines choses n'ont pas besoin d'être remarquées pour continuer.",
        "close_relapse": "La paix qui fut faite ne tint pas ; certaines fissures veulent rester ouvertes.",
        "close_broken": "Personne ne raccommoda rien. À la fin, ils se croisaient sans un mot.",
        "close_uneasy": "Une paix précaire s'installa entre eux, mince comme la glace de mars.",
        "close_mended": "Ce qui s'était brisé, ils le recoussirent mieux qu'avant.",
        "close_warm": "Ils eurent de la chance l'un envers l'autre, et ils le savaient.",
        "close_widowed": "Ils avaient eu de la chance l'un envers l'autre. La fin fut triste, mais c'était une tristesse que le village reconnut.",
        "title_reconciliation": "{a} et {b} : une réconciliation",
        "title_estrangement": "{a} et {b} : un éloignement",
        "title_feud": "{a} et {b} : une inimitié",
        "title_bond": "{a} et {b} : une amitié",
        "title_love": "{a} et {b} : une histoire",
        "title_open": "{a} et {b} : une affaire non réglée",
        "title_debt": "{a} et {b} : une dette impayée",
        "chronicle_title": "Chronique de {village}",
        "prologue": ("{village} comptait {n} âmes à l'ouverture de ce récit, "
                     "et il couvre {days} jours de leur vie. "
                     "Rien n'y est inventé ; on a seulement regardé, et raconté."),
        "pride_note": "{count} fois, quelqu'un à {village} préféra souffrir de la faim plutôt que de demander de l'aide. L'orgueil est une autre forme de famine.",
        "debt_note": "Quand le récit se ferme, {count} faveurs à {village} n'avaient pas encore été rendues. Le village ne les consignait dans aucun registre, c'est pourquoi aucune ne fut jamais perdue.",
        "deaths_note_1": "Une âme à {village} ne survécut pas à ces années. Un village porte ses morts en silence, c'est ainsi que les morts finissent par porter le village.",
        "deaths_note_n": "{count} âmes à {village} ne survécurent pas à ces années. Un village porte ses morts en silence, c'est ainsi que les morts finissent par porter le village.",
        "arrivals_note_1": "Un étranger arriva à {village} en ce temps. Le village ne sait jamais trop quoi faire de quelqu'un qui n'a pas d'histoire.",
        "arrivals_note_n": "{count} étrangers arrivèrent à {village} en ce temps. Le village ne sait jamais trop quoi faire de quelqu'un qui n'a pas d'histoire.",
        "bonds_note_1": "Un lien se noua à {village} en ce temps. La plupart des choses durables commencent sans que le moment soit marqué.",
        "bonds_note_n": "{count} liens se nouèrent à {village} en ce temps. La plupart des choses durables commencent sans que le moment soit marqué.",
        "births_note_1": "Un enfant naquit à {village} en ce temps.",
        "births_note_n": "{count} enfants naquirent à {village} en ce temps.",
        "died_starvation": "{a} ne survécut pas à cette chronique. Un long hiver l'emporta avant la clôture du récit.",
        "died_misfortune": "{a} ne survécut pas à cette chronique ; un coup soudain, quand il ne restait plus rien pour l'absorber.",
        "epilogue": ("Quand le récit se ferme, {a} et {b} étaient aussi proches que deux personnes peuvent l'être à {village} ; "
                     "{c} et {d} ne se parlaient toujours pas."),
        "colophon": "*(graine du monde : {seed} — lancez-la de nouveau et les mêmes choses arriveront, dans le même ordre, aux mêmes gens)*",
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
        max_arcs = max(3, self.world.tick // 96)
        chosen, appearances = [], {}
        for score, key, events in scored:
            if score < 1.0 or len(chosen) == max_arcs:
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
        if "BOND" in kinds:
            score += 2.5  # a bond formed is inherently dramatic
        if "WIDOWING" in kinds:
            score += 3.0  # love and loss: the oldest arc
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

    def death_cause(self, cid: int) -> str | None:
        """Return the cause of death for a character, or None if still living."""
        for ev in self.world.events:
            if ev.kind == "DEATH" and cid in ev.actors:
                return ev.data.get("cause", "starvation")
        return None

    # ------------------------------------------------------------------
    # assembling the chronicle

    def arc_title(self, key, events):
        a_id, b_id = sorted(key)
        a, b = self.world.char(a_id), self.world.char(b_id)
        first = sum(events[0].data.get("affinity", (0, 0))) / 2
        final = (a.feel(b.id) + b.feel(a.id)) / 2
        kinds = {ev.kind for ev in events}
        if "BOND" in kinds:
            shape = "love"
        elif final > 0.2 and (first < -0.05 or "MEDIATION" in kinds or "QUARREL" in kinds):
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
        if "BOND" in kinds and "WIDOWING" in kinds:
            return self.t["close_widowed"]
        if "BOND" in kinds:
            return self.t["close_warm"]
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
        # If one of the pair died, note it quietly after the closing.
        for cid in sorted(key):
            cause = self.death_cause(cid)
            if cause is not None:
                lines.append("")
                lines.append(self.t[f"died_{cause}"].format(a=self.name(cid)))
        return "\n".join(lines)

    def chronicle(self):
        w = self.world
        parts = ["# " + self.t["chronicle_title"].format(village=self.village), ""]
        parts.append(self.t["prologue"].format(
            village=self.village, n=self.world.initial_people, days=w.tick))

        pride_count = sum(1 for ev in w.events
                          if ev.kind == "HARDSHIP" and ev.data.get("pride"))
        if pride_count >= 3:
            parts.append("")
            parts.append(self.t["pride_note"].format(count=pride_count, village=self.village))

        debt_count = sum(len(c.debts) for c in w.chars)
        if debt_count >= 3:
            parts.append("")
            parts.append(self.t["debt_note"].format(count=debt_count, village=self.village))

        death_count = sum(1 for ev in w.events if ev.kind == "DEATH")
        if death_count >= 1:
            parts.append("")
            key = "deaths_note_1" if death_count == 1 else "deaths_note_n"
            parts.append(self.t[key].format(count=death_count, village=self.village))

        arrival_count = sum(1 for ev in w.events if ev.kind == "ARRIVAL")
        if arrival_count >= 1:
            parts.append("")
            key = "arrivals_note_1" if arrival_count == 1 else "arrivals_note_n"
            parts.append(self.t[key].format(count=arrival_count, village=self.village))

        bond_count = sum(1 for ev in w.events if ev.kind == "BOND")
        if bond_count >= 1:
            parts.append("")
            key = "bonds_note_1" if bond_count == 1 else "bonds_note_n"
            parts.append(self.t[key].format(count=bond_count, village=self.village))

        birth_count = sum(1 for ev in w.events if ev.kind == "BIRTH")
        if birth_count >= 1:
            parts.append("")
            key = "births_note_1" if birth_count == 1 else "births_note_n"
            parts.append(self.t[key].format(count=birth_count, village=self.village))

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
        for a in self.world.living:
            for b in self.world.living:
                if b.id <= a.id:
                    continue
                mutual = a.feel(b.id) + b.feel(a.id)
                if mutual > best_v:
                    best, best_v = (a.id, b.id), mutual
                if mutual < worst_v:
                    worst, worst_v = (a.id, b.id), mutual
        return best, worst
