"""Relationship graph: the village's social web rendered as self-contained HTML.

`relationship_graph(world, narrator)` returns an HTML string you can save
and open in any browser. No external dependencies; the layout is computed
deterministically from the world seed so the same run always produces the
same graph.

Click a node to highlight that character's connections; click again to reset.
"""

import math


def _layout(chars, affinities, width: int, height: int,
            iterations: int = 320) -> dict:
    """Fruchterman-Reingold force-directed layout. Returns {char_id: (x, y)}."""
    n = len(chars)
    if n == 0:
        return {}
    if n == 1:
        return {chars[0].id: (width / 2, height / 2)}

    # initialise on a circle
    ids = [c.id for c in chars]
    pos = {
        cid: (
            width / 2 + (min(width, height) * 0.37) * math.cos(2 * math.pi * i / n),
            height / 2 + (min(width, height) * 0.37) * math.sin(2 * math.pi * i / n),
        )
        for i, cid in enumerate(ids)
    }

    pad = 55  # keep nodes away from the svg edges
    area = (width - 2 * pad) * (height - 2 * pad)
    k = math.sqrt(area / n)  # optimal inter-node distance

    for step in range(iterations):
        t = max(2.0, (width / 8) * (1 - step / iterations) ** 1.6)
        disp = {cid: [0.0, 0.0] for cid in ids}

        # repulsion between every pair
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                dx = pos[a][0] - pos[b][0]
                dy = pos[a][1] - pos[b][1]
                d = math.sqrt(dx * dx + dy * dy) or 0.01
                f = k * k / d
                disp[a][0] += dx / d * f
                disp[a][1] += dy / d * f
                disp[b][0] -= dx / d * f
                disp[b][1] -= dy / d * f

        # attraction for significant relationships
        for (ai, bi), aff in affinities.items():
            if abs(aff) < 0.08:
                continue
            dx = pos[bi][0] - pos[ai][0]
            dy = pos[bi][1] - pos[ai][1]
            d = math.sqrt(dx * dx + dy * dy) or 0.01
            f = d * d / k * (0.4 + 0.9 * abs(aff))
            # warm pairs attract more; cold pairs repel less (natural social clusters)
            sign = 1.0 if aff > 0 else -0.3
            disp[ai][0] += sign * dx / d * f
            disp[ai][1] += sign * dy / d * f
            disp[bi][0] -= sign * dx / d * f
            disp[bi][1] -= sign * dy / d * f

        # apply displacement with temperature cap
        for cid in ids:
            dx, dy = disp[cid]
            d = math.sqrt(dx * dx + dy * dy) or 1.0
            scale = min(d, t) / d
            x = max(pad, min(width - pad, pos[cid][0] + dx * scale))
            y = max(pad, min(height - pad, pos[cid][1] + dy * scale))
            pos[cid] = (x, y)

    return pos


def _edge_style(aff: float, is_bond: bool):
    if is_bond:
        return "#c8a020", 5.5, 0.92
    a = abs(aff)
    w = 1.2 + 3.2 * min(1.0, a)
    if aff > 0:
        r = int(180 + 55 * min(1.0, aff * 1.5))
        g = int(90 * max(0.0, 1.0 - aff))
        b = 18
        opacity = 0.35 + 0.55 * min(1.0, a)
    else:
        r, g = 18, int(50 * max(0.0, 1.0 + aff * 2))
        b = int(180 + 55 * min(1.0, -aff * 1.5))
        opacity = 0.30 + 0.55 * min(1.0, a)
    return f"#{r:02x}{g:02x}{b:02x}", round(w, 2), round(opacity, 3)


def _node_attrs(char):
    if not char.alive:
        return "#3a4a5a", "#5a6a7a", 1.5, 22, 0.52
    if char.childhood:
        return "#4a85b8", "#7ab0d8", 1.5, 15, 1.0
    if char.elder:
        return "#3a6fa8", "#c8a020", 3.0, 24, 1.0
    return "#3a6fa8", "#6a9fd8", 2.0, 22, 1.0


def _tooltip(char, narrator):
    adjs = narrator.adjectives(char)
    status = "dead" if not char.alive else ("elder" if char.elder else ("child" if char.childhood else ""))
    parts = [char.name]
    if adjs:
        parts.append(", ".join(adjs))
    if status:
        parts.append(f"({status})")
    return " · ".join(parts)


_JS = """
(function () {
  var nodes = document.querySelectorAll('.vnode');
  var edges = document.querySelectorAll('.vedge');
  var selected = null;

  nodes.forEach(function (node) {
    node.style.cursor = 'pointer';
    node.addEventListener('click', function () {
      var id = node.dataset.id;
      if (selected === id) {
        selected = null;
        nodes.forEach(function (n) { n.style.opacity = '1'; });
        edges.forEach(function (e) { e.style.opacity = ''; });
        return;
      }
      selected = id;
      nodes.forEach(function (n) {
        n.style.opacity = (n.dataset.id === id) ? '1' : '0.18';
      });
      edges.forEach(function (e) {
        var connected = (e.dataset.a === id || e.dataset.b === id);
        e.style.opacity = connected ? '1' : '0.04';
        if (connected) {
          var other = (e.dataset.a === id) ? e.dataset.b : e.dataset.a;
          document.querySelectorAll('.vnode[data-id="' + other + '"]').forEach(function (n) {
            n.style.opacity = '1';
          });
        }
      });
    });
  });
})();
"""


def relationship_graph(world, narrator) -> str:
    """Return a self-contained HTML relationship graph for this world."""
    from .model import TICKS_PER_SEASON, season_index, year_of

    W, H = 820, 580
    chars = world.chars  # all characters, including dead

    # Build symmetric affinity map: (min_id, max_id) -> mean affinity
    aff_map: dict = {}
    bonds: set = set()
    for ev in world.events:
        if ev.kind == "BOND":
            a, b = ev.actors[0], ev.actors[1]
            bonds.add((min(a, b), max(a, b)))
    for a in chars:
        for b in chars:
            if b.id <= a.id:
                continue
            mutual = (a.feel(b.id) + b.feel(a.id)) / 2
            if abs(mutual) >= 0.12:
                aff_map[(a.id, b.id)] = mutual

    # Layout
    pos = _layout(chars, aff_map, W, H)

    # SVG elements
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" style="display:block;margin:0 auto">',
        f'<rect width="{W}" height="{H}" rx="10" fill="#111827"/>',
    ]

    # Edges (drawn before nodes)
    for (ai, bi), aff in sorted(aff_map.items(), key=lambda x: abs(x[1])):
        if ai not in pos or bi not in pos:
            continue
        is_bond = (ai, bi) in bonds
        color, width, opacity = _edge_style(aff, is_bond)
        x1, y1 = pos[ai]
        x2, y2 = pos[bi]
        svg_lines.append(
            f'<line class="vedge" data-a="{ai}" data-b="{bi}" '
            f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{width}" opacity="{opacity}" '
            f'stroke-linecap="round"/>'
        )

    # Nodes
    for char in chars:
        if char.id not in pos:
            continue
        cx, cy = pos[char.id]
        fill, stroke, sw, r, op = _node_attrs(char)
        tip = _tooltip(char, narrator)
        dagger = " †" if not char.alive else ""
        label = char.name + dagger

        svg_lines.append(
            f'<g class="vnode" data-id="{char.id}" opacity="{op}">'
            f'<title>{tip}</title>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
            f'<text x="{cx:.1f}" y="{cy + r + 13:.1f}" '
            f'font-family="Georgia,serif" font-size="11" '
            f'fill="#c8d8e8" text-anchor="middle">{label}</text>'
            f'</g>'
        )

    svg_lines.append("</svg>")
    svg = "\n".join(svg_lines)

    # Subtitle
    seasons = ("spring", "summer", "autumn", "winter")
    end_season = seasons[season_index(world.tick - 1)]
    end_year = year_of(world.tick - 1)
    n_alive = sum(1 for c in world.chars if c.alive)
    n_dead = sum(1 for c in world.chars if not c.alive)
    subtitle_parts = [f"{world.initial_people} founders · {world.tick} days"]
    if end_year > 1:
        subtitle_parts.append(f"ends year {end_year}, {end_season}")
    if n_dead:
        subtitle_parts.append(f"{n_alive} living, {n_dead} dead")
    subtitle = " · ".join(subtitle_parts)

    legend_html = (
        '<div class="legend">'
        '<span class="li"><span class="ll" style="background:#c8a020;height:4px"></span>bond</span>'
        '<span class="li"><span class="ll" style="background:#cc4400"></span>warmth</span>'
        '<span class="li"><span class="ll" style="background:#2244cc"></span>coldness</span>'
        '<span class="li"><span class="lc" style="background:#3a6fa8"></span>living</span>'
        '<span class="li"><span class="lc" style="background:#3a4a5a;opacity:0.55"></span>dead</span>'
        '<span class="li"><span class="lc" style="background:#3a6fa8;'
        'border:2px solid #c8a020"></span>elder</span>'
        '</div>'
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Village of {narrator.village}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0d1117;color:#c9d1d9;font-family:Georgia,serif;
     display:flex;flex-direction:column;align-items:center;padding:28px 16px 40px}}
h1{{font-size:1.25em;font-weight:normal;letter-spacing:.07em;color:#d4a520;margin-bottom:5px}}
.sub{{font-size:.78em;color:#6b7280;font-style:italic;margin-bottom:18px}}
.legend{{display:flex;gap:18px;font-size:.74em;color:#9ca3af;margin-bottom:16px;
         flex-wrap:wrap;justify-content:center}}
.li{{display:flex;align-items:center;gap:5px}}
.ll{{display:inline-block;width:26px;height:3px;border-radius:2px}}
.lc{{display:inline-block;width:11px;height:11px;border-radius:50%}}
svg{{max-width:100%}}
.colophon{{font-size:.7em;color:#3d4451;font-style:italic;margin-top:18px;text-align:center}}
</style>
</head>
<body>
<h1>The Village of {narrator.village}</h1>
<p class="sub">{subtitle}</p>
{legend_html}
{svg}
<p class="colophon">world seed {world.seed} · same seed, same web, every time</p>
<script>{_JS}</script>
</body>
</html>"""

    return html
