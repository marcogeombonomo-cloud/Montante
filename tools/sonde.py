"""Prova delle fonti di dati: stato, tipo, CORS e un estratto. Scrive sonde/risultati.txt"""
import json, re, sys, time, urllib.request, urllib.error, html
UA = 'MontanteProbe/1.0 (https://github.com/marcogeombonomo-cloud/Montante)'
ORIGIN = 'https://marcogeombonomo-cloud.github.io'
OUT = []
def probe(url, links=False, n=1500):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Origin': ORIGIN, 'Accept': '*/*'})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read(400000); st = r.status; h = dict(r.headers)
    except urllib.error.HTTPError as e:
        body = e.read(4000); st = e.code; h = dict(e.headers)
    except Exception as e:
        OUT.append(f'### {url}\nERRORE: {e!r}\n'); return None
    txt = body.decode('utf-8', 'replace')
    acao = h.get('Access-Control-Allow-Origin') or h.get('access-control-allow-origin')
    OUT.append(f'### {url}\nstato {st} | tipo {h.get("Content-Type")} | CORS {acao} | {len(body)} byte | {time.time()-t:.1f}s\n')
    if links:
        found = sorted(set(re.findall(r'''(?:href|src|url)\s*[=:]\s*["']([^"'#]+)["']''', txt)))
        keep = [u for u in found if re.search(r'json|xml|csv|api|dato|dati|marea|livell|previs|stazion|onde|ondametr|mareogr|temporeale|tempo-reale|open', u, re.I)]
        OUT.append('link: ' + '\n  '.join(keep[:120]) + '\n')
    else:
        OUT.append(txt[:n] + '\n')
    return txt
URLS = [
 # meteo
 ('https://api.open-meteo.com/v1/forecast?latitude=45.21&longitude=12.30&hourly=wind_speed_10m,wind_direction_10m,wind_gusts_10m,pressure_msl,weather_code,precipitation&models=italia_meteo_arpae_icon_2i&forecast_days=3&timeformat=unixtime', False),
 ('https://api.open-meteo.com/v1/forecast?latitude=45.21&longitude=12.30&hourly=wind_speed_10m&models=icon_d2,ecmwf_ifs,ecmwf_ifs025,icon_eu&forecast_days=2&timeformat=unixtime', False),
 ('https://api.open-meteo.com/v1/forecast?latitude=45.21&longitude=12.30&hourly=wind_speed_10m&models=ecmwf_ifs&forecast_days=7', False),
 ('https://api.open-meteo.com/v1/forecast?latitude=45.21&longitude=12.30&hourly=wind_speed_10m&models=best_match&forecast_days=1', False),
 # mare
 ('https://marine-api.open-meteo.com/v1/marine?latitude=45.20&longitude=12.33&hourly=wave_height,wave_direction,wave_period,wind_wave_height,swell_wave_height,sea_surface_temperature,sea_level_height_msl&models=meteofrance_wave,ecmwf_wam,ecmwf_wam025,dwd_ewam,ncep_gfswave016&forecast_days=2&cell_selection=sea', False),
 ('https://marine-api.open-meteo.com/v1/marine?latitude=45.20&longitude=12.33&hourly=wave_height&models=dwd_ewam&forecast_days=7&cell_selection=sea', False),
 ('https://marine-api.open-meteo.com/v1/marine?latitude=45.20&longitude=12.33&hourly=wave_height&models=ecmwf_wam&forecast_days=7&cell_selection=sea', False),
 ('https://marine-api.open-meteo.com/v1/marine?latitude=45.20&longitude=12.33&hourly=sea_surface_temperature,sea_level_height_msl,ocean_current_velocity&forecast_days=2&cell_selection=sea', False),
 # fiumi (torbidità alle foci)
 ('https://flood-api.open-meteo.com/v1/flood?latitude=45.185&longitude=12.29&daily=river_discharge,river_discharge_mean&past_days=7&forecast_days=7', False),
 ('https://flood-api.open-meteo.com/v1/flood?latitude=45.155&longitude=12.32&daily=river_discharge&past_days=3&forecast_days=3', False),
 # maree ufficiali
 ('https://dati.venezia.it/', True),
 ('https://dati.venezia.it/api/3/action/package_search?q=marea&rows=20', False),
 ('https://www.comune.venezia.it/it/content/centro-previsioni-e-segnalazioni-maree', True),
 ('https://www.comune.venezia.it/it/content/dati-dalle-stazioni-rilevamento', True),
 ('https://www.comune.venezia.it/it/content/previsioni-marea', True),
 ('https://www.venezia.isprambiente.it/', True),
 ('https://www.mareografico.it/', True),
 ('https://www.arpa.veneto.it/dati-ambientali/open-data', True),
 ('https://www.arpa.veneto.it/previsioni/it/html/meteo_mare.php', True),
]
for u, l in URLS:
    probe(u, links=l)
    time.sleep(1)
import os
os.makedirs('sonde', exist_ok=True)
open('sonde/risultati.txt', 'w').write('\n'.join(OUT))
