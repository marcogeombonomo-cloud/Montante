/* Montante – service worker: app disponibile anche senza rete */
const VERSION = 'montante-1.1';
const FOTO = 'montante-foto';
const FOTO_MAX = 150;
const SHELL = ['./', './index.html', './manifest.webmanifest', './leaflet.js', './leaflet.css', './icon-180.png', './icon-192.png', './icon-512.png',
  './manrope-500.woff2', './manrope-600.woff2', './manrope-700.woff2', './manrope-800.woff2', './unbounded-600.woff2', './unbounded-700.woff2'];
const FOTO_HOSTS = ['inaturalist-open-data.s3.amazonaws.com', 'static.inaturalist.org'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION && k !== FOTO).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
async function trim(cache, max) {
  const keys = await cache.keys();
  for (let i = 0; i < keys.length - max; i++) await cache.delete(keys[i]);
}
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (FOTO_HOSTS.includes(url.hostname)) {
    // foto dei pesci: dalla copia salvata, così la guida funziona anche in spiaggia senza campo
    e.respondWith((async () => {
      const cache = await caches.open(FOTO);
      const hit = await cache.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok || res.type === 'opaque') { await cache.put(req, res.clone()); trim(cache, FOTO_MAX); }
      return res;
    })());
    return;
  }
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
