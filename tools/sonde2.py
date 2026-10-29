# Quinta sonda: i link mostrati nell'app esistono?
import urllib.request, os
URLS = [
    'https://www.comune.venezia.it/maree',
    'https://www.comune.venezia.it/it/content/centro-previsioni-e-segnalazioni-maree',
    'https://www.comune.venezia.it/it/content/centro-maree',
    'https://dati.venezia.it/',
    'https://open-meteo.com/en/docs/marine-weather-api',
    'https://open-meteo.com/en/docs/flood-api',
    'https://github.com/cosinekitty/astronomy',
]
os.makedirs('sonde', exist_ok=True)
out = []
for u in URLS:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1'})
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read(200000).decode('utf-8', 'replace')
            import re
            t = re.search(r'<title[^>]*>(.*?)</title>', body, re.S)
            out.append(f'{r.status} {u} -> {r.geturl()} | {(t.group(1).strip() if t else "")[:120]}')
    except Exception as e:
        out.append(f'ERR {u} {e}')
open('sonde/risultati5.txt', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
