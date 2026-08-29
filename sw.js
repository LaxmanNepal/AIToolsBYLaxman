const CACHE='ai-tools-v5';
const CORE=['/','/index.html','/manifest.json','/icon.svg','/tools/index.json'];
const STATIC=/\.(?:css|js|svg|png|jpg|jpeg|webp|ico)$/i;

self.addEventListener('install',event=>event.waitUntil((async()=>{
  const cache=await caches.open(CACHE);
  await Promise.all(CORE.map(async url=>{try{await cache.add(url)}catch(_){}}));
  await self.skipWaiting();
})()));

self.addEventListener('activate',event=>event.waitUntil((async()=>{
  const keys=await caches.keys();
  await Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)));
  await self.clients.claim();
})()));

self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET'||new URL(event.request.url).origin!==location.origin)return;
  const url=new URL(event.request.url);
  if(url.pathname==='/tools/index.json'){
    event.respondWith((async()=>{try{const response=await fetch(event.request,{cache:'no-store'});if(response.ok)await caches.open(CACHE).then(c=>c.put(event.request,response.clone()));return response}catch(_){return caches.match(event.request)}})());
    return;
  }
  if(STATIC.test(url.pathname)||url.pathname==='/'||url.pathname==='/index.html'){
    event.respondWith((async()=>{const cached=await caches.match(event.request);if(cached)return cached;try{const response=await fetch(event.request);if(response.ok)await caches.open(CACHE).then(c=>c.put(event.request,response.clone()));return response}catch(_){return cached}})());
  }
});
