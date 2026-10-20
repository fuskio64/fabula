"""Timeline — a visual lifespan chart for every soul who passed through the village.

`timeline(world, narrator)` returns a Markdown document with an ASCII chart:
one row per character, each bar spanning their lifespan, with event markers.

Markers: B = bonded  R = reconciled  + = child born  † = died  → = departed
"""

from .model import TICKS_PER_SEASON, year_of
from .world import CHILDHOOD_TICKS

_CHARS_PER_YEAR = 8  # bar width per simulated year

_TL = {
    "en": {
        "title":    "# Timeline of {village}",
        "subtitle": "*Seed {seed} · {n} souls · {y} year{yp}*",
        "legend":   "B bonded  R reconciled  + child born  A adopted  T taught  X died  > departed  . childhood",
        "yr":       "Yr{y}",
    },
    "es": {
        "title":    "# Cronologia de {village}",
        "subtitle": "*Semilla {seed} · {n} almas · {y} ano{yp}*",
        "legend":   "B unido/a  R reconciliado/a  + hijo/a nacido/a  A adoptado/a  T enseñado/a  X muerto/a  > partido/a  . infancia",
        "yr":       "A{y}",
    },
    "fr": {
        "title":    "# Chronologie de {village}",
        "subtitle": "*Graine {seed} · {n} ames · {y} an{yp}*",
        "legend":   "B lie  R reconcilie  + enfant ne  A adopte  T enseigne  X mort  > parti  . enfance",
        "yr":       "An{y}",
    },
    "pt": {
        "title":    "# Cronologia de {village}",
        "subtitle": "*Semente {seed} · {n} almas · {y} ano{yp}*",
        "legend":   "B ligado/a  R reconciliado/a  + filho/a nascido/a  A adotado/a  T ensinado/a  X morreu  > partiu  . infancia",
        "yr":       "A{y}",
    },
    "it": {
        "title":    "# Cronologia di {village}",
        "subtitle": "*Seme {seed} · {n} anime · {y} ann{yp}*",
        "legend":   "B legato  R riconciliato  + figlio nato  A adottato  T insegnato  X morto  > partito  . infanzia",
        "yr":       "A{y}",
    },
}


def _tick_to_col(tick: int, total: int, bar_width: int) -> int:
    return min(int(tick * bar_width / total), bar_width - 1)


def _make_bar(c, world, bar_width: int) -> str:
    total = world.tick

    start = c.born_at if c.born_at is not None else c.joined_at
    if not c.alive:
        end = c.died_at if c.died_at is not None else total
    else:
        end = total

    bar = [' '] * bar_width
    start_col = _tick_to_col(start, total, bar_width)
    end_col   = min(_tick_to_col(end, total, bar_width), bar_width - 1)

    # base lifespan — ASCII dash
    for col in range(start_col, end_col + 1):
        bar[col] = '-'

    # childhood (overrides base)
    if c.born_at is not None:
        child_end_tick = c.born_at + CHILDHOOD_TICKS
        child_end_col = _tick_to_col(min(child_end_tick, end), total, bar_width)
        for col in range(start_col, child_end_col + 1):
            bar[col] = '.'

    # event markers — lower number = higher priority (wins ties)
    PRIORITY = {'X': 0, '>': 1, 'B': 2, 'R': 3, '+': 4, 'A': 5, 'T': 6}
    marks: dict[int, str] = {}

    def place(tick: int, ch: str) -> None:
        col = _tick_to_col(tick, total, bar_width)
        if 0 <= col < bar_width:
            if ch not in PRIORITY or PRIORITY.get(marks.get(col, ch), 9) >= PRIORITY[ch]:
                marks[col] = ch

    for ev in world.events:
        if ev.kind == 'DEATH' and ev.actors and ev.actors[0] == c.id:
            place(ev.tick, 'X')
        elif ev.kind == 'DEPARTURE' and ev.actors and ev.actors[0] == c.id:
            place(ev.tick, '>')
        elif ev.kind == 'BOND' and c.id in ev.actors[:2]:
            place(ev.tick, 'B')
        elif ev.kind == 'RECONCILIATION' and c.id in ev.actors[:2]:
            place(ev.tick, 'R')
        elif ev.kind == 'BIRTH' and len(ev.actors) >= 3 and c.id in ev.actors[1:3]:
            place(ev.tick, '+')
        elif ev.kind == 'ADOPTION' and len(ev.actors) >= 3 and c.id == ev.actors[0]:
            place(ev.tick, 'A')
        elif ev.kind == 'TEACHING' and len(ev.actors) >= 2 and c.id == ev.actors[1]:
            place(ev.tick, 'T')

    for col, ch in marks.items():
        bar[col] = ch

    return ''.join(bar)


def timeline(world, narrator) -> str:
    lang = getattr(narrator, 'lang', 'en')
    t = _TL.get(lang, _TL['en'])
    village = narrator.village

    total = world.tick
    n_years = max(1, year_of(total - 1))
    bar_width = min(60, n_years * _CHARS_PER_YEAR)

    # sort: founders first (joined_at==0, no parent_ids), then arrivals by tick, then born-in by tick
    def sort_key(c):
        if c.parent_ids is None and c.joined_at == 0:
            return (0, 0, c.id)           # founder
        if c.born_at is not None:
            return (2, c.born_at, c.id)   # born in village
        return (1, c.joined_at, c.id)     # arrived

    chars = sorted(world.chars, key=sort_key)
    name_w = max((len(c.name) for c in chars), default=8) + 2

    # Italian plural suffix: anno/anni
    if lang == 'it':
        yp = 'i' if n_years != 1 else 'o'
    else:
        yp = '' if n_years == 1 else 's'

    parts = [
        t['title'].format(village=village),
        '',
        t['subtitle'].format(seed=world.seed, n=len(chars), y=n_years, yp=yp),
        '',
    ]

    # year header line
    yr_fmt = t.get('yr', 'Yr{y}')
    gap = ' ' * name_w
    header = gap
    for yr in range(1, n_years + 1):
        label = yr_fmt.format(y=yr)
        pad_l = (_CHARS_PER_YEAR - len(label)) // 2
        pad_r = _CHARS_PER_YEAR - len(label) - pad_l
        header += ' ' * pad_l + label + ' ' * pad_r
    parts.append(header)

    # separator
    sep = ' ' * name_w
    for yr in range(1, n_years + 1):
        sep += '|' + '-' * (_CHARS_PER_YEAR - 1)
    sep += '|'
    parts.append(sep)

    # character rows
    for c in chars:
        bar = _make_bar(c, world, bar_width)
        parts.append(c.name.ljust(name_w) + bar)

    parts.append('')
    parts.append(t['legend'])
    parts.append('')
    return '\n'.join(parts)
