"""Cast of characters — a compact registry of all souls who passed through the village.

`cast(world, narrator)` returns a Markdown document listing every character with
their origin, fate, relationships, and key family links. Supports all five languages.
"""

from .model import TICKS_PER_SEASON, year_of


_CT = {
    "en": {
        "title":        "# The Register of {village}",
        "subtitle":     "*World seed {seed} · {n} souls recorded*",
        "section_living": "## Living at the close",
        "section_dead":   "## Died in this record",
        "section_gone":   "## Departed",
        "status_elder":   "elder",
        "status_child":   "child",
        "origin_founder": "founder",
        "origin_born":    "born in {village}",
        "origin_stranger":"arrived year {year}",
        "died_cause":     "died year {year} ({cause})",
        "departed_year":  "left year {year}",
        "bonded_with":    "bonded with {name}",
        "widowed":        "widowed ({name})",
        "parent_of":      "parent of {names}",
        "sibling_of":     "sibling of {names}",
        "adopted_by":     "adopted by {pa} & {pb}",
        "causes": {
            "starvation": "starvation",
            "old_age":    "old age",
            "misfortune": "misfortune",
        },
        "colophon": "*(world seed {seed})*",
    },
    "es": {
        "title":        "# El registro de {village}",
        "subtitle":     "*Semilla: {seed} · {n} almas registradas*",
        "section_living": "## Vivos al cierre",
        "section_dead":   "## Fallecidos en este registro",
        "section_gone":   "## Partidos",
        "status_elder":   "anciano/a",
        "status_child":   "niño/a",
        "origin_founder": "fundador/a",
        "origin_born":    "nacido/a en {village}",
        "origin_stranger":"llegó el año {year}",
        "died_cause":     "murió el año {year} ({cause})",
        "departed_year":  "partió el año {year}",
        "bonded_with":    "unido/a a {name}",
        "widowed":        "viudo/a ({name})",
        "parent_of":      "padre/madre de {names}",
        "sibling_of":     "hermano/a de {names}",
        "adopted_by":     "adoptado/a por {pa} y {pb}",
        "causes": {
            "starvation": "hambre",
            "old_age":    "vejez",
            "misfortune": "desgracia",
        },
        "colophon": "*(semilla: {seed})*",
    },
    "fr": {
        "title":        "# Le registre de {village}",
        "subtitle":     "*Graine : {seed} · {n} âmes enregistrées*",
        "section_living": "## Vivants à la clôture",
        "section_dead":   "## Décédés dans ce registre",
        "section_gone":   "## Partis",
        "status_elder":   "ancien",
        "status_child":   "enfant",
        "origin_founder": "fondateur",
        "origin_born":    "né à {village}",
        "origin_stranger":"arrivé l'an {year}",
        "died_cause":     "mort l'an {year} ({cause})",
        "departed_year":  "parti l'an {year}",
        "bonded_with":    "lié à {name}",
        "widowed":        "veuf/veuve ({name})",
        "parent_of":      "parent de {names}",
        "sibling_of":     "frère/sœur de {names}",
        "adopted_by":     "adopté par {pa} et {pb}",
        "causes": {
            "starvation": "famine",
            "old_age":    "vieillesse",
            "misfortune": "malheur",
        },
        "colophon": "*(graine : {seed})*",
    },
    "pt": {
        "title":        "# O registo de {village}",
        "subtitle":     "*Semente: {seed} · {n} almas registadas*",
        "section_living": "## Vivos no fecho",
        "section_dead":   "## Falecidos neste registo",
        "section_gone":   "## Partidos",
        "status_elder":   "ancião/ã",
        "status_child":   "criança",
        "origin_founder": "fundador/a",
        "origin_born":    "nascido/a em {village}",
        "origin_stranger":"chegou no ano {year}",
        "died_cause":     "morreu no ano {year} ({cause})",
        "departed_year":  "partiu no ano {year}",
        "bonded_with":    "ligado/a a {name}",
        "widowed":        "viúvo/a ({name})",
        "parent_of":      "pai/mãe de {names}",
        "sibling_of":     "irmão/ã de {names}",
        "adopted_by":     "adotado/a por {pa} e {pb}",
        "causes": {
            "starvation": "fome",
            "old_age":    "velhice",
            "misfortune": "desgraça",
        },
        "colophon": "*(semente: {seed})*",
    },
    "it": {
        "title":        "# Il registro di {village}",
        "subtitle":     "*Seme: {seed} · {n} anime registrate*",
        "section_living": "## Viventi alla chiusura",
        "section_dead":   "## Morti in questo registro",
        "section_gone":   "## Partiti",
        "status_elder":   "anziano/a",
        "status_child":   "bambino/a",
        "origin_founder": "fondatore/trice",
        "origin_born":    "nato/a a {village}",
        "origin_stranger":"arrivò l'anno {year}",
        "died_cause":     "morì l'anno {year} ({cause})",
        "departed_year":  "partì l'anno {year}",
        "bonded_with":    "legato/a a {name}",
        "widowed":        "vedovo/a ({name})",
        "parent_of":      "genitore di {names}",
        "sibling_of":     "fratello/sorella di {names}",
        "adopted_by":     "adottato/a da {pa} e {pb}",
        "causes": {
            "starvation": "inedia",
            "old_age":    "vecchiaia",
            "misfortune": "sventura",
        },
        "colophon": "*(seme: {seed})*",
    },
}


def _char_line(t: dict, c, world, village: str) -> str:
    tags = []

    # detect adoption: was an ADOPTION event filed for this character?
    adoption_ev = next(
        (ev for ev in world.events if ev.kind == "ADOPTION" and ev.actors and ev.actors[0] == c.id),
        None)

    # origin
    if c.parent_ids:
        bio_parents = [world.chars[pid].name for pid in c.parent_ids
                       if pid < len(world.chars)]
        origin = t["origin_born"].format(village=village)
        if bio_parents and not adoption_ev:
            origin += f" ({' & '.join(bio_parents)})"
        tags.append(origin)
        # adoption tag
        if adoption_ev and len(adoption_ev.actors) >= 3 and "adopted_by" in t:
            pa = world.chars[adoption_ev.actors[1]].name if adoption_ev.actors[1] < len(world.chars) else "?"
            pb = world.chars[adoption_ev.actors[2]].name if adoption_ev.actors[2] < len(world.chars) else "?"
            tags.append(t["adopted_by"].format(pa=pa, pb=pb))
    elif c.joined_at == 0:
        tags.append(t["origin_founder"])
    else:
        yr = year_of(c.joined_at)
        tags.append(t["origin_stranger"].format(year=yr))

    # status qualifiers
    if c.elder:
        tags.append(t["status_elder"])
    elif c.childhood:
        tags.append(t["status_child"])

    # fate
    if not c.alive:
        if c.departed:
            yr = year_of(c.died_at) if c.died_at is not None else "?"
            tags.append(t["departed_year"].format(year=yr))
        else:
            yr = year_of(c.died_at) if c.died_at is not None else "?"
            death_evs = [ev for ev in world.events
                         if ev.kind == "DEATH" and ev.actors and ev.actors[0] == c.id]
            cause_raw = death_evs[0].data.get("cause", "misfortune") if death_evs else "misfortune"
            cause = t["causes"].get(cause_raw, cause_raw.replace("_", " "))
            tags.append(t["died_cause"].format(year=yr, cause=cause))

    # bond
    if c.partner is not None and c.partner < len(world.chars):
        partner = world.chars[c.partner]
        if partner.alive:
            tags.append(t["bonded_with"].format(name=partner.name))
        else:
            tags.append(t["widowed"].format(name=partner.name))
    else:
        # check if widowed (partner died, partner field cleared)
        widowing = next((ev for ev in world.events
                         if ev.kind == "WIDOWING" and ev.actors and ev.actors[0] == c.id), None)
        if widowing and widowing.actors[1] < len(world.chars):
            deceased = world.chars[widowing.actors[1]]
            tags.append(t["widowed"].format(name=deceased.name))

    # children
    children = [ch for ch in world.chars if ch.parent_ids and c.id in ch.parent_ids]
    if children:
        tags.append(t["parent_of"].format(names=", ".join(ch.name for ch in children)))

    # siblings (only list if not too many)
    if c.parent_ids:
        siblings = [ch for ch in world.chars
                    if ch.id != c.id and ch.parent_ids and set(ch.parent_ids) == set(c.parent_ids)]
        if siblings:
            tags.append(t["sibling_of"].format(names=", ".join(s.name for s in siblings)))

    return f"**{c.name}** — {'; '.join(tags)}."


def cast(world, narrator) -> str:
    lang = getattr(narrator, "lang", "en")
    t = _CT.get(lang, _CT["en"])
    village = narrator.village

    chars = list(world.chars)

    parts = [
        t["title"].format(village=village),
        "",
        t["subtitle"].format(seed=world.seed, n=len(chars)),
        "",
    ]

    living = [c for c in chars if c.alive]
    dead = [c for c in chars if not c.alive and not c.departed]
    departed = [c for c in chars if c.departed]

    if living:
        parts.append(t["section_living"])
        parts.append("")
        for c in living:
            parts.append(_char_line(t, c, world, village))
        parts.append("")

    if dead:
        parts.append(t["section_dead"])
        parts.append("")
        for c in sorted(dead, key=lambda c: c.died_at or 0):
            parts.append(_char_line(t, c, world, village))
        parts.append("")

    if departed:
        parts.append(t["section_gone"])
        parts.append("")
        for c in departed:
            parts.append(_char_line(t, c, world, village))
        parts.append("")

    parts.append(t["colophon"].format(seed=world.seed))
    parts.append("")
    return "\n".join(parts)
