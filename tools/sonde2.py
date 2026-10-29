"""Quarta sonda: riferimento USNO per luna, CORS di raw.githubusercontent, orizzonti dei modelli, fiume Adige."""
import json, time, urllib.request, urllib.error, os
UA = 'MontanteProbe/1.0 (https://github.com/marcogeombonomo-cloud/Montante)'
ORIGIN = 'https://marcogeombonomo-cloud.github.io'
OUT = []
def get(url, n=400000):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Origin': ORIGIN, 'Accept': '*/*'})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, dict(r.headers), r.read(n).decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(3000).decode('utf-8', 'replace')
    except Exception as e:
        return None, {}, repr(e)
def show(u, n=3000):
    st, h, t = get(u)
    acao = h.get('Access-Control-Allow-Origin') or h.get('access-control-allow-origin')
    OUT.append(f'### {u}\nstato {st} | {h.get("Content-Type")} | CORS {acao} | cache {h.get("Cache-Control")} | {len(t)} char\n{t[:n]}\n')
    return t
for d in ['2026-10-30', '2026-10-31', '2026-11-05', '2026-11-12', '2026-11-20']:
    show(f'https://aa.usno.navy.mil/api/rstt/oneday?date={d}&coords=45.2297,12.3095&tz=1', 1800); time.sleep(1)
show('https://raw.githubusercontent.com/marcogeombonomo-cloud/Montante/main/manifest.webmanifest', 300)
def horizon(u):
    st, h, t = get(u)
    try:
        d = json.loads(t); hh = d['hourly']; keys = [k for k in hh if k != 'time']
        out = []
        for k in keys:
            vals = hh[k]; last = max((i for i, v in enumerate(vals) if v is not None), default=-1)
            out.append(f'{k}: ultimo valore a indice {last} ({hh["time"][last] if last >= 0 else "-"})')
        OUT.append(f'### ORIZZONTE {u}\n' + '\n'.join(out) + '\n')
    except Exception as e:
        OUT.append(f'### ORIZZONTE {u}\nerrore {e!r} {t[:300]}\n')
horizon('https://api.open-meteo.com/v1/forecast?latitude=45.21&longitude=12.30&hourly=wind_speed_10m&models=italia_meteo_arpae_icon_2i,icon_d2,ecmwf_ifs&forecast_days=10')
horizon('https://marine-api.open-meteo.com/v1/marine?latitude=45.20&longitude=12.32&hourly=wave_height&models=dwd_ewam,ecmwf_wam,meteofrance_wave&forecast_days=10&cell_selection=sea')
for la, lo in [(45.16, 12.29), (45.15, 12.30), (45.17, 12.28), (45.14, 12.31), (45.18, 12.25), (45.13, 12.30)]:
    show(f'https://flood-api.open-meteo.com/v1/flood?latitude={la}&longitude={lo}&daily=river_discharge,river_discharge_median&past_days=3&forecast_days=2', 600); time.sleep(.5)
show('https://flood-api.open-meteo.com/v1/flood?latitude=45.185&longitude=12.29&daily=river_discharge,river_discharge_median,river_discharge_p75,river_discharge_max&past_days=40&forecast_days=7', 1500)
os.makedirs('sonde', exist_ok=True)
open('sonde/risultati4.txt', 'w').write('\n'.join(OUT))
