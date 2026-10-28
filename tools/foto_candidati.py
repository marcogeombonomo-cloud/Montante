"""Raccoglie da Wikimedia Commons le immagini candidate per ogni specie e crea un foglio di anteprime numerato.
Fase 1 (senza scelte.json): fogli/<id>.jpg + fogli/<id>.json. Fase 2 (con scelte.json): foto/<id>.jpg + foto/crediti.json."""
import json, os, re, io, sys, time, html, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
UA = 'MontanteFishGuide/1.0 (https://github.com/marcogeombonomo-cloud/Montante; personal fishing app)'
API = 'https://commons.wikimedia.org/w/api.php'
KEY = re.compile(r'draw|illustr|plate|tafel|tav\.|bloch|cuvier|valenc|bonaparte|iconograf|fmib|noaa|fao|lithogr|fische|poisson|engraving|gravure|naturgeschichte|histoire', re.I)
BAD = re.compile(r'map|distribution|range|verbreitung|areal|\.svg$|\.tif|\.pdf$|\.djvu$|fillet|sushi|market|mercato|dish|recipe|cooked|grilled|stamp|briefmarke|logo|otolith|skeleton|scale_', re.I)
def get(params):
    params = dict(params, format='json', formatversion='2')
    url = API + '?' + urllib.parse.urlencode(params)
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(2 + 3 * k)
    return {}
def fetch(url):
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                return r.read()
        except Exception:
            time.sleep(2 + 3 * k)
    return None
def pages_from(params):
    d = get(dict(params, prop='imageinfo', iiprop='url|extmetadata|size|mime', iiurlwidth='420'))
    return (d.get('query') or {}).get('pages') or []
def clean(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', h or ''))).strip()
def candidates(latin):
    seen, out = set(), []
    cats = ['Category:' + latin]
    sub = get({'action': 'query', 'list': 'categorymembers', 'cmtitle': cats[0], 'cmtype': 'subcat', 'cmlimit': '50'})
    for c in ((sub.get('query') or {}).get('categorymembers') or [])[:12]:
        cats.append(c['title'])
    groups = []
    for c in cats:
        groups.append(pages_from({'action': 'query', 'generator': 'categorymembers', 'gcmtitle': c, 'gcmtype': 'file', 'gcmlimit': '60'}))
    groups.append(pages_from({'action': 'query', 'generator': 'search', 'gsrsearch': f'"{latin}" filetype:bitmap', 'gsrnamespace': '6', 'gsrlimit': '40'}))
    for g in groups:
        for p in g:
            t = p.get('title', '')
            ii = (p.get('imageinfo') or [{}])[0]
            if t in seen or not ii.get('thumburl') or BAD.search(t): continue
            if ii.get('mime') not in ('image/jpeg', 'image/png'): continue
            if (ii.get('width') or 0) < 350: continue
            seen.add(t)
            md = ii.get('extmetadata') or {}
            out.append({'title': t, 'thumb': ii['thumburl'], 'url': ii.get('url'), 'page': ii.get('descriptionurl'),
                        'w': ii.get('width'), 'h': ii.get('height'),
                        'lic': clean((md.get('LicenseShortName') or {}).get('value')), 'artist': clean((md.get('Artist') or {}).get('value'))[:140],
                        'desc': clean((md.get('ImageDescription') or {}).get('value'))[:200], 'kw': bool(KEY.search(t + ' ' + clean((md.get('ImageDescription') or {}).get('value'))))})
    out.sort(key=lambda x: (not x['kw'], -(x['w'] or 0) / max(1, x['h'] or 1)))
    return out[:30]
def sheet(items, path):
    W, H, cols = 300, 210, 5
    rows = (len(items) + cols - 1) // cols
    im = Image.new('RGB', (cols * W, rows * (H + 26)), 'white'); d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
    except Exception: f = ImageFont.load_default()
    with ThreadPoolExecutor(4) as ex:
        blobs = list(ex.map(lambda it: fetch(it['thumb']), items))
    for i, it in enumerate(items):
        x, y = (i % cols) * W, (i // cols) * (H + 26)
        b = blobs[i]
        if b:
            try:
                t = Image.open(io.BytesIO(b)).convert('RGB'); t.thumbnail((W - 8, H - 8)); im.paste(t, (x + (W - t.width) // 2, y + (H - t.height) // 2))
            except Exception: pass
        d.rectangle([x, y + H, x + W - 1, y + H + 25], fill=(20, 40, 50)); d.text((x + 6, y + H + 3), f'{i}  ' + it['lic'][:22], fill='white', font=f)
    im.save(path, quality=82)
def main():
    specie = json.load(open('tools/specie.json'))
    if os.path.exists('tools/scelte.json'):
        scelte = json.load(open('tools/scelte.json')); os.makedirs('foto', exist_ok=True); crediti = {}
        for sid, latin in specie:
            if sid not in scelte: continue
            meta = json.load(open(f'fogli/{sid}.json'))
            it = meta[scelte[sid]]
            src = it['thumb'].replace('/420px-', '/960px-') if '/420px-' in it['thumb'] else it['url']
            b = fetch(src) or fetch(it['url'])
            img = Image.open(io.BytesIO(b)).convert('RGB'); img.thumbnail((900, 900))
            img.save(f'foto/{sid}.jpg', quality=84, optimize=True, progressive=True)
            crediti[sid] = {'title': it['title'], 'page': it['page'], 'lic': it['lic'], 'artist': it['artist']}
            time.sleep(.5)
        json.dump(crediti, open('foto/crediti.json', 'w'), ensure_ascii=False, indent=1)
        return
    os.makedirs('fogli', exist_ok=True)
    for sid, latin in specie:
        items = candidates(latin)
        json.dump(items, open(f'fogli/{sid}.json', 'w'), ensure_ascii=False, indent=1)
        if items: sheet(items, f'fogli/{sid}.jpg')
        print(sid, latin, len(items), flush=True)
main()
