"""Seconda sonda: cerca dentro pagine e script le URL dei dati di marea/onde e le prova."""
import re, time, urllib.request, urllib.error, urllib.parse, os
UA = 'MontanteProbe/1.0 (https://github.com/marcogeombonomo-cloud/Montante)'
ORIGIN = 'https://marcogeombonomo-cloud.github.io'
OUT = []
def get(url, n=600000):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Origin': ORIGIN, 'Accept': '*/*'})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, dict(r.headers), r.read(n).decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(3000).decode('utf-8', 'replace')
    except Exception as e:
        return None, {}, repr(e)
PAGES = [
 'https://www.comune.venezia.it/it/content/centro-previsioni-e-segnalazioni-maree-beta',
 'https://www.comune.venezia.it/content/previsioni-onda-alto-adriatico-0',
 'https://www.comune.venezia.it/content/dati-meteorologici-venezia',
 'https://www.comune.venezia.it/it/content/centro-previsioni-e-segnalazioni-maree',
 'https://www.comune.venezia.it/it/content/la-previsione',
 'https://www.venezia.isprambiente.it/rete-meteo-mareografica',
 'https://www.venezia.isprambiente.it/webgis/temporeale2.js?v=2',
 'https://dati.venezia.it/?q=ente-gestore/icpsm-istituzione-centro-previsioni-e-segnalazioni-maree',
 'https://dati.venezia.it/?q=formato/json',
 'https://www.mareografico.it/',
]
URLRE = re.compile(r'''(?:https?:)?//[^\s"'<>()]+|(?<=["'])/[^\s"'<>()]+(?=["'])''')
cand = []
for p in PAGES:
    st, h, txt = get(p)
    OUT.append(f'### PAGINA {p}\nstato {st} | {h.get("Content-Type")} | {len(txt)} char')
    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)', txt)
    found = set(URLRE.findall(txt))
    for s in scripts: found.add(s)
    keep = sorted(u for u in found if re.search(r'\.json|\.xml|\.csv|\.txt|json|ajax|api|feed|temporeale|tempo_reale|previs|livell|stazion|onda|marea|\.php', u, re.I) and not re.search(r'facebook|twitter|whatsapp|google|\.css|\.png|\.jpg|\.svg|\.ico|plus\.|linkedin|t\.me', u, re.I))
    OUT.append('  ' + '\n  '.join(keep[:80]))
    for s in scripts:
        if re.search(r'jquery|bootstrap|google|drupal\.js|modernizr', s, re.I): continue
        su = urllib.parse.urljoin(p, s)
        st2, h2, js = get(su)
        inner = sorted(set(u for u in URLRE.findall(js) if re.search(r'json|xml|csv|txt|ajax|api|temporeale|previs|livell|stazion|onda|marea|php', u, re.I)))
        if inner: OUT.append(f'  SCRIPT {su}: ' + ' | '.join(inner[:40]))
        for u in inner: cand.append(urllib.parse.urljoin(su, u))
    for u in keep: cand.append(urllib.parse.urljoin(p, u))
    time.sleep(1)
seen = set(); n = 0
OUT.append('\n=========== PROVE DEI DATI ===========')
for u in cand:
    if u in seen or not u.startswith('http') or n >= 45: continue
    if re.search(r'\.css|\.png|\.jpg|\.svg|\.ico|facebook|twitter|whatsapp', u, re.I): continue
    seen.add(u); n += 1
    st, h, txt = get(u, 200000)
    acao = h.get('Access-Control-Allow-Origin') or h.get('access-control-allow-origin')
    OUT.append(f'### {u}\nstato {st} | {h.get("Content-Type")} | CORS {acao} | {len(txt)} char\n{txt[:700]}\n')
    time.sleep(.7)
os.makedirs('sonde', exist_ok=True)
open('sonde/risultati2.txt', 'w').write('\n'.join(OUT))
