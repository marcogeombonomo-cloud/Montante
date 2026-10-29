"""Terza sonda: dataset meteomarini del Centro Maree e tempo reale ISPRA."""
import re, time, urllib.request, urllib.error, urllib.parse, os
UA = 'MontanteProbe/1.0 (https://github.com/marcogeombonomo-cloud/Montante)'
ORIGIN = 'https://marcogeombonomo-cloud.github.io'
OUT = []
def get(url, n=800000):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Origin': ORIGIN, 'Accept': '*/*', 'Referer': url})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, dict(r.headers), r.read(n).decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(3000).decode('utf-8', 'replace')
    except Exception as e:
        return None, {}, repr(e)
def show(u, n=2500):
    st, h, t = get(u)
    acao = h.get('Access-Control-Allow-Origin') or h.get('access-control-allow-origin')
    OUT.append(f'### {u}\nstato {st} | {h.get("Content-Type")} | CORS {acao} | {len(t)} char\n{t[:n]}\n')
    return t
t = show('https://dati.venezia.it/?q=content/cpsm-dati-meteomarini-laguna-e-litorale-veneziano', 200)
links = sorted(set(re.findall(r'href="([^"]+)"', t)))
OUT.append('LINK DATASET:\n  ' + '\n  '.join(l for l in links if re.search(r'json|csv|xml|txt|files|dataset|resource|download', l, re.I)))
for l in links:
    if re.search(r'\.(json|csv|xml|txt)(\?|$)', l, re.I):
        show(urllib.parse.urljoin('https://dati.venezia.it/', l), 1800); time.sleep(.5)
# pagina ISPRA tempo reale: html completo per vedere le chiamate ajax
t = show('https://www.venezia.isprambiente.it/ispra/webgis/marea.php', 6000)
for s in re.findall(r'src="([^"]+\.js[^"]*)"', t):
    if 'jquery' in s: continue
    show(urllib.parse.urljoin('https://www.venezia.isprambiente.it/ispra/webgis/', s), 5000)
show('https://www.venezia.isprambiente.it/ispra/webgis/mareaadr.php', 6000)
# onde alto adriatico (Centro Maree)
t = show('https://www.comune.venezia.it/it/content/previsioni-altezza-onda-nellalto-adriatico-0', 100)
OUT.append('IMG/FILE onde:\n  ' + '\n  '.join(sorted(set(re.findall(r'(?:src|href)="([^"]+(?:png|gif|jpg|txt|csv|json|pdf)[^"]*)"', t)))))
t = show('https://www.comune.venezia.it/it/content/previsioni-onda-alto-adriatico-0', 100)
OUT.append('IMG/FILE onde2:\n  ' + '\n  '.join(sorted(set(re.findall(r'(?:src|href)="([^"]+(?:png|gif|jpg|txt|csv|json|pdf)[^"]*)"', t)))))
t = show('https://www.comune.venezia.it/it/content/il-bollettino-marea-venezia', 100)
OUT.append('FILE bollettino:\n  ' + '\n  '.join(sorted(set(re.findall(r'(?:src|href)="([^"]+(?:png|gif|jpg|txt|csv|json|pdf|xml)[^"]*)"', t)))))
t = show('https://www.comune.venezia.it/it/content/dati-dalle-stazioni-rilevamento', 100)
OUT.append('FILE stazioni:\n  ' + '\n  '.join(sorted(set(re.findall(r'(?:src|href)="([^"]+)"', t)))[:200]))
os.makedirs('sonde', exist_ok=True)
open('sonde/risultati3.txt', 'w').write('\n'.join(OUT))
