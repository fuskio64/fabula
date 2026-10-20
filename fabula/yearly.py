"""Year-by-year logbook.

`yearly(world, narrator)` returns a Markdown logbook structured by year and
season — the same events as the chronicle, but laid out as a ledger so the
reader can scan what happened when.

Notable events (deaths, bonds, births, estrangements) are named individually.
Minor events (gifts, quarrels) are collapsed to counts. Supports all five
chronicle languages.
"""

from collections import defaultdict

from .model import TICKS_PER_SEASON, season_index, year_of


_YT = {
    "en": {
        "title":         "The Logbook of {village}",
        "subtitle":      "*World seed {seed} · {seasons} seasons · {people} souls at opening*",
        "year_header":   "## Year {n}",
        "pop_no_deaths": "*{alive} souls at spring. No deaths.*",
        "pop_one_death": "*{alive} souls at spring. {names} died.*",
        "pop_deaths":    "*{alive} souls at spring. {dead} deaths: {names}.*",
        "season_names":  ("Spring", "Summer", "Autumn", "Winter"),
        "season_lean":   "Lean season.",
        "season_blight": "Blight.",
        "season_bounty": "Plenty.",
        "event_bond":        "{a} and {b} chose each other.",
        "event_death":       "{a} died ({cause}).",
        "event_birth":       "{child} born.",
        "event_estrange":    "{a} and {b} stopped speaking.",
        "event_reconcile":   "{a} and {b} made peace.",
        "event_mediation":   "{a} and {b} were brought to speak.",
        "event_tribute":     "{a} brought bread to {b}.",
        "event_ingrat":      "{b} turned away {a} (who had given).",
        "event_resent":      "{a} came to resent {b}.",
        "event_arrival":     "{a} arrived.",
        "event_departure":   "{a} left.",
        "event_coming_of_age": "{a} came of age.",
        "event_adoption":      "{pa} and {pb} took in {child}.",
        "event_teaching":      "{elder} taught {young}.",
        "event_memorial":      "The village gathered for {name}.",
        "event_feud":          "{a} and {b} came to open war.",
        "event_illness":       "{a} fell ill.",
        "event_recovery":      "{a} recovered.",
        "event_jealousy":      "{name} turned cold after {loved_one} and {rival} bonded.",
        "event_legacy":        "{student} kept working in {teacher}'s way.",
        "event_drought":       "Drought — two seasons of thin harvest.",
        "event_drought_end":   "The drought broke.",
        "event_celebration":   "A birth — the village gathered.",
        "event_pact":          "{a} and {b} named what they had.",
        "event_vigil":         "The village gathered around {name}.",
        "count_gifts":         "{n} gift",
        "count_gifts_pl":      "{n} gifts",
        "count_quarrels":      "{n} quarrel",
        "count_quarrels_pl":   "{n} quarrels",
        "count_refusals":      "{n} refusal",
        "count_refusals_pl":   "{n} refusals",
        "count_repayments":    "{n} debt repaid",
        "count_repayments_pl": "{n} debts repaid",
        "tone_deaths":   "A hard year.",
        "tone_bonds":    "A year of warmth.",
        "tone_quarrels": "A contentious year.",
        "tone_lean":     "The village went hungry much of this year.",
        "tone_quiet":    "A quiet year.",
        "colophon":      "*(world seed {seed} — same seed, same logbook, every time)*",
        "founders_line":  "*Founders: {names}.*",
        "close_header":  "## At the close",
        "close_alive":   "*{n} souls remain: {names}.*",
        "close_bonds":   "Bonds still standing: {pairs}.",
        "close_no_bonds":"No bonds remaining.",
        "causes": {
            "starvation": "starvation",
            "old_age":    "old age",
            "misfortune": "misfortune",
        },
    },
    "es": {
        "title":         "El diario de {village}",
        "subtitle":      "*Semilla: {seed} · {seasons} estaciones · {people} almas al inicio*",
        "year_header":   "## Año {n}",
        "pop_no_deaths": "*{alive} almas en primavera. Sin muertes.*",
        "pop_one_death": "*{alive} almas en primavera. Murió {names}.*",
        "pop_deaths":    "*{alive} almas en primavera. {dead} muertes: {names}.*",
        "season_names":  ("Primavera", "Verano", "Otoño", "Invierno"),
        "season_lean":   "Escasez.",
        "season_blight": "Plaga.",
        "season_bounty": "Abundancia.",
        "event_bond":        "{a} y {b} se eligieron.",
        "event_death":       "{a} murió ({cause}).",
        "event_birth":       "{child} nació.",
        "event_estrange":    "{a} y {b} dejaron de hablarse.",
        "event_reconcile":   "{a} y {b} hicieron las paces.",
        "event_mediation":   "{a} y {b} volvieron a hablarse.",
        "event_tribute":     "{a} le llevó pan a {b}.",
        "event_ingrat":      "{b} echó a {a} (que había dado).",
        "event_resent":      "{a} empezó a resentirse de {b}.",
        "event_arrival":     "{a} llegó.",
        "event_departure":   "{a} se fue.",
        "event_coming_of_age": "{a} llegó a la edad adulta.",
        "event_adoption":      "{pa} y {pb} acogieron a {child}.",
        "event_teaching":      "{elder} enseñó a {young}.",
        "event_memorial":      "La aldea se reunió por {name}.",
        "event_feud":          "{a} y {b} llegaron a la guerra abierta.",
        "event_illness":       "{a} cayó enfermo.",
        "event_recovery":      "{a} se recuperó.",
        "event_jealousy":      "{name} se enfrió tras el vínculo de {loved_one} y {rival}.",
        "event_legacy":        "{student} siguió trabajando a la manera de {teacher}.",
        "event_drought":       "Sequía — dos estaciones de cosechas escasas.",
        "event_drought_end":   "La sequía se rompió.",
        "event_celebration":   "Un nacimiento — la aldea se reunió.",
        "event_pact":          "{a} y {b} pusieron nombre a lo que tenían.",
        "event_vigil":         "La aldea se reunió alrededor de {name}.",
        "count_gifts":         "{n} regalo",
        "count_gifts_pl":      "{n} regalos",
        "count_quarrels":      "{n} pelea",
        "count_quarrels_pl":   "{n} peleas",
        "count_refusals":      "{n} negativa",
        "count_refusals_pl":   "{n} negativas",
        "count_repayments":    "{n} deuda saldada",
        "count_repayments_pl": "{n} deudas saldadas",
        "tone_deaths":   "Un año duro.",
        "tone_bonds":    "Un año cálido.",
        "tone_quarrels": "Un año de disputas.",
        "tone_lean":     "La aldea pasó hambre buena parte del año.",
        "tone_quiet":    "Un año tranquilo.",
        "colophon":      "*(semilla: {seed} — misma semilla, mismo diario, siempre)*",
        "founders_line":  "*Fundadores: {names}.*",
        "close_header":  "## Al cierre",
        "close_alive":   "*{n} almas siguen: {names}.*",
        "close_bonds":   "Vínculos en pie: {pairs}.",
        "close_no_bonds":"Sin vínculos supervivientes.",
        "causes": {
            "starvation": "hambre",
            "old_age":    "vejez",
            "misfortune": "desgracia",
        },
    },
    "fr": {
        "title":         "Le journal de {village}",
        "subtitle":      "*Graine : {seed} · {seasons} saisons · {people} âmes à l'ouverture*",
        "year_header":   "## An {n}",
        "pop_no_deaths": "*{alive} âmes au printemps. Pas de morts.*",
        "pop_one_death": "*{alive} âmes au printemps. {names} mourut.*",
        "pop_deaths":    "*{alive} âmes au printemps. {dead} morts : {names}.*",
        "season_names":  ("Printemps", "Été", "Automne", "Hiver"),
        "season_lean":   "Disette.",
        "season_blight": "Fléau.",
        "season_bounty": "Abondance.",
        "event_bond":        "{a} et {b} se choisirent.",
        "event_death":       "{a} mourut ({cause}).",
        "event_birth":       "{child} naquit.",
        "event_estrange":    "{a} et {b} cessèrent de se parler.",
        "event_reconcile":   "{a} et {b} firent la paix.",
        "event_mediation":   "{a} et {b} furent remis en contact.",
        "event_tribute":     "{a} apporta du pain à {b}.",
        "event_ingrat":      "{b} renvoya {a} (qui avait donné).",
        "event_resent":      "{a} en vint à en vouloir à {b}.",
        "event_arrival":     "{a} arriva.",
        "event_departure":   "{a} repartit.",
        "event_coming_of_age": "{a} devint adulte.",
        "event_adoption":      "{pa} et {pb} recueillirent {child}.",
        "event_teaching":      "{elder} enseigna à {young}.",
        "event_memorial":      "Le village se rassembla pour {name}.",
        "event_feud":          "{a} et {b} en vinrent à la guerre ouverte.",
        "event_illness":       "{a} tomba malade.",
        "event_recovery":      "{a} se remit.",
        "event_jealousy":      "{name} se refroidit après le lien entre {loved_one} et {rival}.",
        "event_legacy":        "{student} continua à travailler à la manière de {teacher}.",
        "event_drought":       "Sécheresse — deux saisons de maigres récoltes.",
        "event_drought_end":   "La sécheresse prit fin.",
        "event_celebration":   "Une naissance — le village se rassembla.",
        "event_pact":          "{a} et {b} nommèrent ce qu'ils avaient.",
        "event_vigil":         "Le village se rassembla autour de {name}.",
        "count_gifts":         "{n} don",
        "count_gifts_pl":      "{n} dons",
        "count_quarrels":      "{n} querelle",
        "count_quarrels_pl":   "{n} querelles",
        "count_refusals":      "{n} refus",
        "count_refusals_pl":   "{n} refus",
        "count_repayments":    "{n} dette remboursée",
        "count_repayments_pl": "{n} dettes remboursées",
        "tone_deaths":   "Une année difficile.",
        "tone_bonds":    "Une année chaleureuse.",
        "tone_quarrels": "Une année de querelles.",
        "tone_lean":     "Le village a souffert de la faim une bonne partie de l'année.",
        "tone_quiet":    "Une année tranquille.",
        "colophon":      "*(graine : {seed} — même graine, même journal, toujours)*",
        "founders_line":  "*Fondateurs : {names}.*",
        "close_header":  "## À la clôture",
        "close_alive":   "*{n} âmes restent : {names}.*",
        "close_bonds":   "Liens encore debout : {pairs}.",
        "close_no_bonds":"Aucun lien survivant.",
        "causes": {
            "starvation": "famine",
            "old_age":    "vieillesse",
            "misfortune": "malheur",
        },
    },
    "pt": {
        "title":         "O diário de {village}",
        "subtitle":      "*Semente: {seed} · {seasons} estações · {people} almas na abertura*",
        "year_header":   "## Ano {n}",
        "pop_no_deaths": "*{alive} almas na primavera. Sem mortes.*",
        "pop_one_death": "*{alive} almas na primavera. {names} morreu.*",
        "pop_deaths":    "*{alive} almas na primavera. {dead} mortes: {names}.*",
        "season_names":  ("Primavera", "Verão", "Outono", "Inverno"),
        "season_lean":   "Escassez.",
        "season_blight": "Praga.",
        "season_bounty": "Abundância.",
        "event_bond":        "{a} e {b} escolheram-se.",
        "event_death":       "{a} morreu ({cause}).",
        "event_birth":       "{child} nasceu.",
        "event_estrange":    "{a} e {b} deixaram de se falar.",
        "event_reconcile":   "{a} e {b} fizeram as pazes.",
        "event_mediation":   "{a} e {b} foram postos em contacto.",
        "event_tribute":     "{a} levou pão a {b}.",
        "event_ingrat":      "{b} mandou {a} embora (que tinha dado).",
        "event_resent":      "{a} passou a guardar rancor de {b}.",
        "event_arrival":     "{a} chegou.",
        "event_departure":   "{a} saiu.",
        "event_coming_of_age": "{a} chegou à maioridade.",
        "event_adoption":      "{pa} e {pb} acolheram {child}.",
        "event_teaching":      "{elder} ensinou {young}.",
        "event_memorial":      "A aldeia reuniu-se por {name}.",
        "event_feud":          "{a} e {b} chegaram à guerra aberta.",
        "event_illness":       "{a} adoeceu.",
        "event_recovery":      "{a} recuperou.",
        "event_jealousy":      "{name} ficou frio após o vínculo entre {loved_one} e {rival}.",
        "event_legacy":        "{student} continuou a trabalhar à maneira de {teacher}.",
        "event_drought":       "Seca — duas estações de colheitas magras.",
        "event_drought_end":   "A seca terminou.",
        "event_celebration":   "Um nascimento — a aldeia reuniu-se.",
        "event_pact":          "{a} e {b} deram nome ao que tinham.",
        "event_vigil":         "A aldeia reuniu-se à volta de {name}.",
        "count_gifts":         "{n} dádiva",
        "count_gifts_pl":      "{n} dádivas",
        "count_quarrels":      "{n} disputa",
        "count_quarrels_pl":   "{n} disputas",
        "count_refusals":      "{n} recusa",
        "count_refusals_pl":   "{n} recusas",
        "count_repayments":    "{n} dívida saldada",
        "count_repayments_pl": "{n} dívidas saldadas",
        "tone_deaths":   "Um ano difícil.",
        "tone_bonds":    "Um ano quente.",
        "tone_quarrels": "Um ano de disputas.",
        "tone_lean":     "A aldeia passou fome boa parte do ano.",
        "tone_quiet":    "Um ano tranquilo.",
        "colophon":      "*(semente: {seed} — mesma semente, mesmo diário, sempre)*",
        "founders_line":  "*Fundadores: {names}.*",
        "close_header":  "## No fecho",
        "close_alive":   "*{n} almas restam: {names}.*",
        "close_bonds":   "Vínculos ainda de pé: {pairs}.",
        "close_no_bonds":"Sem vínculos sobreviventes.",
        "causes": {
            "starvation": "fome",
            "old_age":    "velhice",
            "misfortune": "desgraça",
        },
    },
    "it": {
        "title":         "Il diario di {village}",
        "subtitle":      "*Seme: {seed} · {seasons} stagioni · {people} anime all'apertura*",
        "year_header":   "## Anno {n}",
        "pop_no_deaths": "*{alive} anime in primavera. Nessun morto.*",
        "pop_one_death": "*{alive} anime in primavera. {names} morì.*",
        "pop_deaths":    "*{alive} anime in primavera. {dead} morti: {names}.*",
        "season_names":  ("Primavera", "Estate", "Autunno", "Inverno"),
        "season_lean":   "Magra.",
        "season_blight": "Flagello.",
        "season_bounty": "Abbondanza.",
        "event_bond":        "{a} e {b} si scelsero.",
        "event_death":       "{a} morì ({cause}).",
        "event_birth":       "{child} nacque.",
        "event_estrange":    "{a} e {b} smisero di parlarsi.",
        "event_reconcile":   "{a} e {b} fecero pace.",
        "event_mediation":   "{a} e {b} furono messi in contatto.",
        "event_tribute":     "{a} portò del pane a {b}.",
        "event_ingrat":      "{b} mandò via {a} (che aveva dato).",
        "event_resent":      "{a} cominciò a risentirsi di {b}.",
        "event_arrival":     "{a} arrivò.",
        "event_departure":   "{a} se ne andò.",
        "event_coming_of_age": "{a} divenne adulto.",
        "event_adoption":      "{pa} e {pb} accolsero {child}.",
        "event_teaching":      "{elder} insegnò a {young}.",
        "event_memorial":      "Il villaggio si riunì per {name}.",
        "event_feud":          "{a} e {b} arrivarono alla guerra aperta.",
        "event_illness":       "{a} si ammalò.",
        "event_recovery":      "{a} si riprese.",
        "event_jealousy":      "{name} si raffreddò dopo il legame tra {loved_one} e {rival}.",
        "event_legacy":        "{student} continuò a lavorare alla maniera di {teacher}.",
        "event_drought":       "Siccità — due stagioni di magri raccolti.",
        "event_drought_end":   "La siccità si spezzò.",
        "event_celebration":   "Una nascita — il villaggio si radunò.",
        "event_pact":          "{a} e {b} diedero un nome a quello che avevano.",
        "event_vigil":         "Il villaggio si radunò attorno a {name}.",
        "count_gifts":         "{n} dono",
        "count_gifts_pl":      "{n} doni",
        "count_quarrels":      "{n} lite",
        "count_quarrels_pl":   "{n} liti",
        "count_refusals":      "{n} rifiuto",
        "count_refusals_pl":   "{n} rifiuti",
        "count_repayments":    "{n} debito saldato",
        "count_repayments_pl": "{n} debiti saldati",
        "tone_deaths":   "Un anno difficile.",
        "tone_bonds":    "Un anno caldo.",
        "tone_quarrels": "Un anno di liti.",
        "tone_lean":     "Il villaggio soffrì la fame buona parte dell'anno.",
        "tone_quiet":    "Un anno tranquillo.",
        "colophon":      "*(seme: {seed} — stesso seme, stesso diario, sempre)*",
        "founders_line":  "*Fondatori: {names}.*",
        "close_header":  "## Alla chiusura",
        "close_alive":   "*{n} anime restano: {names}.*",
        "close_bonds":   "Legami ancora in piedi: {pairs}.",
        "close_no_bonds":"Nessun legame sopravvissuto.",
        "causes": {
            "starvation": "inedia",
            "old_age":    "vecchiaia",
            "misfortune": "sventura",
        },
    },
}

_NAMED_KINDS = {
    "DEATH", "BOND", "BIRTH", "ESTRANGEMENT", "RECONCILIATION",
    "MEDIATION", "TRIBUTE", "INGRATITUDE", "RESENTMENT", "ARRIVAL", "DEPARTURE",
    "COMING_OF_AGE", "ADOPTION", "TEACHING", "MEMORIAL", "FEUD",
    "ILLNESS", "RECOVERY", "JEALOUSY", "LEGACY", "DROUGHT", "DROUGHT_END", "CELEBRATION", "PACT", "VIGIL",
}
_COUNTED_KINDS = {"GIFT", "QUARREL", "REFUSAL", "REPAYMENT"}
_SKIP = {"RUMOR", "HARDSHIP", "MISFORTUNE", "HARVEST", "FESTIVAL",
         "LEAN_SEASON", "BLIGHT", "BOUNTY", "OFFENSE"}


def _named_line(t: dict, ev, world) -> str | None:
    name = lambda cid: world.chars[cid].name if cid < len(world.chars) else "?"
    causes = t.get("causes", {})
    actors = ev.actors
    if ev.kind == "BOND":
        return t["event_bond"].format(a=name(actors[0]), b=name(actors[1]))
    if ev.kind == "DEATH":
        raw = ev.data.get("cause", "starvation")
        cause = causes.get(raw, raw.replace("_", " "))
        return t["event_death"].format(a=name(actors[0]), cause=cause)
    if ev.kind == "BIRTH":
        return t["event_birth"].format(child=name(actors[0]))
    if ev.kind == "ESTRANGEMENT":
        return t["event_estrange"].format(a=name(actors[0]), b=name(actors[1]))
    if ev.kind == "RECONCILIATION":
        return t["event_reconcile"].format(a=name(actors[0]), b=name(actors[1]))
    if ev.kind == "MEDIATION":
        return t["event_mediation"].format(a=name(actors[0]), b=name(actors[1]))
    if ev.kind == "TRIBUTE":
        return t["event_tribute"].format(a=name(actors[0]), b=name(actors[1]))
    if ev.kind == "INGRATITUDE":
        return t["event_ingrat"].format(a=name(actors[0]), b=name(actors[1]))
    if ev.kind == "RESENTMENT":
        return t["event_resent"].format(a=name(actors[0]), b=name(actors[1]))
    if ev.kind == "ARRIVAL":
        return t["event_arrival"].format(a=name(actors[0]))
    if ev.kind == "DEPARTURE":
        return t["event_departure"].format(a=name(actors[0]))
    if ev.kind == "COMING_OF_AGE":
        return t["event_coming_of_age"].format(a=name(actors[0]))
    if ev.kind == "ADOPTION" and len(actors) >= 3:
        return t["event_adoption"].format(child=name(actors[0]), pa=name(actors[1]), pb=name(actors[2]))
    if ev.kind == "TEACHING" and len(actors) >= 2:
        return t["event_teaching"].format(elder=name(actors[0]), young=name(actors[1]))
    if ev.kind == "MEMORIAL" and actors:
        return t["event_memorial"].format(name=name(actors[0]))
    if ev.kind == "FEUD" and len(actors) >= 2:
        return t["event_feud"].format(a=name(actors[0]), b=name(actors[1]))
    if ev.kind == "ILLNESS" and actors:
        return t["event_illness"].format(a=name(actors[0]))
    if ev.kind == "RECOVERY" and actors:
        return t["event_recovery"].format(a=name(actors[0]))
    if ev.kind == "JEALOUSY" and len(actors) >= 3 and "event_jealousy" in t:
        return t["event_jealousy"].format(
            name=name(actors[0]), loved_one=name(actors[1]), rival=name(actors[2]))
    if ev.kind == "LEGACY" and len(actors) >= 2 and "event_legacy" in t:
        return t["event_legacy"].format(teacher=name(actors[0]), student=name(actors[1]))
    if ev.kind == "DROUGHT" and "event_drought" in t:
        return t["event_drought"]
    if ev.kind == "DROUGHT_END" and "event_drought_end" in t:
        return t["event_drought_end"]
    if ev.kind == "CELEBRATION" and "event_celebration" in t:
        return t["event_celebration"]
    if ev.kind == "PACT" and len(actors) >= 2 and "event_pact" in t:
        return t["event_pact"].format(a=name(actors[0]), b=name(actors[1]))
    if ev.kind == "VIGIL" and actors and "event_vigil" in t:
        return t["event_vigil"].format(name=name(actors[0]))
    return None


def _season_entry(t: dict, season_evs: list, world) -> str:
    """Build a compact one-line summary of a season's events."""
    parts = []

    lean = any(e.kind == "LEAN_SEASON" for e in season_evs)
    blight = any(e.kind == "BLIGHT" for e in season_evs)
    bounty = any(e.kind == "BOUNTY" for e in season_evs)

    if lean:   parts.append(t["season_lean"])
    if blight: parts.append(t["season_blight"])
    if bounty: parts.append(t["season_bounty"])

    named = []
    counts = {"GIFT": 0, "QUARREL": 0, "REFUSAL": 0, "REPAYMENT": 0}
    seen_pairs: set = set()

    for ev in season_evs:
        if ev.kind in _NAMED_KINDS:
            pair = frozenset(ev.actors[:2])
            key = (ev.kind, pair)
            if key not in seen_pairs:
                seen_pairs.add(key)
                line = _named_line(t, ev, world)
                if line:
                    named.append(line)
        elif ev.kind in _COUNTED_KINDS:
            counts[ev.kind] = counts.get(ev.kind, 0) + 1

    parts.extend(named)

    for kind, key_sg, key_pl in (
        ("GIFT", "count_gifts", "count_gifts_pl"),
        ("QUARREL", "count_quarrels", "count_quarrels_pl"),
        ("REFUSAL", "count_refusals", "count_refusals_pl"),
        ("REPAYMENT", "count_repayments", "count_repayments_pl"),
    ):
        n = counts.get(kind, 0)
        if n == 0:
            continue
        tmpl = t[key_sg] if n == 1 else t[key_pl]
        parts.append(tmpl.format(n=n) + ".")

    return " ".join(parts) if parts else ""


def yearly(world, narrator) -> str:
    lang = getattr(narrator, "lang", "en")
    t = _YT.get(lang, _YT["en"])
    village = narrator.village
    n_seasons = world.tick // TICKS_PER_SEASON
    n_years = max(1, n_seasons // 4)

    founders = [c for c in world.chars if c.joined_at == 0 and c.parent_ids is None]
    founders_line = t["founders_line"].format(names=", ".join(c.name for c in founders))

    parts = [
        f"# {t['title'].format(village=village)}",
        "",
        t["subtitle"].format(
            seed=world.seed,
            seasons=n_seasons,
            people=world.initial_people),
        founders_line,
        "",
        "---",
        "",
    ]

    evs_by_season: dict = defaultdict(list)
    for ev in world.events:
        sn = ev.tick // TICKS_PER_SEASON
        evs_by_season[sn].append(ev)

    season_names = t["season_names"]

    for yr in range(1, n_years + 1):
        first_sn = (yr - 1) * 4
        spring_tick = first_sn * TICKS_PER_SEASON

        alive_at_spring = sum(
            1 for c in world.chars
            if (c.alive or (c.died_at is not None and c.died_at >= spring_tick))
            and c.joined_at <= spring_tick
        )

        deaths_this_year = [
            ev for ev in world.events
            if ev.kind == "DEATH" and year_of(ev.tick) == yr
        ]
        death_names = [world.chars[ev.actors[0]].name for ev in deaths_this_year
                       if ev.actors[0] < len(world.chars)]

        if not deaths_this_year:
            pop_line = t["pop_no_deaths"].format(alive=alive_at_spring)
        elif len(deaths_this_year) == 1:
            pop_line = t["pop_one_death"].format(alive=alive_at_spring, names=death_names[0])
        else:
            pop_line = t["pop_deaths"].format(
                alive=alive_at_spring,
                dead=len(deaths_this_year),
                names=", ".join(death_names))

        parts.append(t["year_header"].format(n=yr))
        parts.append("")
        parts.append(pop_line)
        parts.append("")

        year_deaths = len(deaths_this_year)
        year_bonds = sum(
            1 for ev in world.events
            if ev.kind == "BOND" and year_of(ev.tick) == yr)
        year_quarrels = sum(
            1 for ev in world.events
            if ev.kind == "QUARREL" and year_of(ev.tick) == yr)
        year_lean = sum(
            1 for ev in world.events
            if ev.kind in ("LEAN_SEASON", "BLIGHT") and year_of(ev.tick) == yr)

        has_content = False
        for si in range(4):
            sn = first_sn + si
            if sn >= n_seasons:
                break
            entry = _season_entry(t, evs_by_season.get(sn, []), world)
            if entry:
                parts.append(f"*{season_names[si]}:* {entry}")
                has_content = True

        if not has_content:
            parts.append("")

        # year tone
        if year_deaths >= 2:
            tone = t["tone_deaths"]
        elif year_bonds >= 2:
            tone = t["tone_bonds"]
        elif year_quarrels >= 4:
            tone = t["tone_quarrels"]
        elif year_lean >= 2:
            tone = t["tone_lean"]
        else:
            tone = t["tone_quiet"]

        parts.append("")
        parts.append(tone)
        parts.append("")
        parts.append("---")
        parts.append("")

    # closing state
    living = [c for c in world.chars if c.alive]
    alive_names = ", ".join(c.name for c in living)
    seen_bond_ids: set = set()
    bond_pairs = []
    for c in living:
        if c.partner is not None and c.partner < len(world.chars):
            pid = c.partner
            pair_key = frozenset((c.id, pid))
            if pair_key not in seen_bond_ids and world.chars[pid].alive:
                seen_bond_ids.add(pair_key)
                bond_pairs.append(f"{c.name} & {world.chars[pid].name}")

    parts.append(t["close_header"])
    parts.append("")
    parts.append(t["close_alive"].format(n=len(living), names=alive_names))
    if bond_pairs:
        parts.append(t["close_bonds"].format(pairs=", ".join(bond_pairs)))
    else:
        parts.append(t["close_no_bonds"])
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(t["colophon"].format(seed=world.seed))
    parts.append("")
    return "\n".join(parts)
