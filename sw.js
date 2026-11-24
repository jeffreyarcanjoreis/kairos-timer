// Gerado por montar.py — não editar à mão.
const VERSAO = 'kairos-timer-6a308691a5';
const ARQUIVOS = ['./', './index.html', './manifest.webmanifest', './icons/icon-180.png', './icons/icon-192.png', './icons/icon-512.png',
  './fonts/archivo-latin-wdth.woff2', './fonts/archivo-latin-ext.woff2', './fonts/fraunces-latin.woff2', './fonts/fraunces-latin-ext.woff2'];

self.addEventListener('install', ev => {
  ev.waitUntil(caches.open(VERSAO).then(c => c.addAll(ARQUIVOS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', ev => {
  // apaga versões antigas, inclusive o cache de fontes do Google usado até 24/11/2026
  ev.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== VERSAO).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', ev => {
  const req = ev.request;
  if (req.method !== 'GET') return;
  if (new URL(req.url).origin !== self.location.origin) return;
  ev.respondWith(caches.match(req, { ignoreSearch: true }).then(salvo => salvo ||
    fetch(req).catch(() => req.mode === 'navigate' ? caches.match('./index.html') : Response.error())));
});
