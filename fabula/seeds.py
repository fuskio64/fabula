"""Story seeds — writing prompts derived from the actual events of a village run.

`story_seeds(world, narrator)` returns a Markdown document with 3-7 story seeds.
Each seed names specific characters and events. They are not invented — every seed
traces back to something the record contains.
"""

from .model import TICKS_PER_SEASON, year_of


_SS = {
    "en": {
        "title":    "# Story Seeds — {village}",
        "subtitle": "*Seed {seed} · {days} days · drawn from the record*",
        "preamble": "These are not inventions. Each one traces back to something that happened in this village.",
        "seed_label": "**Story {n}.**",
        "no_seeds":  "No strong story patterns found in this short run. Try a longer simulation.",
        "patterns": {
            "ingratitude": "A story about the day {b} turned {a} away empty-handed — when {a} had once filled {b}'s basket in a lean stretch. What do you do with a debt that was never answered?",
            "long_debt":   "A story about the debt {a} carried toward {b} for {n} seasons — what it felt like to owe someone that long, and what finally happened when it was settled.",
            "feud":        "A story about the feud between {a} and {b}. Not the beginning of it, but the middle — when everyone in {village} already knew which side they were on.",
            "estrangement":"A story about {a} and {b}, who stopped speaking. Not the argument — that is already gone. The silence after, which lasted.",
            "reconciliation": "A story about {a} and {b}, who had been estranged for years and then made peace. What changes in a village when two people who were at war choose to stop?",
            "adoption":    "A story about {child} — the child who lost both parents and was taken in by {pa} and {pb}. What does it mean to start over inside a family that is not quite yours?",
            "teaching":    "A story about {elder} and {young}, and what passed between them when {young} came of age. The kind of thing that cannot be taught directly. Only witnessed.",
            "mass_death":  "A story about {season} of year {year}, when {n} people died inside the same weeks. What remained. Who remained. What the village was after.",
            "memorial":    "A story about the day {name} died, and the gathering that followed. Not a ceremony — just the people who had cared for the same person finding themselves in the same place.",
            "long_grief":  "A story about {name}, who outlived their partner and kept moving. The village gave what warmth it could. Some things cannot be given back.",
            "widowing_bond": "A story about {a}, who lost {b} and, after a time, chose {c}. What it costs to let someone in again after that kind of loss.",
            "illness":     "A story about the time {name} fell ill. Not whether they lived or died — that is in the record. What people did in the meantime. Who came. Who did not.",
            "jealousy":    "A story about {name}, who had carried something for {loved_one} for as long as it lasted — and what happened inside them when {loved_one} and {rival} chose each other.",
            "legacy":      "A story about {student} in the seasons after {teacher} died — the ways {teacher}'s work kept showing up in what {student} did, without either of them knowing it would go that way.",
            "feud_end":    "A story about the feud between {a} and {b}, and how it ended — at {name}'s graveside, of all places. They had both loved the same person. Grief did what years of argument could not.",
            "pact":        "A story about {a} and {b} — the friendship that {village} did not have a name for. What they made of it. What it cost them. Whether it held.",
            "drought":     "A story about the year the harvest failed in {village}. Not about what was lost — the record has that. About what {village} discovered in the two thin seasons. What people became. What they kept afterward that they hadn't had before.",
            "mediator":    "A story about {name}, who stood between people in {village} when they could no longer reach each other. Not the mediations that worked, or the ones that didn't — the fact of a person who kept doing it. What the village made of that. What they asked nothing in return.",
            "departure":   "A story about {name}, who left {village}. Not about what drove them out — that is in the record. What the village was afterward, missing a person it may not have been kind to.",
            "offense":     "A story about the day the wrong story reached {name} in {village} — about {source}, or something that had happened between them. Not the original event. The travel of it. Whether what arrived was still recognizable as the truth. Whether it mattered.",
        },
    },
    "es": {
        "title":    "# Semillas de historia — {village}",
        "subtitle": "*Semilla {seed} · {days} días · extraídas del registro*",
        "preamble": "No son invenciones. Cada una remite a algo que sucedió en esta aldea.",
        "seed_label": "**Historia {n}.**",
        "no_seeds":  "No se encontraron patrones narrativos fuertes en esta simulación corta. Prueba con una más larga.",
        "patterns": {
            "ingratitude": "Una historia sobre el día en que {b} rechazó a {a} con las manos vacías — cuando {a} le había llenado la cesta en un momento de escasez. ¿Qué haces con una deuda que nunca fue respondida?",
            "long_debt":   "Una historia sobre la deuda que {a} cargó hacia {b} durante {n} estaciones — lo que se siente deber a alguien tanto tiempo, y lo que pasó cuando finalmente se saldó.",
            "feud":        "Una historia sobre la enemistad entre {a} y {b}. No el comienzo, sino el medio — cuando todo el mundo en {village} ya sabía de qué lado estaba.",
            "estrangement":"Una historia sobre {a} y {b}, que dejaron de hablarse. No la discusión — esa ya se fue. El silencio después, que duró.",
            "reconciliation": "Una historia sobre {a} y {b}, que estuvieron distanciados durante años y luego hicieron las paces. ¿Qué cambia en una aldea cuando dos personas en guerra deciden parar?",
            "adoption":    "Una historia sobre {child} — el niño que perdió a ambos padres y fue acogido por {pa} y {pb}. ¿Qué significa empezar de nuevo en una familia que no es del todo la tuya?",
            "teaching":    "Una historia sobre {elder} y {young}, y lo que pasó entre ellos cuando {young} llegó a la edad adulta. El tipo de cosa que no se puede enseñar directamente. Solo presenciar.",
            "mass_death":  "Una historia sobre el {season} del año {year}, cuando {n} personas murieron en las mismas semanas. Lo que quedó. Quién quedó. Lo que era la aldea después.",
            "memorial":    "Una historia sobre el día en que {name} murió, y la reunión que siguió. No una ceremonia — solo la gente que había querido a la misma persona encontrándose en el mismo lugar.",
            "long_grief":  "Una historia sobre {name}, que sobrevivió a su compañero y siguió adelante. La aldea dio lo que pudo. Hay cosas que no se pueden devolver.",
            "widowing_bond": "Una historia sobre {a}, que perdió a {b} y, después de un tiempo, eligió a {c}. Lo que cuesta dejar entrar a alguien de nuevo después de una pérdida así.",
            "illness":     "Una historia sobre la vez en que {name} cayó enfermo. No si vivió o murió — eso está en el registro. Lo que la gente hizo mientras tanto. Quién vino. Quién no.",
            "jealousy":    "Una historia sobre {name}, que había llevado algo por {loved_one} mientras duró — y lo que pasó por dentro cuando {loved_one} y {rival} se eligieron.",
            "legacy":      "Una historia sobre {student} en las estaciones después de que {teacher} murió — las maneras en que el trabajo de {teacher} seguía apareciendo en lo que {student} hacía, sin que ninguno supiera que iría así.",
            "feud_end":    "Una historia sobre la enemistad entre {a} y {b}, y cómo terminó — junto a la tumba de {name}, de todos los lugares. Ambos habían querido a la misma persona. El duelo hizo lo que años de disputas no habían podido.",
            "pact":        "Una historia sobre {a} y {b} — la amistad para la que {village} no tenía nombre. Lo que hicieron con ella. Lo que les costó. Si aguantó.",
            "drought":     "Una historia sobre el año en que la cosecha falló en {village}. No sobre lo que se perdió — el registro ya lo tiene. Sobre lo que {village} descubrió en las dos estaciones escasas. En qué se convirtió la gente. Lo que guardaron después que antes no tenían.",
            "mediator":    "Una historia sobre {name}, que se puso entre personas en {village} cuando ya no podían alcanzarse mutuamente. No las mediaciones que funcionaron, ni las que no — el hecho de una persona que seguía haciéndolo. Lo que la aldea pensó de eso. Lo que no pidió nada a cambio.",
            "departure":   "Una historia sobre {name}, que dejó {village}. No sobre lo que los expulsó — eso está en el registro. Lo que era la aldea después, faltando una persona con la que quizás no había sido amable.",
            "offense":     "Una historia sobre el día en que la historia equivocada llegó a {name} en {village} — sobre {source}, o algo que había pasado entre ellos. No el evento original. El viaje de él. Si lo que llegó seguía siendo reconocible como verdad. Si importaba.",
        },
    },
    "fr": {
        "title":    "# Germes d'histoires — {village}",
        "subtitle": "*Graine {seed} · {days} jours · tires du registre*",
        "preamble": "Ce ne sont pas des inventions. Chacun renvoie a quelque chose qui s'est passe dans ce village.",
        "seed_label": "**Histoire {n}.**",
        "no_seeds":  "Aucun motif narratif fort trouve dans cette courte simulation. Essayez plus longtemps.",
        "patterns": {
            "ingratitude": "Une histoire sur le jour ou {b} a renvoye {a} les mains vides — alors que {a} avait rempli le panier de {b} en periode de disette. Que faire d'une dette qui n'a jamais ete honoree ?",
            "long_debt":   "Une histoire sur la dette que {a} a portee envers {b} pendant {n} saisons — ce que ca fait de devoir a quelqu'un aussi longtemps, et ce qui s'est passe quand elle a finalement ete acquittee.",
            "feud":        "Une histoire sur la querelle entre {a} et {b}. Pas le debut — le milieu, quand tout le monde a {village} savait deja de quel cote il etait.",
            "estrangement":"Une histoire sur {a} et {b}, qui ont cesse de se parler. Pas la dispute — elle est deja partie. Le silence apres, qui a dure.",
            "reconciliation": "Une histoire sur {a} et {b}, qui avaient ete brouilles pendant des annees et ont ensuite fait la paix. Qu'est-ce qui change dans un village quand deux personnes en guerre choisissent d'arreter ?",
            "adoption":    "Une histoire sur {child} — l'enfant qui a perdu ses deux parents et a ete recueilli par {pa} et {pb}. Que signifie recommencer dans une famille qui n'est pas tout a fait la sienne ?",
            "teaching":    "Une histoire sur {elder} et {young}, et ce qui s'est passe entre eux quand {young} est devenu adulte. Le genre de chose qu'on ne peut pas enseigner directement. Seulement temoigner.",
            "mass_death":  "Une histoire sur le {season} de l'an {year}, quand {n} personnes sont mortes dans les memes semaines. Ce qui est reste. Qui est reste. Ce qu'etait le village apres.",
            "memorial":    "Une histoire sur le jour ou {name} est mort, et le rassemblement qui a suivi. Pas une ceremonie — juste des gens qui avaient aime la meme personne se retrouvant au meme endroit.",
            "long_grief":  "Une histoire sur {name}, qui a survecu a son partenaire et a continue d'avancer. Le village a donne ce qu'il pouvait. Certaines choses ne peuvent pas etre rendues.",
            "widowing_bond": "Une histoire sur {a}, qui a perdu {b} et, apres un temps, a choisi {c}. Ce que ca coute de laisser entrer quelqu'un a nouveau apres une telle perte.",
            "illness":     "Une histoire sur le moment ou {name} tomba malade. Pas si il vecut ou mourut — c'est dans le registre. Ce que les gens firent entre-temps. Qui vint. Qui ne vint pas.",
            "jealousy":    "Une histoire sur {name}, qui avait porte quelque chose pour {loved_one} aussi longtemps que ca avait dure — et ce qui se passa en lui quand {loved_one} et {rival} se choisirent.",
            "legacy":      "Une histoire sur {student} dans les saisons apres la mort de {teacher} — les façons dont le travail de {teacher} continuait d'apparaitre dans ce que faisait {student}, sans qu'aucun des deux sache que ca se passerait ainsi.",
            "feud_end":    "Une histoire sur la querelle entre {a} et {b}, et comment elle prit fin — au bord de la tombe de {name}, de tous les endroits. Tous deux avaient aime la meme personne. Le deuil fit ce que des annees de dispute n'avaient pas pu.",
            "pact":        "Une histoire sur {a} et {b} — l'amitie pour laquelle {village} n'avait pas de mot. Ce qu'ils en firent. Ce que ca leur couta. Si ca tint.",
            "drought":     "Une histoire sur l'annee ou la recolte echoua a {village}. Pas sur ce qui fut perdu — le registre a ca. Sur ce que {village} decouvrit dans les deux saisons maigres. Ce que les gens devinrent. Ce qu'ils garderent apres qui n'etait pas la avant.",
            "mediator":    "Une histoire sur {name}, qui se placa entre des gens a {village} quand ils ne pouvaient plus se rejoindre. Pas les mediations qui marcherent, ni celles qui ne marcherent pas — le fait d'une personne qui continuait a le faire. Ce que le village en pensa. Ce qu'elle ne demanda pas en retour.",
            "departure":   "Une histoire sur {name}, qui quitta {village}. Pas sur ce qui le chassa — c'est dans le registre. Ce qu'etait le village apres, manquant d'une personne envers laquelle il n'avait peut-etre pas ete aimable.",
            "offense":     "Une histoire sur le jour ou la mauvaise histoire parvint a {name} a {village} — sur {source}, ou sur quelque chose qui s'etait passe entre eux. Pas l'evenement original. Son trajet. Si ce qui arriva ressemblait encore a la verite. Si cela importait.",
        },
    },
    "pt": {
        "title":    "# Sementes de história — {village}",
        "subtitle": "*Semente {seed} · {days} dias · tiradas do registo*",
        "preamble": "Não são invenções. Cada uma remete para algo que aconteceu nesta aldeia.",
        "seed_label": "**História {n}.**",
        "no_seeds":  "Nenhum padrão narrativo forte encontrado nesta simulação curta. Tente com uma mais longa.",
        "patterns": {
            "ingratitude": "Uma história sobre o dia em que {b} rejeitou {a} de mãos vazias — quando {a} lhe tinha enchido o cesto numa época de escassez. O que se faz com uma dívida que nunca foi respondida?",
            "long_debt":   "Uma história sobre a dívida que {a} carregou para com {b} durante {n} estações — o que se sente dever a alguém tanto tempo, e o que aconteceu quando finalmente foi saldada.",
            "feud":        "Uma história sobre a inimizade entre {a} e {b}. Não o início — o meio, quando toda a gente em {village} já sabia de que lado estava.",
            "estrangement":"Uma história sobre {a} e {b}, que deixaram de se falar. Não a discussão — essa já foi. O silêncio depois, que durou.",
            "reconciliation": "Uma história sobre {a} e {b}, que estiveram afastados durante anos e depois fizeram as pazes. O que muda numa aldeia quando duas pessoas em guerra decidem parar?",
            "adoption":    "Uma história sobre {child} — a criança que perdeu ambos os pais e foi acolhida por {pa} e {pb}. O que significa recomeçar dentro de uma família que não é bem a sua?",
            "teaching":    "Uma história sobre {elder} e {young}, e o que passou entre eles quando {young} chegou à maioridade. O tipo de coisa que não pode ser ensinada diretamente. Apenas testemunhada.",
            "mass_death":  "Uma história sobre o {season} do ano {year}, quando {n} pessoas morreram nas mesmas semanas. O que ficou. Quem ficou. O que era a aldeia depois.",
            "memorial":    "Uma história sobre o dia em que {name} morreu, e a reunião que se seguiu. Não uma cerimónia — apenas pessoas que tinham amado a mesma pessoa encontrando-se no mesmo lugar.",
            "long_grief":  "Uma história sobre {name}, que sobreviveu ao seu companheiro e continuou. A aldeia deu o que pôde. Há coisas que não podem ser devolvidas.",
            "widowing_bond": "Uma história sobre {a}, que perdeu {b} e, depois de um tempo, escolheu {c}. O que custa deixar alguém entrar de novo depois de uma perda assim.",
            "illness":     "Uma história sobre a vez em que {name} adoeceu. Não se viveu ou morreu — isso está no registo. O que as pessoas fizeram entretanto. Quem veio. Quem não veio.",
            "jealousy":    "Uma história sobre {name}, que tinha carregado algo por {loved_one} enquanto durou — e o que aconteceu por dentro quando {loved_one} e {rival} se escolheram.",
            "legacy":      "Uma história sobre {student} nas estações após a morte de {teacher} — as formas como o trabalho de {teacher} continuava a aparecer no que {student} fazia, sem que nenhum dos dois soubesse que seria assim.",
            "feud_end":    "Uma história sobre a inimizade entre {a} e {b}, e como terminou — junto à sepultura de {name}, de todos os lugares. Ambos tinham amado a mesma pessoa. O luto fez o que anos de disputa não tinham conseguido.",
            "pact":        "Uma história sobre {a} e {b} — a amizade para a qual {village} não tinha nome. O que fizeram com ela. O que lhes custou. Se aguentou.",
            "drought":     "Uma história sobre o ano em que a colheita falhou em {village}. Não sobre o que se perdeu — o registo tem isso. Sobre o que {village} descobriu nas duas estações magras. O que as pessoas se tornaram. O que guardaram depois que antes não tinham.",
            "mediator":    "Uma história sobre {name}, que se pôs entre pessoas em {village} quando já não conseguiam alcançar-se. Não as mediações que funcionaram, nem as que não — o facto de uma pessoa que continuava a fazê-lo. O que a aldeia pensou disso. O que não pediu nada em troca.",
            "departure":   "Uma história sobre {name}, que deixou {village}. Não sobre o que os expulsou — isso está no registo. O que era a aldeia depois, com falta de uma pessoa com quem talvez não tinha sido gentil.",
            "offense":     "Uma história sobre o dia em que a história errada chegou a {name} em {village} — sobre {source}, ou algo que tinha acontecido entre eles. Não o evento original. A sua viagem. Se o que chegou ainda era reconhecível como verdade. Se importava.",
        },
    },
    "it": {
        "title":    "# Semi di storia — {village}",
        "subtitle": "*Seme {seed} · {days} giorni · tratti dal registro*",
        "preamble": "Non sono invenzioni. Ognuno rimanda a qualcosa che e successo in questo villaggio.",
        "seed_label": "**Storia {n}.**",
        "no_seeds":  "Nessun pattern narrativo forte trovato in questa breve simulazione. Prova con una piu lunga.",
        "patterns": {
            "ingratitude": "Una storia sul giorno in cui {b} ha mandato via {a} a mani vuote — quando {a} aveva riempito il cesto di {b} in un periodo di magra. Cosa si fa con un debito che non e mai stato onorato?",
            "long_debt":   "Una storia sul debito che {a} ha portato verso {b} per {n} stagioni — cosa si prova a dovere a qualcuno cosi a lungo, e cosa e successo quando e stato finalmente saldato.",
            "feud":        "Una storia sulla faida tra {a} e {b}. Non l'inizio — il mezzo, quando tutti a {village} sapevano gia da che parte stare.",
            "estrangement":"Una storia su {a} e {b}, che hanno smesso di parlarsi. Non la lite — quella e gia andata. Il silenzio dopo, che e durato.",
            "reconciliation": "Una storia su {a} e {b}, che erano stati in rotta per anni e poi hanno fatto pace. Cosa cambia in un villaggio quando due persone in guerra scelgono di smettere?",
            "adoption":    "Una storia su {child} — il bambino che ha perso entrambi i genitori ed e stato accolto da {pa} e {pb}. Cosa significa ricominciare dentro una famiglia che non e del tutto la propria?",
            "teaching":    "Una storia su {elder} e {young}, e quello che e passato tra loro quando {young} e diventato adulto. Il tipo di cosa che non puo essere insegnata direttamente. Solo testimoniata.",
            "mass_death":  "Una storia sul {season} dell'anno {year}, quando {n} persone sono morte nelle stesse settimane. Cosa e rimasto. Chi e rimasto. Com'era il villaggio dopo.",
            "memorial":    "Una storia sul giorno in cui {name} e morto, e il raduno che e seguito. Non una cerimonia — solo persone che avevano amato la stessa persona ritrovandosi nello stesso posto.",
            "long_grief":  "Una storia su {name}, che ha sopravvissuto al proprio compagno e ha continuato ad andare avanti. Il villaggio ha dato quel che poteva. Certe cose non si possono restituire.",
            "widowing_bond": "Una storia su {a}, che ha perso {b} e, dopo un po', ha scelto {c}. Cosa costa lasciar entrare qualcuno di nuovo dopo una perdita simile.",
            "illness":     "Una storia sulla volta in cui {name} si ammalò. Non se visse o morì — questo è nel registro. Cosa fecero le persone nel frattempo. Chi venne. Chi no.",
            "jealousy":    "Una storia su {name}, che aveva portato qualcosa per {loved_one} finché durò — e cosa successe dentro di loro quando {loved_one} e {rival} si scelsero.",
            "legacy":      "Una storia su {student} nelle stagioni dopo la morte di {teacher} — i modi in cui il lavoro di {teacher} continuava ad apparire in ciò che faceva {student}, senza che nessuno dei due sapesse che sarebbe andata così.",
            "feud_end":    "Una storia sulla faida tra {a} e {b}, e come si concluse — sulla tomba di {name}, di tutti i posti. Entrambi avevano amato la stessa persona. Il dolore fece quello che anni di litigio non avevano potuto.",
            "pact":        "Una storia su {a} e {b} — l'amicizia per la quale {village} non aveva un nome. Cosa ne fecero. Cosa gli costò. Se resse.",
            "drought":     "Una storia sull'anno in cui il raccolto fallì a {village}. Non su quello che fu perso — il registro ha quello. Su quello che {village} scoprì nelle due stagioni magre. Cosa divennero le persone. Cosa tennero dopo che prima non avevano.",
            "mediator":    "Una storia su {name}, che si mise tra le persone a {village} quando non riuscivano più a raggiungersi. Non le mediazioni che funzionarono, né quelle che non funzionarono — il fatto di una persona che continuava a farlo. Quello che il villaggio ne pensò. Quello che non chiese nulla in cambio.",
            "departure":   "Una storia su {name}, che lasciò {village}. Non su quello che lo spinse fuori — quello è nel registro. Com'era il villaggio dopo, senza una persona con cui forse non era stato gentile.",
            "offense":     "Una storia sul giorno in cui la storia sbagliata raggiunse {name} a {village} — su {source}, o qualcosa che era successo tra loro. Non l'evento originale. Il suo viaggio. Se quello che arrivò era ancora riconoscibile come verità. Se importava.",
        },
    },
}


def _collect_seeds(world, narrator, t: dict) -> list[str]:
    w = world
    name = lambda cid: w.chars[cid].name if cid < len(w.chars) else "?"
    pats = t["patterns"]
    seeds: list[str] = []
    used_pairs: set = set()

    # --- ingratitude: GIFT followed later by INGRATITUDE for same pair ---
    gift_pairs = {frozenset(ev.actors[:2]): ev for ev in w.events if ev.kind == "GIFT"}
    for ev in w.events:
        if ev.kind == "INGRATITUDE" and len(ev.actors) >= 2:
            pair = frozenset(ev.actors[:2])
            if pair in gift_pairs and pair not in used_pairs:
                used_pairs.add(pair)
                a = name(ev.actors[1])  # actor[1] = the original giver who was turned away
                b = name(ev.actors[0])  # actor[0] = the one who was ungrateful (b turned a away)
                seeds.append(pats["ingratitude"].format(a=a, b=b, village=narrator.village))
                if len(seeds) >= 7:
                    return seeds
                break

    # --- long debt: REPAYMENT where carried > 3 seasons ---
    for ev in w.events:
        if ev.kind == "REPAYMENT" and ev.data.get("carried", 0) > TICKS_PER_SEASON * 3:
            if len(ev.actors) >= 2:
                pair = frozenset(ev.actors[:2])
                if pair not in used_pairs:
                    used_pairs.add(pair)
                    a = name(ev.actors[0])
                    b = name(ev.actors[1])
                    n_seasons = ev.data["carried"] // TICKS_PER_SEASON
                    seeds.append(pats["long_debt"].format(a=a, b=b, n=n_seasons, village=narrator.village))
                    if len(seeds) >= 7:
                        return seeds
                    break

    # --- feud that ended through shared grief ---
    if "feud_end" in pats:
        feud_pairs = {frozenset(ev.actors[:2]) for ev in w.events if ev.kind == "FEUD"}
        for recon_ev in w.events:
            if (recon_ev.kind == "RECONCILIATION"
                    and recon_ev.data.get("reason") == "shared_grief"
                    and len(recon_ev.actors) >= 2):
                pair = frozenset(recon_ev.actors[:2])
                if pair in feud_pairs and pair not in used_pairs:
                    used_pairs.add(pair)
                    a, b = name(recon_ev.actors[0]), name(recon_ev.actors[1])
                    deceased_id = recon_ev.data.get("deceased")
                    deceased_name = name(deceased_id) if deceased_id is not None else "?"
                    seeds.append(pats["feud_end"].format(
                        a=a, b=b, name=deceased_name, village=narrator.village))
                    if len(seeds) >= 7:
                        return seeds
                    break

    # --- mediator (the person who kept standing between others) ---
    if "mediator" in pats:
        from collections import Counter as _Counter
        med_counts: _Counter = _Counter(
            ev.data.get("mediator") for ev in w.events
            if ev.kind == "MEDIATION" and ev.data.get("mediator") is not None
        )
        if med_counts:
            top_mediator_id = med_counts.most_common(1)[0][0]
            if top_mediator_id < len(w.chars):
                seeds.append(pats["mediator"].format(
                    name=w.chars[top_mediator_id].name, village=narrator.village))
                if len(seeds) >= 7:
                    return seeds

    # --- drought (village-wide hardship arc) ---
    if "drought" in pats:
        for ev in w.events:
            if ev.kind == "DROUGHT":
                seeds.append(pats["drought"].format(village=narrator.village))
                if len(seeds) >= 7:
                    return seeds
                break

    # --- feud ---
    for ev in w.events:
        if ev.kind == "FEUD" and len(ev.actors) >= 2:
            pair = frozenset(ev.actors[:2])
            if pair not in used_pairs:
                used_pairs.add(pair)
                a, b = name(ev.actors[0]), name(ev.actors[1])
                seeds.append(pats["feud"].format(a=a, b=b, village=narrator.village))
                if len(seeds) >= 7:
                    return seeds
                break

    # --- reconciliation ---
    for ev in w.events:
        if ev.kind == "RECONCILIATION" and len(ev.actors) >= 2:
            pair = frozenset(ev.actors[:2])
            if pair not in used_pairs:
                used_pairs.add(pair)
                a, b = name(ev.actors[0]), name(ev.actors[1])
                seeds.append(pats["reconciliation"].format(a=a, b=b, village=narrator.village))
                if len(seeds) >= 7:
                    return seeds
                break

    # --- estrangement (unresolved) ---
    reconciled = {frozenset(ev.actors[:2]) for ev in w.events if ev.kind == "RECONCILIATION"}
    for ev in w.events:
        if ev.kind == "ESTRANGEMENT" and len(ev.actors) >= 2:
            pair = frozenset(ev.actors[:2])
            if pair not in reconciled and pair not in used_pairs:
                a_id, b_id = ev.actors[0], ev.actors[1]
                if a_id < len(w.chars) and b_id < len(w.chars):
                    if w.chars[a_id].alive and w.chars[b_id].alive:
                        used_pairs.add(pair)
                        a, b = name(a_id), name(b_id)
                        seeds.append(pats["estrangement"].format(a=a, b=b, village=narrator.village))
                        if len(seeds) >= 7:
                            return seeds
                        break

    # --- offense (gossip that reached the wrong ears) ---
    if "offense" in pats:
        for ev in w.events:
            if ev.kind == "OFFENSE" and len(ev.actors) >= 2:
                listener_id, source_id = ev.actors[0], ev.actors[1]
                if listener_id < len(w.chars) and source_id < len(w.chars):
                    seeds.append(pats["offense"].format(
                        name=w.chars[listener_id].name,
                        source=w.chars[source_id].name,
                        village=narrator.village))
                    if len(seeds) >= 7:
                        return seeds
                    break

    # --- adoption ---
    for ev in w.events:
        if ev.kind == "ADOPTION" and len(ev.actors) >= 3:
            child = name(ev.actors[0])
            pa, pb = name(ev.actors[1]), name(ev.actors[2])
            seeds.append(pats["adoption"].format(child=child, pa=pa, pb=pb, village=narrator.village))
            if len(seeds) >= 7:
                return seeds
            break

    # --- teaching ---
    for ev in w.events:
        if ev.kind == "TEACHING" and len(ev.actors) >= 2:
            elder = name(ev.actors[0])
            young = name(ev.actors[1])
            seeds.append(pats["teaching"].format(elder=elder, young=young, village=narrator.village))
            if len(seeds) >= 7:
                return seeds
            break

    # --- mass death ---
    from collections import Counter
    season_deaths: Counter = Counter()
    death_by_season: dict = {}
    for ev in w.events:
        if ev.kind == "DEATH":
            sn = ev.tick // TICKS_PER_SEASON
            season_deaths[sn] += 1
    if season_deaths:
        worst_sn, worst_n = season_deaths.most_common(1)[0]
        if worst_n >= 3:
            from .model import season_index
            season_names = t.get("season_names",
                ("Spring", "Summer", "Autumn", "Winter"))
            # fall back to EN if narrator doesn't expose season_names
            if hasattr(narrator, "t") and "seasons" in narrator.t:
                season_names_raw = narrator.t["seasons"]
                season_names_display = tuple(s[0].upper() + s[1:] for s in season_names_raw)
            else:
                season_names_display = ("Spring", "Summer", "Autumn", "Winter")
            sname = season_names_display[worst_sn % 4]
            yr = (worst_sn // 4) + 1
            seeds.append(pats["mass_death"].format(
                season=sname, year=yr, n=worst_n, village=narrator.village))
            if len(seeds) >= 7:
                return seeds

    # --- memorial ---
    for ev in w.events:
        if ev.kind == "MEMORIAL" and ev.actors:
            nm = name(ev.actors[0])
            seeds.append(pats["memorial"].format(name=nm, village=narrator.village))
            if len(seeds) >= 7:
                return seeds
            break

    # --- departure (a person pushed out or driven to leave) ---
    if "departure" in pats:
        for ev in w.events:
            if ev.kind == "DEPARTURE" and ev.actors:
                cid = ev.actors[0]
                if cid < len(w.chars):
                    seeds.append(pats["departure"].format(
                        name=w.chars[cid].name, village=narrator.village))
                    if len(seeds) >= 7:
                        return seeds
                    break

    # --- widowing + re-bond ---
    widowed = {ev.actors[0]: ev for ev in w.events if ev.kind == "WIDOWING" and ev.actors}
    for wid_id, wid_ev in widowed.items():
        if wid_id >= len(w.chars):
            continue
        c = w.chars[wid_id]
        lost_id = wid_ev.actors[1] if len(wid_ev.actors) > 1 else None
        # did this person re-bond?
        for bond_ev in w.events:
            if bond_ev.kind == "BOND" and bond_ev.tick > wid_ev.tick:
                if wid_id in bond_ev.actors[:2]:
                    new_partner_id = bond_ev.actors[1] if bond_ev.actors[0] == wid_id else bond_ev.actors[0]
                    a = c.name
                    b = name(lost_id) if lost_id is not None else "?"
                    cc = name(new_partner_id)
                    seeds.append(pats["widowing_bond"].format(a=a, b=b, c=cc, village=narrator.village))
                    if len(seeds) >= 7:
                        return seeds
                    break

    # --- long grief (widowed, never re-bonded) ---
    for wid_id, wid_ev in widowed.items():
        if wid_id >= len(w.chars):
            continue
        c = w.chars[wid_id]
        re_bonded = any(
            ev.kind == "BOND" and ev.tick > wid_ev.tick and wid_id in ev.actors[:2]
            for ev in w.events
        )
        if not re_bonded and c.alive:
            seeds.append(pats["long_grief"].format(name=c.name, village=narrator.village))
            if len(seeds) >= 7:
                return seeds
            break

    # --- illness ---
    if "illness" in pats:
        for ev in w.events:
            if ev.kind == "ILLNESS" and ev.actors:
                cid = ev.actors[0]
                if cid < len(w.chars):
                    nm = w.chars[cid].name
                    seeds.append(pats["illness"].format(name=nm, village=narrator.village))
                    if len(seeds) >= 7:
                        return seeds
                    break

    # --- jealousy ---
    if "jealousy" in pats:
        for ev in w.events:
            if ev.kind == "JEALOUSY" and len(ev.actors) >= 3:
                trio = frozenset(ev.actors[:3])
                if trio not in used_pairs:
                    used_pairs.add(trio)
                    nm = name(ev.actors[0])
                    lo = name(ev.actors[1])
                    rv = name(ev.actors[2])
                    seeds.append(pats["jealousy"].format(
                        name=nm, loved_one=lo, rival=rv, village=narrator.village))
                    if len(seeds) >= 7:
                        return seeds
                    break

    # --- legacy ---
    if "legacy" in pats:
        for ev in w.events:
            if ev.kind == "LEGACY" and len(ev.actors) >= 2:
                pair = frozenset(ev.actors[:2])
                if pair not in used_pairs:
                    used_pairs.add(pair)
                    teacher = name(ev.actors[0])
                    student = name(ev.actors[1])
                    seeds.append(pats["legacy"].format(
                        teacher=teacher, student=student, village=narrator.village))
                    if len(seeds) >= 7:
                        return seeds
                    break

    # --- pact (named close friendship) ---
    if "pact" in pats:
        for ev in w.events:
            if ev.kind == "PACT" and len(ev.actors) >= 2:
                pair = frozenset(ev.actors[:2])
                if pair not in used_pairs:
                    used_pairs.add(pair)
                    a_name = name(ev.actors[0])
                    b_name = name(ev.actors[1])
                    seeds.append(pats["pact"].format(
                        a=a_name, b=b_name, village=narrator.village))
                    if len(seeds) >= 7:
                        return seeds
                    break

    return seeds


def story_seeds(world, narrator) -> str:
    lang = getattr(narrator, "lang", "en")
    t = _SS.get(lang, _SS["en"])
    village = narrator.village

    parts = [
        t["title"].format(village=village),
        "",
        t["subtitle"].format(seed=world.seed, days=world.tick),
        "",
        t["preamble"],
        "",
    ]

    seeds = _collect_seeds(world, narrator, t)

    if not seeds:
        parts.append(t["no_seeds"])
    else:
        for i, seed_text in enumerate(seeds, 1):
            parts.append(t["seed_label"].format(n=i) + " " + seed_text)
            parts.append("")

    parts.append("")
    return "\n".join(parts)
