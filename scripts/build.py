#!/usr/bin/env python3
import json, pathlib, html, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
ASSETS = ROOT / 'assets'

ADSENSE_HEAD = '''<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8281021937433044"
     crossorigin="anonymous"></script>'''

ADSENSE_PUBLISHER = 'ca-pub-8281021937433044'
ADSENSE_SLOTS = {
    'inline-1': '6626839246',
    'mid-2': '7732037353',
    'bottom': '7839848569',
}
ADSENSE_LABELS = {
    'inline-1': 'Haut de page',
    'mid-2': 'Milieu de page',
    'bottom': 'Bas de page',
}


def load(name):
    return json.loads((DATA_DIR / name).read_text(encoding='utf-8'))


def esc(value):
    return html.escape(str(value), quote=True)


def merged_tools():
    tools = load('ias.json')['items']
    prices = load('prix.json')['items']
    out = []
    for tool in tools:
        item = dict(tool)
        item.update(prices.get(tool['id'], {}))
        out.append(item)
    return out


def nav(prefix='', active=''):
    links = [
        ('index.html', 'Accueil', 'home'),
        ('choisir.html', 'Quelle IA choisir ?', 'choose'),
        ('catalogue.html', 'Catalogue', 'catalogue'),
        ('categories.html', 'Catégories', 'categories'),
        ('comparer.html', 'Comparer', 'compare'),
        ('local.html', 'IA locale & GPU', 'local'),
        ('modeles-locaux.html', 'Modèles locaux', 'models'),
        ('tutoriels.html', 'Tutoriels', 'tutorials'),
        ('glossaire.html', 'Glossaire', 'glossary'),
    ]
    rendered = ''.join(
        f'<a class="{"active" if key == active else ""}" href="{prefix}{href}">{label}</a>'
        for href, label, key in links
    )
    mobile = ''.join(
        f'<a class="{"active" if key == active else ""}" href="{prefix}{href}">{label}</a>'
        for href, label, key in links
    )
    project_active = ' active' if active == 'forgotten' else ''
    support_active = ' active' if active == 'support' else ''
    return (
        f'<header class="top"><nav class="nav">'
        f'<a class="brand" href="{prefix}index.html"><span class="brand-badge">IA</span> IA Atlas</a>'
        f'<div class="links">{rendered}</div><div class="grow"></div>'
        f'<a class="btn project-link{project_active}" href="{prefix}forgotten-source.html">🌌 Forgotten Source</a>'
        f'<a class="btn support-link{support_active}" href="{prefix}soutenir.html">💜 Soutenir</a>'
        f'<details class="mobile-menu"><summary aria-label="Ouvrir le menu">☰</summary><div class="mobile-panel">{mobile}'
        f'<a class="project-link{project_active}" href="{prefix}forgotten-source.html">🌌 Forgotten Source</a>'
        f'<a class="support-link{support_active}" href="{prefix}soutenir.html">💜 Soutenir</a>'
        f'</div></details></nav></header>'
    )

def ad_slot(slot='inline-1', kind='medium'):
    google_slot = ADSENSE_SLOTS[slot]
    label = ADSENSE_LABELS[slot]
    return (
        f'<div class="ad-zone ad-{kind}" data-ia-atlas-ad-zone="{slot}">'
        f'<div class="ad-slot adsense-unit" data-ad-slot="{google_slot}" data-ad-provider="adsense">'
        f'<div class="ad-inner"><span class="ad-title">PUBLICITÉ • {label}</span>'
        '<span class="ad-copy">Emplacement publicitaire AdSense — cette zone reste visible même si aucune annonce n’est encore diffusée.</span></div>'
        f'<ins class="adsbygoogle" style="display:block;width:100%" data-ad-client="{ADSENSE_PUBLISHER}" '
        f'data-ad-slot="{google_slot}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
        '</div></div><script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'
    )

def footer(prefix=''):
    return (
        '<footer class="footer">'
        f'<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:12px">'
        f'<a class="project-link btn" href="{prefix}forgotten-source.html">🌌 Forgotten Source</a>'
        f'<a class="support-link btn" href="{prefix}soutenir.html">💜 Soutenir IA Atlas</a></div>'
        '<div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-bottom:10px">'
        f'<a href="{prefix}a-propos.html">À propos</a>'
        f'<a href="{prefix}mentions-legales.html">Mentions légales</a>'
        f'<a href="{prefix}confidentialite.html">Confidentialité</a>'
        f'<a href="{prefix}cookies.html">Cookies</a>'
        f'<a href="{prefix}sources.html">Sources</a>'
        '</div>IA Atlas • guide indépendant • aucune affiliation avec les services cités.'
        '</footer>'
    )

def shell(title, description, body, prefix='', active=''):
    style = (ASSETS / 'site.css').read_text(encoding='utf-8')
    return (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{esc(title)}</title><meta name="description" content="{esc(description)}">'
        '<meta name="robots" content="index,follow">'
        f'{ADSENSE_HEAD}'
        f'<style>{style}</style></head><body><div class="shell">{nav(prefix, active)}'
        f'<main class="container">{body}</main>{footer(prefix)}</div></body></html>'
    )


def tool_page(tool, tools_by_id):
    source_url = tool.get('sourceUrl') or tool.get('officialUrl', '')
    status_class = 'official' if source_url else 'warn'
    reliability = '✓ Source officielle liée' if source_url else '⚠ Information à revérifier'
    scores = ''.join(
        f'<div class="score"><span>{esc(k)}</span><div class="bar"><i style="width:{int(v)*10}%"></i></div><b>{esc(v)}</b></div>'
        for k, v in tool.get('scores', {}).items()
    )
    strengths = ''.join(f'<li>{esc(x)}</li>' for x in tool.get('strengths', []))
    limits = ''.join(f'<li>{esc(x)}</li>' for x in tool.get('limits', []))
    alternatives = []
    for alt_id in tool.get('alternatives', []):
        alt = tools_by_id.get(alt_id)
        if alt:
            alternatives.append(f'<a class="btn" href="{esc(alt_id)}.html">{esc(alt["name"])}</a>')
    official = (
        f'<a class="btn primary" href="{esc(tool.get("officialUrl"))}" target="_blank" rel="noopener">Ouvrir le site officiel ↗</a>'
        if tool.get('officialUrl') else '<span class="badge warn">Lien officiel à ajouter</span>'
    )
    tags = ''.join(f'<span class="tag">{esc(tag)}</span>' for tag in tool.get('tags', []))
    body = f'''
<div class="breadcrumb"><a href="../index.html">Accueil</a> › <a href="../catalogue.html">Catalogue</a> › {esc(tool['name'])}</div>
<section class="details-hero">
  <div class="hero">
    <div class="tool-id"><div class="avatar">{esc(tool.get('mark', tool['name'][0]))}</div><div><span class="eyebrow">{esc(tool.get('kindLabel','IA'))}</span><h1 style="margin:8px 0">{esc(tool['name'])}</h1><div class="muted">{esc(tool.get('company',''))}</div></div></div>
    <p class="lead">{esc(tool.get('desc',''))}</p>
    <div class="simple"><b>En clair :</b> {esc(tool.get('simple',''))}</div>
    <div class="actions"><button class="favbtn" data-id="{esc(tool['id'])}">☆ Ajouter aux favoris</button><button class="btn addcompare" data-id="{esc(tool['id'])}">Ajouter au comparateur</button></div>
  </div>
  <aside class="card side-summary">
    <span class="reliability {status_class}">{reliability}</span>
    <div class="kv">
      <div><small>Prix indicatif</small><b>{esc(tool.get('price','Voir site officiel'))}</b></div>
      <div><small>Niveau</small><b>{esc(tool.get('level',''))}</b></div>
      <div><small>Idéal pour</small><b>{esc(tool.get('bestFor',''))}</b></div>
      <div><small>Dernière vérification</small><b>{esc(tool.get('verified',''))}</b></div>
    </div>{official}
  </aside>
</section>
{ad_slot()}
<section class="section two">
  <div class="card"><h2>Pour qui ?</h2><p class="muted">{esc(tool.get('who',''))}</p><h3 style="margin-top:18px">Points forts</h3><ul class="checklist good">{strengths}</ul></div>
  <div class="card"><h2>Limites à connaître</h2><ul class="checklist bad">{limits}</ul><h3 style="margin-top:18px">Prix</h3><p><b>{esc(tool.get('price',''))}</b></p><p class="muted small">{esc(tool.get('priceNote',''))}</p></div>
</section>
{ad_slot('mid-2','native')}
<section class="section two">
  <div class="card"><h2>Compétences</h2>{scores}</div>
  <div class="card"><h2>Verdict IA Atlas</h2><div class="verdict">{esc(tool.get('verdict',''))}</div><h3 style="margin-top:18px">Tags</h3><div class="tags">{tags}</div></div>
</section>
<section class="section"><div class="card"><h2>Alternatives</h2><div class="actions">{''.join(alternatives) or '<span class="muted">Aucune alternative renseignée.</span>'}</div></div></section>
{ad_slot('bottom')}
<script src="../assets/user-state.js"></script>
'''
    return shell(f"{tool['name']} — fiche détaillée | IA Atlas", tool.get('simple',''), body, '../', 'catalogue')


def category_page(kind, label, description, tools):
    items = [t for t in tools if t.get('kind') == kind]
    cards = ''.join(
        f'<article class="card tool-card"><div class="tool-top"><div class="tool-id"><div class="avatar">{esc(t.get("mark",t["name"][0]))}</div><div><h3>{esc(t["name"])}</h3><div class="muted small">{esc(t.get("company",""))}</div></div></div><span class="badge">{esc(t.get("price",""))}</span></div><div class="simple"><b>En clair :</b> {esc(t.get("simple",""))}</div><a class="btn" href="../ia/{esc(t["id"])}.html">Voir la fiche</a></article>'
        for t in items
    )
    body = (
        f'<div class="breadcrumb"><a href="../index.html">Accueil</a> › <a href="../categories.html">Catégories</a> › {esc(label)}</div>'
        f'<section class="hero"><span class="eyebrow">Catégorie</span><h1>{esc(label)}</h1><p class="lead">{esc(description)}</p></section>'
        f'{ad_slot()}<section class="section"><div class="section-head"><div><h2>{len(items)} outils</h2><p>Fiches générées depuis la base centrale.</p></div></div><div class="grid">{cards}</div></section>{ad_slot('mid-2','native')}{ad_slot("bottom")}'
    )
    return shell(f'{label} — IA Atlas', description, body, '../', 'categories')


def model_overview(data):
    families = data['families']; models = data['models']
    cards = ''.join(
        f'<article class="card"><h3>{esc(f["name"])}</h3><p class="muted small">{esc(f["company"])}</p><p>{esc(f["description"])}</p><div class="tags"><span class="tag">{sum(1 for m in models if m["familyId"]==f["id"])} variantes suivies</span></div><a class="btn" href="{esc(f["page"])}">Voir la famille</a></article>'
        for f in families
    )
    body = f'<section class="hero"><span class="eyebrow">Base locale centralisée</span><h1>Modèles locaux</h1><p class="lead">Toutes les variantes affichées viennent de <code>data/modeles-locaux.json</code>.</p></section>{ad_slot()}<section class="section"><div class="grid">{cards}</div></section>{ad_slot('mid-2','native')}{ad_slot("bottom")}'
    return shell('Modèles locaux — IA Atlas', 'Familles de modèles locaux et estimations de VRAM.', body, '', 'models')


def model_family_page(family, models):
    rows = ''.join(
        f'<tr><td><b>{esc(m["name"])}</b></td><td>{esc(m.get("parametersB","?"))}B</td><td>≈ {esc(m["q4VramEstimateGB"])} Go</td><td>{esc(m.get("notes",""))}</td></tr>'
        for m in models
    )
    official = f'<a class="btn primary" href="{esc(family.get("officialUrl"))}" target="_blank" rel="noopener">Source / site officiel ↗</a>' if family.get('officialUrl') else ''
    body = f'<div class="breadcrumb"><a href="../index.html">Accueil</a> › <a href="../modeles-locaux.html">Modèles locaux</a> › {esc(family["name"])}</div><section class="hero"><span class="eyebrow">{esc(family.get("company",""))}</span><h1>{esc(family["name"])}</h1><p class="lead">{esc(family["description"])}</p><div class="actions">{official}</div></section>{ad_slot()}<section class="section"><div class="card"><h2>Variantes suivies</h2><div style="overflow:auto"><table class="compare-table"><thead><tr><th>Modèle</th><th>Paramètres</th><th>VRAM poids Q4</th><th>Note</th></tr></thead><tbody>{rows}</tbody></table></div><div class="notice" style="margin-top:16px"><b>Important :</b> ces besoins VRAM sont des estimations pratiques. Le contexte, le moteur et l’offloading peuvent changer la mémoire réelle.</div></div></section>{ad_slot('mid-2','native')}{ad_slot("bottom")}'
    return shell(f'{family["name"]} — IA Atlas', family['description'], body, '../', 'models')


def write_runtime_data(tools):
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / 'data.js').write_text('window.IA_ATLAS=' + json.dumps(tools, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    gpu = load('gpu.json')['items']
    local = load('modeles-locaux.json')
    gp = [[x['name'], x['vramGB'], x['architecture']] for x in gpu]
    family_map = {x['id']: x for x in local['families']}
    models = [
        {'name': m['name'], 'family': family_map[m['familyId']]['name'], 'need': m['q4VramEstimateGB'], 'url': family_map[m['familyId']]['page']}
        for m in local['models']
    ]
    (ASSETS / 'local-data.js').write_text(
        'window.IA_GPU=' + json.dumps(gp, ensure_ascii=False, separators=(',', ':')) + ';'
        'window.IA_LOCAL_MODELS=' + json.dumps(models, ensure_ascii=False, separators=(',', ':')) + ';\n',
        encoding='utf-8'
    )


def patch_runtime_pages():
    # The three interactive pages read the single derived dataset assets/data.js.
    def replace_data_array(source):
        marker = 'const DATA='
        if 'const DATA=window.IA_ATLAS;' in source:
            return source
        start = source.find(marker)
        if start < 0:
            return source
        arr = source.find('[', start + len(marker))
        if arr < 0:
            return source
        depth = 0; in_string = False; escaped = False; end = -1
        for i in range(arr, len(source)):
            ch = source[i]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end < 0:
            return source
        semi = end + 1
        if semi < len(source) and source[semi] == ';':
            semi += 1
        return source[:start] + 'const DATA=window.IA_ATLAS;' + source[semi:]

    for name in ['catalogue.html', 'choisir.html', 'comparer.html']:
        path = ROOT / name
        s = replace_data_array(path.read_text(encoding='utf-8'))
        if 'src="assets/data.js"' not in s:
            s = s.replace('<script>const DATA=window.IA_ATLAS;', '<script src="assets/data.js"></script><script>const DATA=window.IA_ATLAS;', 1)
        path.write_text(s, encoding='utf-8')

    # The GPU page reads assets/local-data.js generated from gpu.json + modeles-locaux.json.
    path = ROOT / 'local.html'
    s = path.read_text(encoding='utf-8')
    if 'const GPUS=window.IA_GPU' not in s:
        s = re.sub(
            r'<script>const GPUS=\[.*?\],MODELS=\[.*?\];(?=function lvl)',
            '<script src="assets/local-data.js"></script><script>const GPUS=window.IA_GPU,MODELS=window.IA_LOCAL_MODELS;',
            s, count=1, flags=re.S
        )
    elif 'src="assets/local-data.js"' not in s:
        s = s.replace('<script>const GPUS=window.IA_GPU', '<script src="assets/local-data.js"></script><script>const GPUS=window.IA_GPU', 1)
    path.write_text(s, encoding='utf-8')



def write_search_files():
    """Keep Search Console / AdSense support files in sync with the deployed Cloudflare Pages domain."""
    import xml.sax.saxutils as xmlutils
    base = 'https://ia-atlas.pages.dev/'
    exclude = {'404.html', 'googleadd0c574641401b2.html', 'emplacements-publicitaires.html'}
    urls = []
    for path in sorted(ROOT.rglob('*.html')):
        rel = path.relative_to(ROOT).as_posix()
        if rel in exclude or rel.startswith('.github/'):
            continue
        if rel == 'index.html':
            loc, priority = base, '1.0'
        else:
            loc = base + rel
            if rel in {'catalogue.html','choisir.html','categories.html','local.html','modeles-locaux.html','tutoriels.html','forgotten-source.html','soutenir.html'}:
                priority = '0.8'
            elif rel.startswith(('ia/','categorie/','modeles/')):
                priority = '0.7'
            else:
                priority = '0.5'
        urls.append((loc, priority))
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, priority in urls:
        out += ['  <url>', f'    <loc>{xmlutils.escape(loc)}</loc>', '    <lastmod>2026-09-09</lastmod>', f'    <priority>{priority}</priority>', '  </url>']
    out.append('</urlset>')
    (ROOT / 'sitemap.xml').write_text('\n'.join(out) + '\n', encoding='utf-8')
    (ROOT / 'robots.txt').write_text(
        'User-agent: *\nAllow: /\nDisallow: /emplacements-publicitaires.html\n\nSitemap: https://ia-atlas.pages.dev/sitemap.xml\n',
        encoding='utf-8'
    )
    (ROOT / 'ads.txt').write_text('google.com, pub-8281021937433044, DIRECT, f08c47fec0942fa0\n', encoding='utf-8')
    (ROOT / 'googleadd0c574641401b2.html').write_text(
        'google-site-verification: googleadd0c574641401b2.html\n', encoding='utf-8'
    )


def main():
    tools = merged_tools()
    tools_by_id = {t['id']: t for t in tools}
    write_runtime_data(tools)
    patch_runtime_pages()

    (ROOT / 'ia').mkdir(exist_ok=True)
    for tool in tools:
        (ROOT / 'ia' / f'{tool["id"]}.html').write_text(tool_page(tool, tools_by_id), encoding='utf-8')

    category_defs = {
        'assistant': ('assistant', 'Assistants généralistes', 'Pour discuter, écrire et faire un peu de tout.'),
        'recherche': ('research', 'Recherche', 'Pour chercher, synthétiser et explorer des sources.'),
        'code': ('coding', 'Code', 'Pour programmer, corriger et créer des applications.'),
        'image': ('image', 'Image', 'Pour générer et modifier des images.'),
        'video': ('video', 'Vidéo', 'Pour générer des vidéos et avatars.'),
        'audio': ('audio', 'Audio & voix', 'Pour musique, voix et transcription.'),
        'local': ('local-chat', 'IA locale', 'Pour faire tourner des modèles sur votre propre PC.'),
        'agents': ('rag-agent', 'Agents & automatisation', 'Pour connecter des outils, documents et actions.'),
        'productivite': ('productivity', 'Productivité', 'Pour documents, réunions et logiciels de travail.'),
    }
    (ROOT / 'categorie').mkdir(exist_ok=True)
    for slug, (kind, label, desc) in category_defs.items():
        (ROOT / 'categorie' / f'{slug}.html').write_text(category_page(kind, label, desc, tools), encoding='utf-8')

    local_data = load('modeles-locaux.json')
    (ROOT / 'modeles-locaux.html').write_text(model_overview(local_data), encoding='utf-8')
    (ROOT / 'modeles').mkdir(exist_ok=True)
    for family in local_data['families']:
        models = [m for m in local_data['models'] if m['familyId'] == family['id']]
        (ROOT / family['page']).write_text(model_family_page(family, models), encoding='utf-8')

    write_search_files()

    print(f'IA Atlas build OK: {len(tools)} outils, {len(local_data["models"])} modèles locaux, {len(load("gpu.json")["items"])} GPU')


if __name__ == '__main__':
    main()
