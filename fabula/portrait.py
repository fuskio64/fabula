"""Character portrait: a single person's story in full.

`portrait(world, narrator, name)` returns a Markdown document focused on one
character — their traits, the significant moments they lived through, how the
village saw them at the close of the record, and if they died, what was left.

Supports all five chronicle languages.
"""

from collections import defaultdict

from .model import TICKS_PER_SEASON, season_index, year_of


_PT = {
    "en": {
        "no_record":        "No record of {name}",
        "not_found":        "*No character by that name was found in {village} (seed {seed}).*",
        "adj_join":         " and ",
        "status_departed":  "left the village",
        "status_died":      "died ({cause})",
        "status_dead":      "dead",
        "status_elder":     "living, elder",
        "status_child":     "living, still a child",
        "status_living":    "living",
        "origin_born_to":   "born in {village} to {parents}",
        "origin_born":      "born in {village}",
        "origin_stranger":  "arrived in {village} as a stranger",
        "origin_founder":   "founder of {village}",
        "parent_join":      " and ",
        "section_character":  "## Character",
        "section_happened":   "## What Happened",
        "section_view":       "## How the Village Saw Them",
        "section_left":       "## What Was Left",
        "section_lost":       "## What the Village Lost",
        "trait_diligence_hi":  "tireless in the fields — the kind of person who works without being watched",
        "trait_diligence_lo":  "not known for their industry; other things occupied them",
        "trait_generosity_hi": "open-handed, with a surplus or without",
        "trait_generosity_lo": "reluctant to give; not cruel, but counted their stores",
        "trait_pride_hi":      "proud — the kind of person who would rather go hungry than ask",
        "trait_pride_lo":      "not proud; could receive help without it costing them something",
        "trait_openness_hi":   "talkative, always the first to know what was being said",
        "trait_openness_lo":   "reserved; kept what they knew to themselves",
        "regard_warm":         "warmly regarded by those still living",
        "regard_ok":           "regarded well enough",
        "regard_neutral":      "regarded with neither warmth nor coldness",
        "regard_suspect":      "regarded with some suspicion",
        "regard_poor":         "poorly regarded by most of the village",
        "view_at_departure":   "At the time {name} left, they were {regard}.",
        "view_at_close":       "At the close of this record, {name} was {regard}.",
        "closest_to":          "Closest to {name}.",
        "estranged_from":      "Most estranged from {name}.",
        "asymm_colder":        ("They held others in colder regard than the village held them — "
                                "a common asymmetry in people who have been disappointed."),
        "asymm_warmer":        "They thought better of their neighbors than their neighbors thought of them.",
        "bond_active":         "Bonded with {name}.",
        "bond_widowed":        "Bonded with {name} — now widowed.",
        "bond_lost":           "Was once bonded; their partner did not outlive them.",
        "parent_of":           "Parent of {names}.",
        "sibling_of":          "Sibling of {names}.",
        "debt_owes_one":       "Still owed a favor to {names}.",
        "debt_owes_n":         "Still owed favors to {names}.",
        "debt_owed_by_one":    "{names} still owed a favor to {char}.",
        "debt_owed_by_n":      "{names} still owed favors to {char}.",
        "quarrel_with":        "quarreled with {names}",
        "quarrel_and_others":  "quarreled with {shown}, and {n} others",
        "colophon":            "*(world seed {seed} · {village})*",
        "year":                "year",
        "seasons":             ("spring", "summer", "autumn", "winter"),
        "causes": {
            "starvation": "starvation",
            "old_age":    "old age",
            "misfortune": "misfortune",
        },
        "events": {
            "GIFT_gave":       "gave {other} bread",
            "GIFT_received":   "received bread from {other}",
            "REFUSAL_gave":    "turned {other} away empty-handed",
            "REFUSAL_received":"was turned away by {other}",
            "QUARREL":         "quarreled with {other}",
            "BOND":            "bonded with {other}",
            "WIDOWING":        "outlived {other}",
            "INGRATITUDE_gave":    "closed the door on {other} — though they had once given",
            "INGRATITUDE_received":"was turned away by {other}, after having helped them",
            "RESENTMENT":      "came to resent {other} for a debt that curdled",
            "ESTRANGEMENT":    "became permanently estranged from {other} — the silence between them became official",
            "REPAYMENT_gave":  "returned what was owed to {other}, without being asked",
            "REPAYMENT_received":"received back what was owed by {other}",
            "MEDIATION":       "was brought back to speaking terms with {other}",
            "RECONCILIATION":  "made peace with {other}",
            "BLIGHT":          "was among those whose stores were halved by a blight that season",
            "TRIBUTE_gave":    "gave bread to {other} after a death — the kind of gift that does not wait to be asked",
            "TRIBUTE_received":"received bread from {other} in the days of grief",
            "OFFENSE":         "took offense at what {other} had been saying",
            "DEATH":           "died ({cause})",
            "COMING_OF_AGE":   "came of age in the village",
        },
    },
    "es": {
        "no_record":        "Sin registro de {name}",
        "not_found":        "*No se encontró ningún personaje con ese nombre en {village} (semilla {seed}).*",
        "adj_join":         " y ",
        "status_departed":  "abandonó la aldea",
        "status_died":      "murió ({cause})",
        "status_dead":      "muerto",
        "status_elder":     "vivo, anciano",
        "status_child":     "vivo, todavía niño",
        "status_living":    "vivo",
        "origin_born_to":   "nacido en {village} de {parents}",
        "origin_born":      "nacido en {village}",
        "origin_stranger":  "llegó a {village} como forastero",
        "origin_founder":   "fundador de {village}",
        "parent_join":      " y ",
        "section_character":  "## Carácter",
        "section_happened":   "## Lo que pasó",
        "section_view":       "## Cómo lo veía la aldea",
        "section_left":       "## Lo que quedó",
        "section_lost":       "## Lo que perdió la aldea",
        "trait_diligence_hi":  "incansable en el campo — el tipo de persona que trabaja sin que nadie la mire",
        "trait_diligence_lo":  "no conocida por su laboriosidad; otras cosas la ocupaban",
        "trait_generosity_hi": "mano abierta, con excedente o sin él",
        "trait_generosity_lo": "reacia a dar; no cruel, pero contaba sus reservas",
        "trait_pride_hi":      "orgullosa — el tipo de persona que prefiere pasar hambre antes de pedir",
        "trait_pride_lo":      "sin orgullo; podía recibir ayuda sin que le costara nada",
        "trait_openness_hi":   "habladora, siempre la primera en saber lo que se decía",
        "trait_openness_lo":   "reservada; guardaba lo que sabía para sí",
        "regard_warm":         "bien vista por los que aún viven",
        "regard_ok":           "vista con suficiente benevolencia",
        "regard_neutral":      "vista sin calidez ni frialdad",
        "regard_suspect":      "vista con cierta sospecha",
        "regard_poor":         "mal vista por la mayor parte de la aldea",
        "view_at_departure":   "Cuando {name} se fue, era {regard}.",
        "view_at_close":       "Al cierre de este registro, {name} era {regard}.",
        "closest_to":          "Más cercano a {name}.",
        "estranged_from":      "Más distanciado de {name}.",
        "asymm_colder":        ("Tenía a los demás en más baja estima de la que la aldea le tenía a él — "
                                "una asimetría común en quienes han sido decepcionados."),
        "asymm_warmer":        "Pensaba mejor de sus vecinos de lo que ellos pensaban de él.",
        "bond_active":         "Unido a {name}.",
        "bond_widowed":        "Unido a {name} — ahora viudo.",
        "bond_lost":           "Estuvo unido en su día; su pareja no le sobrevivió.",
        "parent_of":           "Padre o madre de {names}.",
        "sibling_of":          "Hermano/a de {names}.",
        "debt_owes_one":       "Todavía debía un favor a {names}.",
        "debt_owes_n":         "Todavía debía favores a {names}.",
        "debt_owed_by_one":    "{names} aún le debía un favor a {char}.",
        "debt_owed_by_n":      "{names} aún le debían favores a {char}.",
        "quarrel_with":        "se peleó con {names}",
        "quarrel_and_others":  "se peleó con {shown} y {n} más",
        "colophon":            "*(semilla del mundo: {seed} · {village})*",
        "year":                "año",
        "seasons":             ("primavera", "verano", "otoño", "invierno"),
        "causes": {
            "starvation": "hambre",
            "old_age":    "vejez",
            "misfortune": "desgracia",
        },
        "events": {
            "GIFT_gave":       "le dio pan a {other}",
            "GIFT_received":   "recibió pan de {other}",
            "REFUSAL_gave":    "echó a {other} con las manos vacías",
            "REFUSAL_received":"fue echado por {other}",
            "QUARREL":         "se peleó con {other}",
            "BOND":            "se unió a {other}",
            "WIDOWING":        "sobrevivió a {other}",
            "INGRATITUDE_gave":    "cerró la puerta a {other} — aunque un día le había dado",
            "INGRATITUDE_received":"fue echado por {other}, después de haberle ayudado",
            "RESENTMENT":      "llegó a resentirse de {other} por una deuda que se agrio",
            "ESTRANGEMENT":    "quedó definitivamente distanciado de {other} — el silencio entre ellos se hizo oficial",
            "REPAYMENT_gave":  "devolvió lo que debía a {other}, sin que se lo pidieran",
            "REPAYMENT_received":"recuperó lo que {other} le debía",
            "MEDIATION":       "volvió a hablar con {other}",
            "RECONCILIATION":  "hizo las paces con {other}",
            "BLIGHT":          "fue uno de los que vio sus reservas reducidas a la mitad por una plaga esa estación",
            "TRIBUTE_gave":    "le dio pan a {other} tras una muerte — el tipo de regalo que no espera a ser pedido",
            "TRIBUTE_received":"recibió pan de {other} en los días de duelo",
            "OFFENSE":         "se ofendió por lo que {other} había dicho",
            "DEATH":           "murió ({cause})",
            "COMING_OF_AGE":   "llegó a la madurez en la aldea",
        },
    },
    "fr": {
        "no_record":        "Aucun registre de {name}",
        "not_found":        "*Aucun personnage de ce nom n'a été trouvé à {village} (graine {seed}).*",
        "adj_join":         " et ",
        "status_departed":  "quitta le village",
        "status_died":      "mourut ({cause})",
        "status_dead":      "mort",
        "status_elder":     "vivant, ancien",
        "status_child":     "vivant, encore enfant",
        "status_living":    "vivant",
        "origin_born_to":   "né à {village} de {parents}",
        "origin_born":      "né à {village}",
        "origin_stranger":  "arrivé à {village} comme étranger",
        "origin_founder":   "fondateur de {village}",
        "parent_join":      " et ",
        "section_character":  "## Caractère",
        "section_happened":   "## Ce qui s'est passé",
        "section_view":       "## Comment le village le voyait",
        "section_left":       "## Ce qui resta",
        "section_lost":       "## Ce que perdit le village",
        "trait_diligence_hi":  "infatigable aux champs — le genre de personne qui travaille sans être surveillée",
        "trait_diligence_lo":  "peu connue pour son ardeur au travail ; d'autres choses l'occupaient",
        "trait_generosity_hi": "la main ouverte, avec ou sans surplus",
        "trait_generosity_lo": "réticente à donner ; pas cruelle, mais comptait ses réserves",
        "trait_pride_hi":      "fière — le genre de personne qui préférerait avoir faim plutôt que de demander",
        "trait_pride_lo":      "sans orgueil ; pouvait recevoir de l'aide sans que cela lui coûte quelque chose",
        "trait_openness_hi":   "bavarde, toujours la première à savoir ce qui se disait",
        "trait_openness_lo":   "réservée ; gardait ce qu'elle savait pour elle",
        "regard_warm":         "chaleureusement considérée par ceux qui vivent encore",
        "regard_ok":           "considérée assez bien",
        "regard_neutral":      "considérée sans chaleur ni froideur",
        "regard_suspect":      "considérée avec quelque méfiance",
        "regard_poor":         "mal considérée par la plupart du village",
        "view_at_departure":   "Au moment où {name} est parti, il était {regard}.",
        "view_at_close":       "À la clôture de ce registre, {name} était {regard}.",
        "closest_to":          "Plus proche de {name}.",
        "estranged_from":      "Plus distant de {name}.",
        "asymm_colder":        ("Il tenait les autres en moins haute estime que le village ne le tenait — "
                                "une asymétrie courante chez les gens qui ont été déçus."),
        "asymm_warmer":        "Il pensait mieux de ses voisins que ses voisins ne pensaient de lui.",
        "bond_active":         "Lié à {name}.",
        "bond_widowed":        "Lié à {name} — maintenant veuf.",
        "bond_lost":           "Fut autrefois lié ; son partenaire ne lui survécut pas.",
        "parent_of":           "Parent de {names}.",
        "sibling_of":          "Frère/sœur de {names}.",
        "debt_owes_one":       "Devait encore un service à {names}.",
        "debt_owes_n":         "Devait encore des services à {names}.",
        "debt_owed_by_one":    "{names} devait encore un service à {char}.",
        "debt_owed_by_n":      "{names} devaient encore des services à {char}.",
        "quarrel_with":        "se querella avec {names}",
        "quarrel_and_others":  "se querella avec {shown} et {n} autres",
        "colophon":            "*(graine du monde : {seed} · {village})*",
        "year":                "an",
        "seasons":             ("le printemps", "l'été", "l'automne", "l'hiver"),
        "causes": {
            "starvation": "famine",
            "old_age":    "vieillesse",
            "misfortune": "malheur",
        },
        "events": {
            "GIFT_gave":       "donna du pain à {other}",
            "GIFT_received":   "reçut du pain de {other}",
            "REFUSAL_gave":    "renvoya {other} les mains vides",
            "REFUSAL_received":"fut renvoyé par {other}",
            "QUARREL":         "se querella avec {other}",
            "BOND":            "se lia à {other}",
            "WIDOWING":        "survécut à {other}",
            "INGRATITUDE_gave":    "ferma la porte à {other} — alors qu'il lui avait autrefois donné",
            "INGRATITUDE_received":"fut renvoyé par {other}, après l'avoir aidé",
            "RESENTMENT":      "en vint à en vouloir à {other} pour une dette qui s'aigrit",
            "ESTRANGEMENT":    "devint définitivement brouillé avec {other} — le silence entre eux devint officiel",
            "REPAYMENT_gave":  "rendit ce qu'il devait à {other}, sans qu'on le lui demande",
            "REPAYMENT_received":"récupéra ce que {other} lui devait",
            "MEDIATION":       "fut ramené à parler avec {other}",
            "RECONCILIATION":  "fit la paix avec {other}",
            "BLIGHT":          "fut parmi ceux dont les réserves furent réduites de moitié par une maladie des cultures cette saison-là",
            "TRIBUTE_gave":    "apporta du pain à {other} après un décès — le genre de don qui n'attend pas d'être demandé",
            "TRIBUTE_received":"reçut du pain de {other} dans les jours de deuil",
            "OFFENSE":         "s'offensa de ce que {other} avait dit",
            "DEATH":           "mourut ({cause})",
            "COMING_OF_AGE":   "atteignit l'âge adulte dans le village",
        },
    },
    "pt": {
        "no_record":        "Sem registo de {name}",
        "not_found":        "*Não foi encontrado nenhum personagem com esse nome em {village} (semente {seed}).*",
        "adj_join":         " e ",
        "status_departed":  "saiu da aldeia",
        "status_died":      "morreu ({cause})",
        "status_dead":      "morto",
        "status_elder":     "vivo, ancião",
        "status_child":     "vivo, ainda criança",
        "status_living":    "vivo",
        "origin_born_to":   "nascido em {village} de {parents}",
        "origin_born":      "nascido em {village}",
        "origin_stranger":  "chegou a {village} como estranho",
        "origin_founder":   "fundador de {village}",
        "parent_join":      " e ",
        "section_character":  "## Carácter",
        "section_happened":   "## O que aconteceu",
        "section_view":       "## Como a aldeia o via",
        "section_left":       "## O que ficou",
        "section_lost":       "## O que a aldeia perdeu",
        "trait_diligence_hi":  "incansável nos campos — o tipo de pessoa que trabalha sem ser vigiada",
        "trait_diligence_lo":  "não conhecida pelo seu empenho; outras coisas a ocupavam",
        "trait_generosity_hi": "mão aberta, com excedente ou sem ele",
        "trait_generosity_lo": "relutante em dar; não cruel, mas contava as suas reservas",
        "trait_pride_hi":      "orgulhosa — o tipo de pessoa que prefere passar fome a pedir",
        "trait_pride_lo":      "sem orgulho; podia receber ajuda sem que isso lhe custasse nada",
        "trait_openness_hi":   "faladora, sempre a primeira a saber o que se dizia",
        "trait_openness_lo":   "reservada; guardava o que sabia para si",
        "regard_warm":         "vista com carinho pelos que ainda vivem",
        "regard_ok":           "vista com suficiente benevolência",
        "regard_neutral":      "vista sem calor nem frieza",
        "regard_suspect":      "vista com alguma desconfiança",
        "regard_poor":         "mal vista pela maior parte da aldeia",
        "view_at_departure":   "Quando {name} saiu, era {regard}.",
        "view_at_close":       "No encerramento deste registo, {name} era {regard}.",
        "closest_to":          "Mais próximo de {name}.",
        "estranged_from":      "Mais afastado de {name}.",
        "asymm_colder":        ("Tinha os outros em menor apreço do que a aldeia o tinha a ele — "
                                "uma assimetria comum em pessoas que foram desiludidas."),
        "asymm_warmer":        "Pensava melhor dos seus vizinhos do que eles pensavam dele.",
        "bond_active":         "Ligado a {name}.",
        "bond_widowed":        "Ligado a {name} — agora viúvo.",
        "bond_lost":           "Esteve ligado outrora; o seu parceiro não lhe sobreviveu.",
        "parent_of":           "Pai ou mãe de {names}.",
        "sibling_of":          "Irmão/irmã de {names}.",
        "debt_owes_one":       "Ainda devia um favor a {names}.",
        "debt_owes_n":         "Ainda devia favores a {names}.",
        "debt_owed_by_one":    "{names} ainda devia um favor a {char}.",
        "debt_owed_by_n":      "{names} ainda deviam favores a {char}.",
        "quarrel_with":        "discutiu com {names}",
        "quarrel_and_others":  "discutiu com {shown} e mais {n}",
        "colophon":            "*(semente do mundo: {seed} · {village})*",
        "year":                "ano",
        "seasons":             ("a primavera", "o verão", "o outono", "o inverno"),
        "causes": {
            "starvation": "fome",
            "old_age":    "velhice",
            "misfortune": "desgraça",
        },
        "events": {
            "GIFT_gave":       "deu pão a {other}",
            "GIFT_received":   "recebeu pão de {other}",
            "REFUSAL_gave":    "mandou {other} embora de mãos vazias",
            "REFUSAL_received":"foi mandado embora por {other}",
            "QUARREL":         "discutiu com {other}",
            "BOND":            "ligou-se a {other}",
            "WIDOWING":        "sobreviveu a {other}",
            "INGRATITUDE_gave":    "fechou a porta a {other} — embora lhe tivesse dado outrora",
            "INGRATITUDE_received":"foi mandado embora por {other}, depois de o ter ajudado",
            "RESENTMENT":      "chegou a guardar rancor de {other} por uma dívida que azedou",
            "ESTRANGEMENT":    "ficou definitivamente afastado de {other} — o silêncio entre eles tornou-se oficial",
            "REPAYMENT_gave":  "devolveu o que devia a {other}, sem que lhe fosse pedido",
            "REPAYMENT_received":"recuperou o que {other} lhe devia",
            "MEDIATION":       "voltou a falar com {other}",
            "RECONCILIATION":  "fez as pazes com {other}",
            "BLIGHT":          "foi um dos que viu as suas reservas reduzidas a metade por uma praga nessa estação",
            "TRIBUTE_gave":    "deu pão a {other} após uma morte — o tipo de oferenda que não espera ser pedida",
            "TRIBUTE_received":"recebeu pão de {other} nos dias de luto",
            "OFFENSE":         "ofendeu-se com o que {other} tinha dito",
            "DEATH":           "morreu ({cause})",
            "COMING_OF_AGE":   "atingiu a maioridade na aldeia",
        },
    },
    "it": {
        "no_record":        "Nessun registro di {name}",
        "not_found":        "*Nessun personaggio con quel nome è stato trovato a {village} (seme {seed}).*",
        "adj_join":         " e ",
        "status_departed":  "lasciò il villaggio",
        "status_died":      "morì ({cause})",
        "status_dead":      "morto",
        "status_elder":     "vivo, anziano",
        "status_child":     "vivo, ancora bambino",
        "status_living":    "vivo",
        "origin_born_to":   "nato a {village} da {parents}",
        "origin_born":      "nato a {village}",
        "origin_stranger":  "arrivò a {village} come straniero",
        "origin_founder":   "fondatore di {village}",
        "parent_join":      " e ",
        "section_character":  "## Carattere",
        "section_happened":   "## Cosa è successo",
        "section_view":       "## Come lo vedeva il villaggio",
        "section_left":       "## Ciò che rimase",
        "section_lost":       "## Ciò che il villaggio perse",
        "trait_diligence_hi":  "instancabile nei campi — il tipo di persona che lavora senza essere sorvegliata",
        "trait_diligence_lo":  "non nota per la sua laboriosità; altre cose la occupavano",
        "trait_generosity_hi": "a mani aperte, con o senza surplus",
        "trait_generosity_lo": "riluttante a dare; non crudele, ma contava le sue riserve",
        "trait_pride_hi":      "orgogliosa — il tipo di persona che preferirebbe avere fame piuttosto che chiedere",
        "trait_pride_lo":      "senza orgoglio; poteva ricevere aiuto senza che le costasse qualcosa",
        "trait_openness_hi":   "loquace, sempre la prima a sapere cosa si diceva",
        "trait_openness_lo":   "riservata; teneva per sé quello che sapeva",
        "regard_warm":         "vista con calore da chi è ancora in vita",
        "regard_ok":           "vista abbastanza bene",
        "regard_neutral":      "vista senza calore né freddezza",
        "regard_suspect":      "vista con qualche sospetto",
        "regard_poor":         "vista male dalla maggior parte del villaggio",
        "view_at_departure":   "Al momento in cui {name} partì, era {regard}.",
        "view_at_close":       "Alla chiusura di questo registro, {name} era {regard}.",
        "closest_to":          "Più vicino a {name}.",
        "estranged_from":      "Più distante da {name}.",
        "asymm_colder":        ("Teneva gli altri in minor considerazione di quanto il villaggio tenesse lui — "
                                "un'asimmetria comune nelle persone che sono state deluse."),
        "asymm_warmer":        "Pensava meglio dei suoi vicini di quanto loro pensassero di lui.",
        "bond_active":         "Legato a {name}.",
        "bond_widowed":        "Legato a {name} — ora vedovo.",
        "bond_lost":           "Fu un tempo legato; il suo partner non gli sopravvisse.",
        "parent_of":           "Genitore di {names}.",
        "sibling_of":          "Fratello/sorella di {names}.",
        "debt_owes_one":       "Doveva ancora un favore a {names}.",
        "debt_owes_n":         "Doveva ancora dei favori a {names}.",
        "debt_owed_by_one":    "{names} doveva ancora un favore a {char}.",
        "debt_owed_by_n":      "{names} dovevano ancora dei favori a {char}.",
        "quarrel_with":        "litigò con {names}",
        "quarrel_and_others":  "litigò con {shown} e altri {n}",
        "colophon":            "*(seme del mondo: {seed} · {village})*",
        "year":                "anno",
        "seasons":             ("la primavera", "l'estate", "l'autunno", "l'inverno"),
        "causes": {
            "starvation": "inedia",
            "old_age":    "vecchiaia",
            "misfortune": "sventura",
        },
        "events": {
            "GIFT_gave":       "diede del pane a {other}",
            "GIFT_received":   "ricevette del pane da {other}",
            "REFUSAL_gave":    "mandò via {other} a mani vuote",
            "REFUSAL_received":"fu mandato via da {other}",
            "QUARREL":         "litigò con {other}",
            "BOND":            "si legò a {other}",
            "WIDOWING":        "sopravvisse a {other}",
            "INGRATITUDE_gave":    "chiuse la porta a {other} — benché gli avesse dato una volta",
            "INGRATITUDE_received":"fu mandato via da {other}, dopo averlo aiutato",
            "RESENTMENT":      "arrivò a risentirsi di {other} per un debito che si inasprì",
            "ESTRANGEMENT":    "divenne definitivamente estraniato da {other} — il silenzio tra loro divenne ufficiale",
            "REPAYMENT_gave":  "restituì ciò che doveva a {other}, senza che glielo chiedessero",
            "REPAYMENT_received":"recuperò ciò che {other} gli doveva",
            "MEDIATION":       "fu portato a parlare di nuovo con {other}",
            "RECONCILIATION":  "fece pace con {other}",
            "BLIGHT":          "fu tra quelli le cui riserve furono dimezzate da una malattia dei raccolti quella stagione",
            "TRIBUTE_gave":    "portò del pane a {other} dopo una morte — il tipo di dono che non aspetta di essere chiesto",
            "TRIBUTE_received":"ricevette del pane da {other} nei giorni di lutto",
            "OFFENSE":         "si offese per quello che {other} aveva detto",
            "DEATH":           "morì ({cause})",
            "COMING_OF_AGE":   "raggiunse l'età adulta nel villaggio",
        },
    },
}


def _event_desc(t: dict, ev, cid: int, world) -> str:
    others = [a for a in ev.actors if a != cid]
    other = world.char(others[0]).name if others else "—"
    et = t["events"]
    kind = ev.kind

    if kind == "GIFT":
        key = "GIFT_gave" if ev.actors[0] == cid else "GIFT_received"
    elif kind == "REFUSAL":
        key = "REFUSAL_gave" if ev.actors[0] == cid else "REFUSAL_received"
    elif kind == "INGRATITUDE":
        key = "INGRATITUDE_gave" if ev.actors[0] == cid else "INGRATITUDE_received"
    elif kind == "REPAYMENT":
        key = "REPAYMENT_gave" if ev.actors[0] == cid else "REPAYMENT_received"
    elif kind == "TRIBUTE":
        key = "TRIBUTE_gave" if ev.actors[0] == cid else "TRIBUTE_received"
    elif kind == "WIDOWING":
        if ev.actors[0] != cid:
            return ""
        key = "WIDOWING"
    elif kind == "MEDIATION":
        if cid not in ev.actors[:2]:
            return ""
        key = "MEDIATION"
    elif kind == "OFFENSE":
        if ev.actors[0] != cid:
            return ""
        key = "OFFENSE"
    else:
        key = kind

    template = et.get(key, "")
    if not template:
        return ""

    if kind == "DEATH":
        raw = ev.data.get("cause", "")
        cause = t.get("causes", {}).get(raw, raw.replace("_", " "))
        return template.format(cause=cause)
    return template.format(other=other)


def portrait(world, narrator, char_name: str) -> str:
    lang = getattr(narrator, "lang", "en")
    t = _PT.get(lang, _PT["en"])

    char = next(
        (c for c in world.chars if c.name.lower() == char_name.lower()), None
    )
    if char is None:
        return (
            f"# {t['no_record'].format(name=char_name)}\n\n"
            f"{t['not_found'].format(village=narrator.village, seed=world.seed)}\n"
        )

    village = narrator.village
    adjs = narrator.adjectives(char)
    adj_str = t["adj_join"].join(adjs)

    if not char.alive:
        if char.departed:
            status = t["status_departed"]
        else:
            cause_raw = narrator.death_cause(char.id)
            cause = t.get("causes", {}).get(cause_raw, (cause_raw or "").replace("_", " "))
            status = (t["status_died"].format(cause=cause)
                      if cause_raw else t["status_dead"])
    elif char.elder:
        status = t["status_elder"]
    elif char.childhood:
        status = t["status_child"]
    else:
        status = t["status_living"]

    if char.parent_ids:
        parent_names = [world.char(pid).name for pid in char.parent_ids
                        if pid < len(world.chars)]
        if parent_names:
            parents_str = t["parent_join"].join(parent_names)
            origin = t["origin_born_to"].format(village=village, parents=parents_str)
        else:
            origin = t["origin_born"].format(village=village)
    elif char.joined_at > 0:
        origin = t["origin_stranger"].format(village=village)
    else:
        origin = t["origin_founder"].format(village=village)

    def _cap(s: str) -> str:
        return s[0].upper() + s[1:] if s else s

    parts = [f"# {char.name}", "", f"*{_cap(origin)}. {_cap(adj_str)}. {_cap(status)}.*", ""]

    # --- Traits section ---
    trait_notes = []
    if char.diligence > 0.65:
        trait_notes.append(t["trait_diligence_hi"])
    elif char.diligence < 0.35:
        trait_notes.append(t["trait_diligence_lo"])
    if char.generosity > 0.65:
        trait_notes.append(t["trait_generosity_hi"])
    elif char.generosity < 0.35:
        trait_notes.append(t["trait_generosity_lo"])
    if char.pride > 0.65:
        trait_notes.append(t["trait_pride_hi"])
    elif char.pride < 0.35:
        trait_notes.append(t["trait_pride_lo"])
    if char.openness > 0.65:
        trait_notes.append(t["trait_openness_hi"])
    elif char.openness < 0.35:
        trait_notes.append(t["trait_openness_lo"])

    if trait_notes:
        parts.append(t["section_character"])
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
        parts.append(t["section_happened"])
        parts.append("")
        seasons = t["seasons"]
        year_word = t["year"]

        season_kind_groups: dict = defaultdict(list)
        for ev in top_sorted:
            season_kind_groups[(ev.kind, season_index(ev.tick), year_of(ev.tick))].append(ev)

        seen_sk: set = set()
        for ev in top_sorted:
            sk = (ev.kind, season_index(ev.tick), year_of(ev.tick))
            if sk in seen_sk:
                continue
            seen_sk.add(sk)
            group = season_kind_groups[sk]
            when = f"{seasons[sk[1]]}, {year_word} {sk[2]}"

            if len(group) >= 3 and ev.kind == "QUARREL":
                names = []
                for ge in group:
                    others = [a for a in ge.actors if a != char.id]
                    if others:
                        names.append(world.char(others[0]).name)
                if len(names) > 4:
                    shown = ", ".join(names[:3])
                    desc = t["quarrel_and_others"].format(shown=shown, n=len(names) - 3)
                elif len(names) > 1:
                    desc = t["quarrel_with"].format(
                        names=", ".join(names[:-1]) + f", {t['adj_join'].strip()} {names[-1]}")
                else:
                    desc = t["quarrel_with"].format(names=names[0])
                parts.append(f"- *{when.capitalize()}:* {desc}.")
            else:
                desc = _event_desc(t, ev, char.id, world)
                if desc:
                    parts.append(f"- *{when.capitalize()}:* {desc}.")
        parts.append("")

    # --- How the village saw them ---
    living_others = [c for c in world.chars if c.id != char.id and c.alive]
    if living_others:
        avg_in = sum(c.feel(char.id) for c in living_others) / len(living_others)
        avg_out = sum(char.feel(c.id) for c in living_others) / len(living_others)

        if avg_in > 0.3:     regard = t["regard_warm"]
        elif avg_in > 0.05:  regard = t["regard_ok"]
        elif avg_in > -0.1:  regard = t["regard_neutral"]
        elif avg_in > -0.3:  regard = t["regard_suspect"]
        else:                 regard = t["regard_poor"]

        parts.append(t["section_view"])
        parts.append("")
        if not char.alive and char.departed:
            parts.append(t["view_at_departure"].format(name=char.name, regard=regard))
        else:
            parts.append(t["view_at_close"].format(name=char.name, regard=regard))

        def mutual(c):
            return (c.feel(char.id) + char.feel(c.id)) / 2

        best = max(living_others, key=mutual)
        worst = min(living_others, key=mutual)
        best_val = mutual(best)
        worst_val = mutual(worst)

        if best_val > 0.25 and char.partner != best.id:
            parts.append(t["closest_to"].format(name=best.name))
        if worst_val < -0.15:
            parts.append(t["estranged_from"].format(name=worst.name))

        if avg_out < -0.05 and abs(avg_in - avg_out) > 0.15:
            if avg_out < avg_in:
                parts.append(t["asymm_colder"])
            else:
                parts.append(t["asymm_warmer"])
        parts.append("")

    # --- Bond and family ---
    bond_lines = []
    if char.partner is not None:
        partner = world.char(char.partner)
        if partner.alive:
            bond_lines.append(t["bond_active"].format(name=partner.name))
        else:
            bond_lines.append(t["bond_widowed"].format(name=partner.name))
    elif any(ev.kind == "BOND" and char.id in ev.actors for ev in world.events):
        bond_lines.append(t["bond_lost"])

    children = [c for c in world.chars if c.parent_ids and char.id in c.parent_ids]
    if children:
        names = ", ".join(c.name for c in children)
        bond_lines.append(t["parent_of"].format(names=names))

    if char.parent_ids:
        siblings = [
            c for c in world.chars
            if c.id != char.id and c.parent_ids and set(c.parent_ids) == set(char.parent_ids)
        ]
        if siblings:
            names = ", ".join(c.name for c in siblings)
            bond_lines.append(t["sibling_of"].format(names=names))

    if bond_lines:
        parts += bond_lines + [""]

    # --- Debts ---
    debt_lines = []
    if char.debts:
        cred = [narrator.name(d.creditor) for d in char.debts.values()]
        names_str = ", ".join(cred)
        debt_lines.append(
            (t["debt_owes_one"] if len(cred) == 1 else t["debt_owes_n"]).format(names=names_str))
    owed_by = [c for c in world.chars if char.id in c.debts]
    if owed_by:
        names = ", ".join(c.name for c in owed_by)
        debt_lines.append(
            (t["debt_owed_by_one"] if len(owed_by) == 1 else t["debt_owed_by_n"])
            .format(names=names, char=char.name))
    if debt_lines:
        parts += debt_lines + [""]

    # --- Death/departure legacy ---
    if not char.alive:
        if char.departed:
            legacy = narrator.death_legacy(char.id)
            if legacy:
                parts += [t["section_lost"], "", legacy, ""]
        else:
            legacy = narrator.death_legacy(char.id)
            if legacy:
                parts += [t["section_left"], "", legacy, ""]

    parts.append(t["colophon"].format(seed=world.seed, village=village))
    parts.append("")
    return "\n".join(parts)
