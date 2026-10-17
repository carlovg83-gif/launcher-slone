// SLONE Global Media Engine — Service Worker (PWA: instalable Smart TV / Móvil / Desktop)
const CACHE = "slone-tv-v4";
const SHELL = [
  "/",
  "/index.html",
  "/tv.html",
  "/tv",
  "/sync_lab.html",
  "/manifest.json",
  "/assets/slone_luxury_logo.svg",
  "/assets/slone_isotipo_soberano.svg",
  "/assets/slone_logo.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL).catch(() => {})).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  // No cachear flujos multimedia pesados o APIs dinámicas en CacheStorage
  if (url.pathname.includes(".m3u8") || 
      url.pathname.includes(".ts") || 
      url.pathname.startsWith("/api/stream") ||
      url.pathname.startsWith("/api/epg")) {
    return;
  }

  // Red primero con respaldo inmediato en caché para la UI
  e.respondWith(
    fetch(req)
      .then((res) => {
        if (res.status === 200) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        }
        return res;
      })
      .catch(() => caches.match(req).then((r) => r || caches.match("/tv.html") || caches.match("/index.html")))
  );
});
