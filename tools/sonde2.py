# Sesta sonda: le chiamate esatte dell'app a Open-Meteo rispondono con dati validi?
import urllib.request, json, os, statistics
U = {
 'meteo': 'https://api.open-meteo.com/v1/forecast?latitude=45.2100&longitude=12.3100&hourly=wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,pressure_msl,weather_code,precipitation&models=italia_meteo_arpae_icon_2i,ecmwf_ifs&past_days=1&forecast_days=7&timeformat=unixtime&wind_speed_unit=kmh&timezone=GMT',
 'onde': 'https://marine-api.open-meteo.com/v1/marine?latitude=45.2100&longitude=12.3100&hourly=wave_height,wave_period,wave_direction&models=dwd_ewam,ecmwf_wam&past_days=1&forecast_days=7&timeformat=unixtime&cell_selection=sea',
 'sst': 'https://marine-api.open-meteo.com/v1/marine?latitude=45.2100&longitude=12.3100&hourly=sea_surface_temperature&past_days=1&forecast_days=7&timeformat=unixtime&cell_selection=sea',
 'brenta': 'https://flood-api.open-meteo.com/v1/flood?latitude=45.175&longitude=12.275&daily=river_discharge&past_days=60&forecast_days=7&timeformat=unixtime',
}
out = []
for k, u in U.items():
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Montante-sonda'}), timeout=40) as r:
            d = json.loads(r.read())
        out.append(f'== {k}: lat {d.get("latitude")} lon {d.get("longitude")}')
        h = d.get('hourly') or d.get('daily')
        for name, a in h.items():
            if name == 'time': out.append(f'  time n={len(a)}'); continue
            nn = [x for x in a if x is not None]
            firstnull = next((i for i, x in enumerate(a) if x is None), None)
            lastval = max((i for i, x in enumerate(a) if x is not None), default=None)
            out.append(f'  {name}: n={len(a)} validi={len(nn)} primo_null={firstnull} ultimo_valido={lastval} min={min(nn) if nn else None} med={statistics.median(nn) if nn else None} max={max(nn) if nn else None}')
        if k == 'brenta': out.append('  ultimi 12: ' + str(h['river_discharge'][-12:]))
    except Exception as e:
        out.append(f'ERR {k} {e}')
os.makedirs('sonde', exist_ok=True)
open('sonde/risultati6.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
