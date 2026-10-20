"""Stats — a simulation metrics dashboard for a village run.

`stats(world, narrator)` returns a Markdown document with key metrics:
population arc, mortality, social fabric, exchange, and an ASCII
year-by-year activity chart.
"""

from collections import Counter, defaultdict

from .model import TICKS_PER_SEASON, year_of


_ST = {
    "en": {
        "title":       "# Stats — {village}",
        "subtitle":    "*Seed {seed} · {days} days · {years} year{yp} · {founders} founders*",
        "pop_header":  "## Population",
        "pop_line":    "Started: {start}   Peak: {peak} (yr {peak_yr})   Closed: {close}",
        "pop_flow":    "Born in village: {born}   Arrived: {arrived}   Departed: {departed}",
        "mort_header": "## Mortality",
        "mort_none":   "No deaths recorded.",
        "mort_deaths": "Deaths: {n} total — {causes}",
        "mort_hard":   "Hardest year: {yr} ({n} deaths)",
        "lifespan":    "Avg death age: {avg_y}y {avg_s}s   Oldest ever: {name} ({y}y {s}s)",
        "soc_header":  "## Social fabric",
        "soc_bonds":   "Bonds: {formed} formed, {standing} standing",
        "soc_estrange":"Estrangements: {n}",
        "soc_recon":   "Reconciliations: {n}",
        "soc_adopt":   "Adoptions: {n}",
        "soc_teach":   "Teachings: {n}",
        "soc_mediate": "Mediations: {n}",
        "soc_feud":    "Feuds: {n}",
        "soc_jealousy":"Jealousy events: {n}",
        "soc_legacy":  "Legacies passed: {n}",
        "soc_drought": "Droughts: {n}",
        "soc_drought_end": "Drought recoveries: {n}",
        "soc_celebration": "Celebrations: {n}",
        "soc_pact":    "Pacts: {n}",
        "soc_vigil":   "Vigils: {n}",
        "exc_header":  "## Exchange",
        "exc_line":    "Gifts: {gifts}   Quarrels: {quarrels}   Refusals: {refusals}   Debts repaid: {repaid}",
        "exc_line2":   "Ingratitude: {ingrat}   Resentments: {resent}   Tributes: {tribute}",
        "act_header":  "## Activity by year",
        "act_year":    "Yr {y}",
        "causes": {
            "starvation": "starvation",
            "old_age":    "old age",
            "misfortune": "misfortune",
        },
    },
    "es": {
        "title":       "# Estadísticas — {village}",
        "subtitle":    "*Semilla {seed} · {days} días · {years} año{yp} · {founders} fundadores*",
        "pop_header":  "## Población",
        "pop_line":    "Inicio: {start}   Pico: {peak} (a. {peak_yr})   Cierre: {close}",
        "pop_flow":    "Nacidos: {born}   Llegados: {arrived}   Partidos: {departed}",
        "mort_header": "## Mortalidad",
        "mort_none":   "Sin muertes registradas.",
        "mort_deaths": "Muertes: {n} en total — {causes}",
        "mort_hard":   "Año más duro: {yr} ({n} muertes)",
        "lifespan":    "Edad media de muerte: {avg_y}a {avg_s}e   El más longevo: {name} ({y}a {s}e)",
        "soc_header":  "## Tejido social",
        "soc_bonds":   "Vínculos: {formed} formados, {standing} en pie",
        "soc_estrange":"Distanciamientos: {n}",
        "soc_recon":   "Reconciliaciones: {n}",
        "soc_adopt":   "Adopciones: {n}",
        "soc_teach":   "Enseñanzas: {n}",
        "soc_mediate": "Mediaciones: {n}",
        "soc_feud":    "Enemistades: {n}",
        "soc_jealousy":"Celos: {n}",
        "soc_legacy":  "Legados transmitidos: {n}",
        "soc_drought": "Sequías: {n}",
        "soc_drought_end": "Sequías superadas: {n}",
        "soc_celebration": "Celebraciones: {n}",
        "soc_pact":    "Pactos: {n}",
        "soc_vigil":   "Vigilias: {n}",
        "exc_header":  "## Intercambio",
        "exc_line":    "Regalos: {gifts}   Peleas: {quarrels}   Negativas: {refusals}   Deudas saldadas: {repaid}",
        "exc_line2":   "Ingratitud: {ingrat}   Rencores: {resent}   Tributos: {tribute}",
        "act_header":  "## Actividad por año",
        "act_year":    "A. {y}",
        "causes": {
            "starvation": "hambre",
            "old_age":    "vejez",
            "misfortune": "desgracia",
        },
    },
    "fr": {
        "title":       "# Statistiques — {village}",
        "subtitle":    "*Graine {seed} · {days} jours · {years} an{yp} · {founders} fondateurs*",
        "pop_header":  "## Population",
        "pop_line":    "Debut: {start}   Pic: {peak} (an {peak_yr})   Cloture: {close}",
        "pop_flow":    "Nes au village: {born}   Arrives: {arrived}   Partis: {departed}",
        "mort_header": "## Mortalite",
        "mort_none":   "Aucun deces enregistre.",
        "mort_deaths": "Deces: {n} au total — {causes}",
        "mort_hard":   "Annee la plus dure: {yr} ({n} deces)",
        "lifespan":    "Age moyen au deces: {avg_y}a {avg_s}s   Le plus age: {name} ({y}a {s}s)",
        "soc_header":  "## Tissu social",
        "soc_bonds":   "Liens: {formed} formes, {standing} debout",
        "soc_estrange":"Brouilles: {n}",
        "soc_recon":   "Reconciliations: {n}",
        "soc_adopt":   "Adoptions: {n}",
        "soc_teach":   "Enseignements: {n}",
        "soc_mediate": "Mediations: {n}",
        "soc_feud":    "Querelles: {n}",
        "soc_jealousy":"Jalousies: {n}",
        "soc_legacy":  "Heritages transmis: {n}",
        "soc_drought": "Secheresses: {n}",
        "soc_drought_end": "Secheresses surmontees: {n}",
        "soc_celebration": "Celebrations: {n}",
        "soc_pact":    "Pactes: {n}",
        "soc_vigil":   "Veilles: {n}",
        "exc_header":  "## Echanges",
        "exc_line":    "Dons: {gifts}   Querelles: {quarrels}   Refus: {refusals}   Dettes remboursees: {repaid}",
        "exc_line2":   "Ingratitude: {ingrat}   Rancunes: {resent}   Tributs: {tribute}",
        "act_header":  "## Activite par an",
        "act_year":    "An {y}",
        "causes": {
            "starvation": "famine",
            "old_age":    "vieillesse",
            "misfortune": "malheur",
        },
    },
    "pt": {
        "title":       "# Estatísticas — {village}",
        "subtitle":    "*Semente {seed} · {days} dias · {years} ano{yp} · {founders} fundadores*",
        "pop_header":  "## População",
        "pop_line":    "Início: {start}   Pico: {peak} (a. {peak_yr})   Fecho: {close}",
        "pop_flow":    "Nascidos: {born}   Chegados: {arrived}   Partidos: {departed}",
        "mort_header": "## Mortalidade",
        "mort_none":   "Sem mortes registadas.",
        "mort_deaths": "Mortes: {n} no total — {causes}",
        "mort_hard":   "Ano mais duro: {yr} ({n} mortes)",
        "lifespan":    "Idade média à morte: {avg_y}a {avg_s}e   O mais velho: {name} ({y}a {s}e)",
        "soc_header":  "## Tecido social",
        "soc_bonds":   "Vínculos: {formed} formados, {standing} em pé",
        "soc_estrange":"Afastamentos: {n}",
        "soc_recon":   "Reconciliações: {n}",
        "soc_adopt":   "Adoções: {n}",
        "soc_teach":   "Ensinamentos: {n}",
        "soc_mediate": "Mediações: {n}",
        "soc_feud":    "Inimizades: {n}",
        "soc_jealousy":"Ciúmes: {n}",
        "soc_legacy":  "Legados transmitidos: {n}",
        "soc_drought": "Secas: {n}",
        "soc_drought_end": "Secas superadas: {n}",
        "soc_celebration": "Celebrações: {n}",
        "soc_pact":    "Pactos: {n}",
        "soc_vigil":   "Vigílias: {n}",
        "exc_header":  "## Trocas",
        "exc_line":    "Dádivas: {gifts}   Disputas: {quarrels}   Recusas: {refusals}   Dívidas saldadas: {repaid}",
        "exc_line2":   "Ingratidão: {ingrat}   Rancores: {resent}   Tributos: {tribute}",
        "act_header":  "## Atividade por ano",
        "act_year":    "A. {y}",
        "causes": {
            "starvation": "fome",
            "old_age":    "velhice",
            "misfortune": "desgraça",
        },
    },
    "it": {
        "title":       "# Statistiche — {village}",
        "subtitle":    "*Seme {seed} · {days} giorni · {years} ann{yp} · {founders} fondatori*",
        "pop_header":  "## Popolazione",
        "pop_line":    "Inizio: {start}   Picco: {peak} (a. {peak_yr})   Chiusura: {close}",
        "pop_flow":    "Nati al villaggio: {born}   Arrivati: {arrived}   Partiti: {departed}",
        "mort_header": "## Mortalita",
        "mort_none":   "Nessun decesso registrato.",
        "mort_deaths": "Decessi: {n} in totale — {causes}",
        "mort_hard":   "Anno piu duro: {yr} ({n} decessi)",
        "lifespan":    "Eta media al decesso: {avg_y}a {avg_s}s   Il piu anziano: {name} ({y}a {s}s)",
        "soc_header":  "## Tessuto sociale",
        "soc_bonds":   "Legami: {formed} formati, {standing} in piedi",
        "soc_estrange":"Allontanamenti: {n}",
        "soc_recon":   "Riconciliazioni: {n}",
        "soc_adopt":   "Adozioni: {n}",
        "soc_teach":   "Insegnamenti: {n}",
        "soc_mediate": "Mediazioni: {n}",
        "soc_feud":    "Faide: {n}",
        "soc_jealousy":"Gelosie: {n}",
        "soc_legacy":  "Eredita trasmesse: {n}",
        "soc_drought": "Siccita: {n}",
        "soc_drought_end": "Siccita superate: {n}",
        "soc_celebration": "Celebrazioni: {n}",
        "soc_pact":    "Patti: {n}",
        "soc_vigil":   "Veglie: {n}",
        "exc_header":  "## Scambi",
        "exc_line":    "Doni: {gifts}   Liti: {quarrels}   Rifiuti: {refusals}   Debiti saldati: {repaid}",
        "exc_line2":   "Ingratitudine: {ingrat}   Risentimenti: {resent}   Tributi: {tribute}",
        "act_header":  "## Attivita per anno",
        "act_year":    "A. {y}",
        "causes": {
            "starvation": "inedia",
            "old_age":    "vecchiaia",
            "misfortune": "sventura",
        },
    },
}

_BAR_WIDTH = 28
_SKIP_IN_ACTIVITY = {"RUMOR"}


def _ticks_to_ys(ticks: int) -> tuple[int, int]:
    seasons = ticks // TICKS_PER_SEASON
    return seasons // 4, seasons % 4


def stats(world, narrator) -> str:
    lang = getattr(narrator, "lang", "en")
    t = _ST.get(lang, _ST["en"])
    village = narrator.village
    w = world

    n_years = max(1, year_of(w.tick - 1)) if w.tick > 0 else 1
    days = w.tick
    if lang == "it":
        yp = "i" if n_years != 1 else "o"
    else:
        yp = "" if n_years == 1 else "s"

    founders = [c for c in w.chars if c.joined_at == 0 and c.parent_ids is None]
    arrivals = [c for c in w.chars if c.born_at is None and c.joined_at > 0]
    born_in  = [c for c in w.chars if c.born_at is not None]
    departed = sum(1 for ev in w.events if ev.kind == "DEPARTURE")

    # population arc
    pop_by_year: dict[int, int] = {}
    for yr in range(1, n_years + 2):
        tick_start = (yr - 1) * 4 * TICKS_PER_SEASON
        alive_at = sum(
            1 for c in w.chars
            if (c.born_at if c.born_at is not None else c.joined_at) <= tick_start
            and (c.died_at if c.died_at is not None else w.tick) > tick_start
        )
        pop_by_year[yr] = alive_at

    start_pop = w.initial_people
    close_pop = sum(1 for c in w.chars if c.alive)
    peak_yr   = max(pop_by_year, key=lambda y: pop_by_year[y])
    peak_pop  = pop_by_year[peak_yr]

    # mortality
    deaths = [ev for ev in w.events if ev.kind == "DEATH"]
    deaths_by_year: Counter = Counter(year_of(ev.tick) for ev in deaths)
    cause_tally: Counter = Counter(
        ev.data.get("cause", "misfortune") for ev in deaths
    )
    causes_str = ", ".join(
        f"{t['causes'].get(k, k)} {v}"
        for k, v in sorted(cause_tally.items(), key=lambda x: -x[1])
    )
    hardest_yr = deaths_by_year.most_common(1)[0] if deaths_by_year else None

    # lifespan for deceased
    dead_chars = [c for c in w.chars if not c.alive and c.died_at is not None]
    avg_death_ticks = (
        sum(c.died_at - (c.born_at if c.born_at is not None else c.joined_at)
            for c in dead_chars) / len(dead_chars)
        if dead_chars else 0
    )
    avg_y, avg_s = _ticks_to_ys(int(avg_death_ticks))

    # oldest person (living or dead — whoever lived longest)
    def lifespan_ticks(c):
        start = c.born_at if c.born_at is not None else c.joined_at
        end   = c.died_at if c.died_at is not None else w.tick
        return end - start

    oldest = max(w.chars, key=lifespan_ticks) if w.chars else None
    if oldest:
        oy, os_ = _ticks_to_ys(lifespan_ticks(oldest))
    else:
        oy, os_ = 0, 0

    # event counts
    ec = Counter(ev.kind for ev in w.events)
    bonds_standing = sum(
        1 for c in w.chars
        if c.alive and c.partner is not None and c.partner < len(w.chars)
           and w.chars[c.partner].alive
    ) // 2

    # activity by year (all events minus RUMOR)
    act_by_year: Counter = Counter()
    for ev in w.events:
        if ev.kind not in _SKIP_IN_ACTIVITY:
            act_by_year[year_of(ev.tick)] += 1

    max_act = max(act_by_year.values()) if act_by_year else 1

    # build output
    parts = [
        t["title"].format(village=village),
        "",
        t["subtitle"].format(
            seed=w.seed, days=days, years=n_years, yp=yp,
            founders=len(founders)),
        "",
        t["pop_header"],
        "",
        t["pop_line"].format(start=start_pop, peak=peak_pop,
                             peak_yr=peak_yr, close=close_pop),
        t["pop_flow"].format(born=len(born_in), arrived=len(arrivals),
                             departed=departed),
        "",
        t["mort_header"],
        "",
    ]

    if not deaths:
        parts.append(t["mort_none"])
    else:
        parts.append(t["mort_deaths"].format(n=len(deaths), causes=causes_str))
        if hardest_yr:
            parts.append(t["mort_hard"].format(yr=hardest_yr[0], n=hardest_yr[1]))
        if dead_chars:
            parts.append(t["lifespan"].format(
                avg_y=avg_y, avg_s=avg_s,
                name=oldest.name if oldest else "?", y=oy, s=os_))

    parts += [
        "",
        t["soc_header"],
        "",
        t["soc_bonds"].format(formed=ec.get("BOND", 0), standing=bonds_standing),
        t["soc_estrange"].format(n=ec.get("ESTRANGEMENT", 0)),
        t["soc_recon"].format(n=ec.get("RECONCILIATION", 0)),
        t["soc_adopt"].format(n=ec.get("ADOPTION", 0)),
        t["soc_teach"].format(n=ec.get("TEACHING", 0)),
        t["soc_mediate"].format(n=ec.get("MEDIATION", 0)),
        t["soc_feud"].format(n=ec.get("FEUD", 0)),
        t["soc_jealousy"].format(n=ec.get("JEALOUSY", 0)),
        t["soc_legacy"].format(n=ec.get("LEGACY", 0)),
        t["soc_drought"].format(n=ec.get("DROUGHT", 0)),
        t["soc_drought_end"].format(n=ec.get("DROUGHT_END", 0)),
        t["soc_celebration"].format(n=ec.get("CELEBRATION", 0)),
        t["soc_pact"].format(n=ec.get("PACT", 0)),
        t["soc_vigil"].format(n=ec.get("VIGIL", 0)),
        "",
        t["exc_header"],
        "",
        t["exc_line"].format(
            gifts=ec.get("GIFT", 0),
            quarrels=ec.get("QUARREL", 0),
            refusals=ec.get("REFUSAL", 0),
            repaid=ec.get("REPAYMENT", 0)),
        t["exc_line2"].format(
            ingrat=ec.get("INGRATITUDE", 0),
            resent=ec.get("RESENTMENT", 0),
            tribute=ec.get("TRIBUTE", 0)),
        "",
        t["act_header"],
        "",
    ]

    yr_label_w = max(len(t["act_year"].format(y=n_years)), 4)
    for yr in range(1, n_years + 1):
        n_ev = act_by_year.get(yr, 0)
        bar_len = int(n_ev * _BAR_WIDTH / max_act)
        bar = "=" * bar_len + " " * (_BAR_WIDTH - bar_len)
        label = t["act_year"].format(y=yr).ljust(yr_label_w)
        parts.append(f"{label}  [{bar}] {n_ev}")

    parts.append("")
    return "\n".join(parts)
