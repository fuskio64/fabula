"""The fragments narrator.

Tells what the village carries in memory — not a crafted chronicle of what
happened, but the gossip record: who knew what, from whom, and how much it
changed in the telling. Uses the rumor and memory data the simulation already
tracks.

The chronicle's narrator is omniscient and selective. This narrator is a
village archivist who only knows what was passed on, and who cannot verify
what they've been told against what actually occurred. The records are
honest about that.

Supports all five chronicle languages.
"""

from .model import TICKS_PER_SEASON, season_index, year_of


_T = {
    "en": {
        "title":       "What {village} Carries",
        "intro":       ("*A record of the same events, but as they traveled.*  \n"
                        "*The chronicle tells what happened. "
                        "This tells what the village remembers — "
                        "which is not always the same thing.*"),
        "no_events":   ("*The stories in this run did not travel far enough to leave "
                        "a fragments record. Try a longer run or more people.*"),
        "section_of":  "Of {a} and {b}",
        "what_happened": "*{when}. What happened: {desc}.*",
        "no_firsthand": "No one who was there left a trace of remembering it.",
        "firsthand_one": "{name} was there. They remembered it as {valence}.",
        "firsthand_two_same": "Both {names} carried it firsthand and both remembered it as {valence}.",
        "firsthand_two_diff": "{names} were both there, and they did not remember it the same way: {remembered}.",
        "remembered_as": "{name} as {valence}",
        "reached_1":   "It reached one other person.",
        "reached_n":   "It reached {n} others.",
        "heard_from":  "{gap}, {name} heard it from {teller}. {note}",
        "heard_unknown": ("{gap}, {name} heard about it — "
                          "from whom exactly is not recorded. "
                          "They remembered it as {valence}."),
        "summary_held":    "*{mouths}, and the story held.*",
        "summary_flipped": ("*{mouths}, and the story had turned over. "
                             "What it was: {was}. "
                             "What the last ear received: {became}.*"),
        "summary_grew":    ("*{mouths}, and the story grew. "
                             "What it was: {was}. "
                             "What the last ear received: {became}.*"),
        "summary_shrank":  ("*{mouths}, and the story shrank. "
                             "What it was: {was}. "
                             "What the last ear received: {became}.*"),
        "one_telling": "One telling",
        "n_tellings":  "{n} tellings",
        "colophon":    ("*(world seed {seed} — "
                        "the same run of events, seen through the village's imperfect memory)*"),
        "events": {
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
        },
        "gap": {
            "same":   "that same day",
            "few":    "a few days later",
            "some":   "some days after",
            "weeks":  "a few weeks on",
            "season": "a season later",
            "later":  "some time later",
        },
        "distortion": {
            "intact":        "The story arrived intact.",
            "slight":        "The story shifted slightly in the telling.",
            "flip_to_bad":   "What had been a kindness arrived as a wrong. The meaning had reversed.",
            "flip_to_good":  "What had been a wrong arrived as a kindness. The meaning had reversed.",
            "grew_much":     "The story had grown considerably in the telling.",
            "grew":          "Something had been added. The story was larger than when it left.",
            "shrank_much":   "The story had shrunken considerably in the telling.",
            "shrank":        "Something had been lost. The story was smaller than when it left.",
        },
        "valence": {
            "very_good":  "something remarkable",
            "good":       "something good",
            "small_good": "a small kindness",
            "neutral":    "something unremarkable",
            "small_bad":  "a small wrong",
            "bad":        "something bad",
            "very_bad":   "something grave",
        },
        "and":     " and ",
        "year":    "year",
        "seasons": ("spring", "summer", "autumn", "winter"),
    },
    "es": {
        "title":       "Lo que lleva {village}",
        "intro":       ("*Un registro de los mismos hechos, pero tal como viajaron.*  \n"
                        "*La crónica dice lo que pasó. "
                        "Esto dice lo que la aldea recuerda — "
                        "que no siempre es lo mismo.*"),
        "no_events":   ("*Las historias de esta partida no viajaron lo suficiente como para dejar "
                        "un registro de fragmentos. Prueba una partida más larga o con más personas.*"),
        "section_of":  "De {a} y {b}",
        "what_happened": "*{when}. Lo que pasó: {desc}.*",
        "no_firsthand": "Nadie que estuviera allí dejó rastro de recordarlo.",
        "firsthand_one": "{name} estaba allí. Lo recordaba como {valence}.",
        "firsthand_two_same": "Tanto {names} lo llevaron de primera mano y los dos lo recordaban como {valence}.",
        "firsthand_two_diff": "{names} estaban los dos allí, y no lo recordaban igual: {remembered}.",
        "remembered_as": "{name} como {valence}",
        "reached_1":   "Llegó a una persona más.",
        "reached_n":   "Llegó a {n} personas más.",
        "heard_from":  "{gap}, {name} lo oyó de {teller}. {note}",
        "heard_unknown": ("{gap}, {name} se enteró de ello — "
                          "de quién exactamente no queda registrado. "
                          "Lo recordaba como {valence}."),
        "summary_held":    "*{mouths}, y la historia se mantuvo.*",
        "summary_flipped": ("*{mouths}, y la historia había dado la vuelta. "
                             "Lo que era: {was}. "
                             "Lo que recibió el último oído: {became}.*"),
        "summary_grew":    ("*{mouths}, y la historia creció. "
                             "Lo que era: {was}. "
                             "Lo que recibió el último oído: {became}.*"),
        "summary_shrank":  ("*{mouths}, y la historia menguó. "
                             "Lo que era: {was}. "
                             "Lo que recibió el último oído: {became}.*"),
        "one_telling": "Una transmisión",
        "n_tellings":  "{n} transmisiones",
        "colophon":    ("*(semilla del mundo: {seed} — "
                        "la misma serie de hechos, vista a través de la memoria imperfecta de la aldea)*"),
        "events": {
            "GIFT":        lambda a, b: f"{a} le dio pan a {b}",
            "REFUSAL":     lambda a, b: f"{a} echó a {b} con las manos vacías",
            "QUARREL":     lambda a, b: f"{a} y {b} se pelearon abiertamente",
            "INGRATITUDE": lambda a, b: f"{b} echó a {a} — aunque {a} le había llenado la cesta una vez",
            "RESENTMENT":  lambda a, b: f"{a} había llegado a resentirse de {b} por una deuda nunca devuelta",
            "REPAYMENT":   lambda a, b: f"{a} devolvió lo que le debía a {b}",
            "BOND":        lambda a, b: f"{a} y {b} se eligieron antes de que cambiara la estación",
            "OFFENSE":     lambda a, b: f"las palabras de {b} llegaron a oídos de {a}",
            "MEDIATION":   lambda a, b: f"{a} y {b} fueron traídos a hablar de nuevo",
            "WIDOWING":    lambda a, b: f"{a} sobrevivió a {b}",
        },
        "gap": {
            "same":   "ese mismo día",
            "few":    "unos días después",
            "some":   "algunos días más tarde",
            "weeks":  "unas semanas después",
            "season": "una estación después",
            "later":  "algún tiempo después",
        },
        "distortion": {
            "intact":        "La historia llegó intacta.",
            "slight":        "La historia cambió ligeramente al contarla.",
            "flip_to_bad":   "Lo que había sido una bondad llegó como un agravio. El significado se había invertido.",
            "flip_to_good":  "Lo que había sido un agravio llegó como una bondad. El significado se había invertido.",
            "grew_much":     "La historia había crecido considerablemente al contarla.",
            "grew":          "Se había añadido algo. La historia era más grande de lo que era cuando salió.",
            "shrank_much":   "La historia había menguado considerablemente al contarla.",
            "shrank":        "Se había perdido algo. La historia era más pequeña de lo que era cuando salió.",
        },
        "valence": {
            "very_good":  "algo notable",
            "good":       "algo bueno",
            "small_good": "una pequeña bondad",
            "neutral":    "algo sin importancia",
            "small_bad":  "una pequeña injusticia",
            "bad":        "algo malo",
            "very_bad":   "algo grave",
        },
        "and":     " y ",
        "year":    "año",
        "seasons": ("primavera", "verano", "otoño", "invierno"),
    },
    "fr": {
        "title":       "Ce que porte {village}",
        "intro":       ("*Un registre des mêmes événements, mais tels qu'ils ont voyagé.*  \n"
                        "*La chronique dit ce qui s'est passé. "
                        "Ceci dit ce dont le village se souvient — "
                        "ce qui n'est pas toujours la même chose.*"),
        "no_events":   ("*Les histoires de cette partie n'ont pas voyagé assez loin pour laisser "
                        "un registre de fragments. Essayez une partie plus longue ou avec plus de personnes.*"),
        "section_of":  "De {a} et {b}",
        "what_happened": "*{when}. Ce qui s'est passé : {desc}.*",
        "no_firsthand": "Personne qui était là n'a laissé de trace de souvenir.",
        "firsthand_one": "{name} était là. Il s'en souvenait comme de {valence}.",
        "firsthand_two_same": "{names} le portaient tous deux de première main et s'en souvenaient tous deux comme de {valence}.",
        "firsthand_two_diff": "{names} étaient tous deux là, et ils ne s'en souvenaient pas de la même façon : {remembered}.",
        "remembered_as": "{name} comme {valence}",
        "reached_1":   "Cela atteignit une autre personne.",
        "reached_n":   "Cela atteignit {n} autres personnes.",
        "heard_from":  "{gap}, {name} l'entendit de {teller}. {note}",
        "heard_unknown": ("{gap}, {name} en entendit parler — "
                          "de qui exactement n'est pas consigné. "
                          "Il s'en souvenait comme de {valence}."),
        "summary_held":    "*{mouths}, et l'histoire tint.*",
        "summary_flipped": ("*{mouths}, et l'histoire s'était retournée. "
                             "Ce qu'elle était : {was}. "
                             "Ce que la dernière oreille reçut : {became}.*"),
        "summary_grew":    ("*{mouths}, et l'histoire grandit. "
                             "Ce qu'elle était : {was}. "
                             "Ce que la dernière oreille reçut : {became}.*"),
        "summary_shrank":  ("*{mouths}, et l'histoire rapetissa. "
                             "Ce qu'elle était : {was}. "
                             "Ce que la dernière oreille reçut : {became}.*"),
        "one_telling": "Une transmission",
        "n_tellings":  "{n} transmissions",
        "colophon":    ("*(graine du monde : {seed} — "
                        "la même série d'événements, vue à travers la mémoire imparfaite du village)*"),
        "events": {
            "GIFT":        lambda a, b: f"{a} donna du pain à {b}",
            "REFUSAL":     lambda a, b: f"{a} renvoya {b} les mains vides",
            "QUARREL":     lambda a, b: f"{a} et {b} se querellèrent ouvertement",
            "INGRATITUDE": lambda a, b: f"{b} renvoya {a} — alors que {a} avait rempli son panier une fois",
            "RESENTMENT":  lambda a, b: f"{a} en était venu à en vouloir à {b} pour une dette jamais rendue",
            "REPAYMENT":   lambda a, b: f"{a} rendit ce qu'il devait à {b}",
            "BOND":        lambda a, b: f"{a} et {b} se choisirent avant que la saison ne tourne",
            "OFFENSE":     lambda a, b: f"les propos de {b} parvinrent aux oreilles de {a}",
            "MEDIATION":   lambda a, b: f"{a} et {b} furent amenés à se parler de nouveau",
            "WIDOWING":    lambda a, b: f"{a} survécut à {b}",
        },
        "gap": {
            "same":   "le jour même",
            "few":    "quelques jours plus tard",
            "some":   "quelques jours après",
            "weeks":  "quelques semaines plus tard",
            "season": "une saison plus tard",
            "later":  "quelque temps après",
        },
        "distortion": {
            "intact":        "L'histoire arriva intacte.",
            "slight":        "L'histoire changea légèrement dans la transmission.",
            "flip_to_bad":   "Ce qui avait été une gentillesse arriva comme un tort. Le sens s'était inversé.",
            "flip_to_good":  "Ce qui avait été un tort arriva comme une gentillesse. Le sens s'était inversé.",
            "grew_much":     "L'histoire avait considérablement grossi dans la transmission.",
            "grew":          "Quelque chose avait été ajouté. L'histoire était plus grande qu'à son départ.",
            "shrank_much":   "L'histoire avait considérablement rétréci dans la transmission.",
            "shrank":        "Quelque chose avait été perdu. L'histoire était plus petite qu'à son départ.",
        },
        "valence": {
            "very_good":  "quelque chose de remarquable",
            "good":       "quelque chose de bien",
            "small_good": "une petite gentillesse",
            "neutral":    "quelque chose d'anodin",
            "small_bad":  "un petit tort",
            "bad":        "quelque chose de mauvais",
            "very_bad":   "quelque chose de grave",
        },
        "and":     " et ",
        "year":    "an",
        "seasons": ("le printemps", "l'été", "l'automne", "l'hiver"),
    },
    "pt": {
        "title":       "O que {village} carrega",
        "intro":       ("*Um registo dos mesmos acontecimentos, mas tal como viajaram.*  \n"
                        "*A crónica diz o que aconteceu. "
                        "Isto diz o que a aldeia se lembra — "
                        "que nem sempre é a mesma coisa.*"),
        "no_events":   ("*As histórias desta partida não viajaram o suficiente para deixar "
                        "um registo de fragmentos. Experimenta uma partida mais longa ou com mais pessoas.*"),
        "section_of":  "De {a} e {b}",
        "what_happened": "*{when}. O que aconteceu: {desc}.*",
        "no_firsthand": "Ninguém que estivesse lá deixou rasto de o ter recordado.",
        "firsthand_one": "{name} estava lá. Recordava-o como {valence}.",
        "firsthand_two_same": "Tanto {names} o carregaram em primeira mão e ambos o recordavam como {valence}.",
        "firsthand_two_diff": "{names} estavam os dois lá, e não o recordavam da mesma forma: {remembered}.",
        "remembered_as": "{name} como {valence}",
        "reached_1":   "Chegou a mais uma pessoa.",
        "reached_n":   "Chegou a mais {n} pessoas.",
        "heard_from":  "{gap}, {name} ouviu-o de {teller}. {note}",
        "heard_unknown": ("{gap}, {name} soube disso — "
                          "de quem exatamente não está registado. "
                          "Recordava-o como {valence}."),
        "summary_held":    "*{mouths}, e a história manteve-se.*",
        "summary_flipped": ("*{mouths}, e a história tinha dado a volta. "
                             "O que era: {was}. "
                             "O que o último ouvido recebeu: {became}.*"),
        "summary_grew":    ("*{mouths}, e a história cresceu. "
                             "O que era: {was}. "
                             "O que o último ouvido recebeu: {became}.*"),
        "summary_shrank":  ("*{mouths}, e a história encolheu. "
                             "O que era: {was}. "
                             "O que o último ouvido recebeu: {became}.*"),
        "one_telling": "Uma transmissão",
        "n_tellings":  "{n} transmissões",
        "colophon":    ("*(semente do mundo: {seed} — "
                        "a mesma série de acontecimentos, vista pela memória imperfeita da aldeia)*"),
        "events": {
            "GIFT":        lambda a, b: f"{a} deu pão a {b}",
            "REFUSAL":     lambda a, b: f"{a} mandou {b} embora de mãos vazias",
            "QUARREL":     lambda a, b: f"{a} e {b} discutiram abertamente",
            "INGRATITUDE": lambda a, b: f"{b} mandou {a} embora — embora {a} lhe tivesse enchido o cesto uma vez",
            "RESENTMENT":  lambda a, b: f"{a} tinha chegado a guardar rancor de {b} por uma dívida nunca devolvida",
            "REPAYMENT":   lambda a, b: f"{a} devolveu o que devia a {b}",
            "BOND":        lambda a, b: f"{a} e {b} escolheram-se antes que a estação mudasse",
            "OFFENSE":     lambda a, b: f"as palavras de {b} chegaram aos ouvidos de {a}",
            "MEDIATION":   lambda a, b: f"{a} e {b} foram levados a falar de novo",
            "WIDOWING":    lambda a, b: f"{a} sobreviveu a {b}",
        },
        "gap": {
            "same":   "nesse mesmo dia",
            "few":    "alguns dias depois",
            "some":   "alguns dias mais tarde",
            "weeks":  "algumas semanas depois",
            "season": "uma estação depois",
            "later":  "algum tempo depois",
        },
        "distortion": {
            "intact":        "A história chegou intacta.",
            "slight":        "A história mudou ligeiramente na transmissão.",
            "flip_to_bad":   "O que tinha sido uma bondade chegou como uma injustiça. O significado tinha-se invertido.",
            "flip_to_good":  "O que tinha sido uma injustiça chegou como uma bondade. O significado tinha-se invertido.",
            "grew_much":     "A história tinha crescido consideravelmente na transmissão.",
            "grew":          "Tinha sido acrescentado algo. A história era maior do que quando saiu.",
            "shrank_much":   "A história tinha encolhido consideravelmente na transmissão.",
            "shrank":        "Tinha-se perdido algo. A história era menor do que quando saiu.",
        },
        "valence": {
            "very_good":  "algo notável",
            "good":       "algo bom",
            "small_good": "uma pequena bondade",
            "neutral":    "algo sem importância",
            "small_bad":  "uma pequena injustiça",
            "bad":        "algo mau",
            "very_bad":   "algo grave",
        },
        "and":     " e ",
        "year":    "ano",
        "seasons": ("a primavera", "o verão", "o outono", "o inverno"),
    },
    "it": {
        "title":       "Ciò che porta {village}",
        "intro":       ("*Un registro degli stessi eventi, ma come hanno viaggiato.*  \n"
                        "*La cronaca dice cosa è successo. "
                        "Questo dice cosa il villaggio ricorda — "
                        "che non è sempre la stessa cosa.*"),
        "no_events":   ("*Le storie di questa partita non hanno viaggiato abbastanza lontano per lasciare "
                        "un registro di frammenti. Prova una partita più lunga o con più persone.*"),
        "section_of":  "Di {a} e {b}",
        "what_happened": "*{when}. Cosa è successo: {desc}.*",
        "no_firsthand": "Nessuno che fosse lì ha lasciato traccia di ricordarlo.",
        "firsthand_one": "{name} era lì. Lo ricordava come {valence}.",
        "firsthand_two_same": "Sia {names} lo portavano di prima mano e lo ricordavano entrambi come {valence}.",
        "firsthand_two_diff": "{names} erano entrambi lì, e non lo ricordavano allo stesso modo: {remembered}.",
        "remembered_as": "{name} come {valence}",
        "reached_1":   "Raggiunse un'altra persona.",
        "reached_n":   "Raggiunse altre {n} persone.",
        "heard_from":  "{gap}, {name} lo sentì da {teller}. {note}",
        "heard_unknown": ("{gap}, {name} ne seppe — "
                          "da chi esattamente non è registrato. "
                          "Lo ricordava come {valence}."),
        "summary_held":    "*{mouths}, e la storia tenne.*",
        "summary_flipped": ("*{mouths}, e la storia si era ribaltata. "
                             "Com'era: {was}. "
                             "Cosa ricevette l'ultimo orecchio: {became}.*"),
        "summary_grew":    ("*{mouths}, e la storia crebbe. "
                             "Com'era: {was}. "
                             "Cosa ricevette l'ultimo orecchio: {became}.*"),
        "summary_shrank":  ("*{mouths}, e la storia si rimpicciolì. "
                             "Com'era: {was}. "
                             "Cosa ricevette l'ultimo orecchio: {became}.*"),
        "one_telling": "Una trasmissione",
        "n_tellings":  "{n} trasmissioni",
        "colophon":    ("*(seme del mondo: {seed} — "
                        "la stessa serie di eventi, vista attraverso la memoria imperfetta del villaggio)*"),
        "events": {
            "GIFT":        lambda a, b: f"{a} diede del pane a {b}",
            "REFUSAL":     lambda a, b: f"{a} mandò via {b} a mani vuote",
            "QUARREL":     lambda a, b: f"{a} e {b} litigarono apertamente",
            "INGRATITUDE": lambda a, b: f"{b} mandò via {a} — benché {a} gli avesse riempito il cesto una volta",
            "RESENTMENT":  lambda a, b: f"{a} era arrivato a risentirsi di {b} per un debito mai restituito",
            "REPAYMENT":   lambda a, b: f"{a} restituì ciò che doveva a {b}",
            "BOND":        lambda a, b: f"{a} e {b} si scelsero prima che la stagione voltasse",
            "OFFENSE":     lambda a, b: f"le parole di {b} giunsero alle orecchie di {a}",
            "MEDIATION":   lambda a, b: f"{a} e {b} furono portati a parlare di nuovo",
            "WIDOWING":    lambda a, b: f"{a} sopravvisse a {b}",
        },
        "gap": {
            "same":   "lo stesso giorno",
            "few":    "qualche giorno dopo",
            "some":   "alcuni giorni più tardi",
            "weeks":  "qualche settimana dopo",
            "season": "una stagione dopo",
            "later":  "qualche tempo dopo",
        },
        "distortion": {
            "intact":        "La storia arrivò intatta.",
            "slight":        "La storia cambiò leggermente nella trasmissione.",
            "flip_to_bad":   "Quello che era stato un gesto gentile arrivò come un torto. Il significato si era invertito.",
            "flip_to_good":  "Quello che era stato un torto arrivò come un gesto gentile. Il significato si era invertito.",
            "grew_much":     "La storia era cresciuta considerevolmente nella trasmissione.",
            "grew":          "Era stato aggiunto qualcosa. La storia era più grande di quando era partita.",
            "shrank_much":   "La storia si era rimpicciolita considerevolmente nella trasmissione.",
            "shrank":        "Era andato perso qualcosa. La storia era più piccola di quando era partita.",
        },
        "valence": {
            "very_good":  "qualcosa di notevole",
            "good":       "qualcosa di buono",
            "small_good": "una piccola gentilezza",
            "neutral":    "qualcosa di insignificante",
            "small_bad":  "un piccolo torto",
            "bad":        "qualcosa di brutto",
            "very_bad":   "qualcosa di grave",
        },
        "and":     " e ",
        "year":    "anno",
        "seasons": ("la primavera", "l'estate", "l'autunno", "l'inverno"),
    },
}


def _valence_word(t: dict, v: float) -> str:
    vt = t["valence"]
    if v > 0.65:  return vt["very_good"]
    if v > 0.35:  return vt["good"]
    if v > 0.05:  return vt["small_good"]
    if v > -0.05: return vt["neutral"]
    if v > -0.35: return vt["small_bad"]
    if v > -0.65: return vt["bad"]
    return vt["very_bad"]


def _time_gap(t: dict, delta: int) -> str:
    gt = t["gap"]
    if delta <= 2:               return gt["same"]
    if delta <= 8:               return gt["few"]
    if delta <= 20:              return gt["some"]
    if delta < TICKS_PER_SEASON: return gt["weeks"]
    if delta < TICKS_PER_SEASON * 2: return gt["season"]
    return gt["later"]


def _distortion_note(t: dict, prev_val: float, curr_val: float) -> str:
    dt = t["distortion"]
    delta = curr_val - prev_val
    if abs(delta) < 0.05:
        return dt["intact"]
    if abs(delta) < 0.18:
        return dt["slight"]
    if prev_val * curr_val < 0:
        return dt["flip_to_bad"] if curr_val < 0 else dt["flip_to_good"]
    if delta > 0.35:  return dt["grew_much"]
    if delta > 0:     return dt["grew"]
    if delta < -0.35: return dt["shrank_much"]
    return dt["shrank"]


def _season_year(t: dict, tick: int) -> str:
    seasons = t["seasons"]
    return f"{seasons[season_index(tick)]}, {t['year']} {year_of(tick)}"


def _chain_for(world, event_id: int) -> list:
    found = []
    for char in world.chars:
        for m in char.memories:
            if m.event_id == event_id:
                found.append((char, m))
                break
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
    lang = getattr(narrator, "lang", "en")
    t = _T.get(lang, _T["en"])
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
            f"# {t['title'].format(village=village)}\n\n"
            f"{t['no_events']}\n"
        )

    parts = [
        f"# {t['title'].format(village=village)}",
        "",
        t["intro"],
        "",
        "---",
        "",
    ]

    for ev in chosen:
        eid = ev.data.get("id", -1)
        a_name = narrator.name(ev.actors[0])
        b_name = narrator.name(ev.actors[1])

        event_fn = t["events"].get(ev.kind, lambda a, b: f"{a} — {b}")
        desc = event_fn(a_name, b_name)
        when = _season_year(t, ev.tick).capitalize()

        parts.append(f"## {t['section_of'].format(a=a_name, b=b_name)}")
        parts.append("")
        parts.append(t["what_happened"].format(when=when, desc=desc))
        parts.append("")

        chain = _chain_for(world, eid)
        char_mem = {c.id: m for c, m in chain}
        firsthand = [(c, m) for c, m in chain if m.firsthand]
        secondhand = [(c, m) for c, m in chain if not m.firsthand]

        if not firsthand:
            parts.append(t["no_firsthand"])
        elif len(firsthand) == 1:
            c, m = firsthand[0]
            parts.append(t["firsthand_one"].format(
                name=c.name, valence=_valence_word(t, m.valence)))
        else:
            names_str = t["and"].join(c.name for c, _ in firsthand)
            val_words = [_valence_word(t, m.valence) for _, m in firsthand]
            if len(set(val_words)) == 1:
                parts.append(t["firsthand_two_same"].format(
                    names=names_str, valence=val_words[0]))
            else:
                remembered = "; ".join(
                    t["remembered_as"].format(name=c.name, valence=_valence_word(t, m.valence))
                    for c, m in firsthand
                )
                parts.append(t["firsthand_two_diff"].format(
                    names=names_str, remembered=remembered))

        if secondhand:
            parts.append("")
            if len(secondhand) == 1:
                parts.append(t["reached_1"])
            else:
                parts.append(t["reached_n"].format(n=len(secondhand)))
            parts.append("")

            for c, m in secondhand:
                gap = _time_gap(t, m.tick - ev.tick)
                teller_name = (narrator.name(m.heard_from)
                               if m.heard_from is not None else "—")
                if m.heard_from is not None and m.heard_from in char_mem:
                    note = _distortion_note(t, char_mem[m.heard_from].valence, m.valence)
                    parts.append(t["heard_from"].format(
                        gap=gap.capitalize(), name=c.name,
                        teller=teller_name, note=note))
                else:
                    parts.append(t["heard_unknown"].format(
                        gap=gap.capitalize(), name=c.name,
                        valence=_valence_word(t, m.valence)))

        if secondhand and firsthand:
            first_val = firsthand[0][1].valence
            last_val = secondhand[-1][1].valence
            n = len(secondhand)
            mouths = (t["one_telling"] if n == 1
                      else t["n_tellings"].format(n=n))
            drift = abs(last_val - first_val)

            if drift < 0.05:
                summary = t["summary_held"].format(mouths=mouths)
            elif first_val * last_val < 0:
                summary = t["summary_flipped"].format(
                    mouths=mouths,
                    was=_valence_word(t, first_val),
                    became=_valence_word(t, last_val))
            elif last_val > first_val:
                summary = t["summary_grew"].format(
                    mouths=mouths,
                    was=_valence_word(t, first_val),
                    became=_valence_word(t, last_val))
            else:
                summary = t["summary_shrank"].format(
                    mouths=mouths,
                    was=_valence_word(t, first_val),
                    became=_valence_word(t, last_val))
            parts.append("")
            parts.append(summary)

        parts += ["", "---", ""]

    parts.append(t["colophon"].format(seed=world.seed))
    parts.append("")
    return "\n".join(parts)
