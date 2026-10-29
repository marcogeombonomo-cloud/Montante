"""Raccoglie i dati aperti del Centro Previsioni e Segnalazioni Maree del Comune di Venezia
(dati.venezia.it, licenza IODL 2.0) e li riscrive in un solo file JSON leggibile dall'app.
Il sito del Comune non permette la lettura diretta dal browser (niente CORS): questo passaggio la rende possibile."""
import json, re, sys, time, urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
BASE = 'https://dati.venezia.it/sites/default/files/dataset/opendata/'
UA = 'Montante/1.3 (app personale di pesca; https://github.com/marcogeombonomo-cloud/Montante)'
ROMA = ZoneInfo('Europe/Rome')
def get(name):
    for k in range(3):
        try:
            req = urllib.request.Request(BASE + name, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            err = e; time.sleep(3 + 5 * k)
    print('non disponibile:', name, err, file=sys.stderr); return None
def ms(s):
    # orari del Centro Maree: ora italiana
    try: return int(datetime.strptime(s.strip(), '%Y-%m-%d %H:%M:%S').replace(tzinfo=ROMA).timestamp() * 1000)
    except Exception: return None
def nums(v): return [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', v or '')]
out = {'fonte': 'Centro Previsioni e Segnalazioni Maree, Comune di Venezia (dati.venezia.it, IODL 2.0)',
       'creato': int(time.time() * 1000), 'previsione': None, 'livelli': {}, 'vento': {}, 'onde': {}, 'acqua': {}, 'pressione': {}}
p = get('previsione.json')
if p:
    est = [{'t': ms(x.get('DATA_ESTREMALE', '')), 'tipo': x.get('TIPO_ESTREMALE'), 'cm': float(x['VALORE'])}
           for x in p if x.get('VALORE') not in (None, '') and ms(x.get('DATA_ESTREMALE', ''))]
    out['previsione'] = {'emessa': ms(p[0].get('DATA_PREVISIONE', '')) if p else None, 'stazione': 'Punta della Salute', 'estremi': sorted(est, key=lambda e: e['t'])}
for name, key, conv in [('livello.json', 'livelli', lambda n: {'cm': round(n[0] * 100)}),
                        ('vento.json', 'vento', lambda n: {'dir': n[0], 'kmh': round(n[1] * 3.6, 1), 'raffica_kmh': round(n[2] * 3.6, 1) if len(n) > 2 else None}),
                        ('onde_mare.json', 'onde', lambda n: {'hs': n[0], 'hmax': n[1] if len(n) > 1 else None}),
                        ('tempacqua.json', 'acqua', lambda n: {'c': n[0]}),
                        ('pressione.json', 'pressione', lambda n: {'hpa': n[0]})]:
    d = get(name) or []
    for x in d:
        n = nums(x.get('valore')); t = ms(x.get('data', ''))
        if not n or not t: continue
        try: rec = conv(n)
        except Exception: continue
        rec.update({'t': t, 'nome': x.get('stazione'), 'lat': float(x['latDDN']) if x.get('latDDN') else None, 'lon': float(x['lonDDE']) if x.get('lonDDE') else None})
        out[key][x.get('ID_stazione') or x.get('nome_abbr')] = rec
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else 'venezia.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('ok', len(out['livelli']), 'livelli', len(out['vento']), 'venti', 'previsione' if out['previsione'] else 'senza previsione')
