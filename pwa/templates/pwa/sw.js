const CACHE_NAME = 'devisys-cache-v1';
const urlsToCache = [
  '/',
  '/devis/creer/', // Votre URL de création de devis
  '/static/AdminLTE/dist/css/AdminLTE.min.css',
  '/static/AdminLTE/bower_components/bootstrap/dist/css/bootstrap.min.css',
  '/static/core/img/logo.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('fetch', event => {
  // Sécurité : Ne pas mettre en cache les pages de l'administration Django
  if (event.request.url.includes('/admin/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
