/* Montante – service worker: app disponibile anche senza rete */
const VERSION = 'montante-1.2';
const SHELL = ['./', './index.html', './manifest.webmanifest', './leaflet.js', './leaflet.css', './icon-180.png', './icon-192.png', './icon-512.png',
  './manrope-500.woff2', './manrope-600.woff2', './manrope-700.woff2', './manrope-800.woff2', './unbounded-600.woff2', './unbounded-700.woff2'].concat(["./foto/alletterato.jpg", "./foto/amia.jpg", "./foto/calamaro.jpg", "./foto/cefalo.jpg", "./foto/corvina.jpg", "./foto/fasciato.jpg", "./foto/fragolino.jpg", "./foto/gallinella.jpg", "./foto/go.jpg", "./foto/lanzardo.jpg", "./foto/leccia.jpg", "./foto/mafrone.jpg", "./foto/mormora.jpg", "./foto/ombrina.jpg", "./foto/orata.jpg", "./foto/pagro.jpg", "./foto/palamita.jpg", "./foto/passera.jpg", "./foto/pizzuto.jpg", "./foto/rombo.jpg", "./foto/sarago.jpg", "./foto/seppia.jpg", "./foto/serra.jpg", "./foto/sgombro.jpg", "./foto/sogliola.jpg", "./foto/sparaglione.jpg", "./foto/spigola.jpg", "./foto/sugarello.jpg", "./foto/tracina.jpg", "./foto/triglia.jpg"]);

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  // toglie le copie delle versioni precedenti, comprese le vecchie foto scaricate da iNaturalist
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // mappe e previsioni: sempre dalla rete
  if (req.mode === 'navigate') {
    // pagina: prima la rete (per ricevere gli aggiornamenti), senza campo la copia salvata
    e.respondWith((async () => {
      const cache = await caches.open(VERSION);
      const net = fetch(req).then(r => { if (r.ok) cache.put('./index.html', r.clone()); return r; });
      const timeout = new Promise(res => setTimeout(res, 3500));
      const first = await Promise.race([net.catch(() => null), timeout]);
      if (first) return first;
      const cached = await cache.match('./index.html');
      return cached || net;
    })());
    return;
  }
  e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {
    if (res.ok) { const cp = res.clone(); caches.open(VERSION).then(c => c.put(req, cp)); }
    return res;
  })));
});
