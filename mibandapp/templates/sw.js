let CACHE_STATIC = 'static-v2';
let CACHE_DYNAMIC = 'dynamic-v2';

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_STATIC).then( (cache) => {
            return cache.addAll([
                    '/static/css/main.css',
                    '/static/js/main.js',
                ]);
        }).catch( (err) => {
            console.log('Error opening cache [static]!')
        })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then( (keyList) => {
            return Promise.all(
                keyList.map( function(key) {
                    if( key !== CACHE_STATIC && key !== CACHE_DYNAMIC ){
                        return caches.delete(key);
                    }
                })
            )
        })
    )
    return event.waitUntil( self.clients.claim() );
});

self.addEventListener('fetch', (event) => {
    // console.log(event)
    if ( event.request.url.match(/\.(jpeg|jpg|gif|png|css|js|svg|woff|woff2)$/) ){
        event.respondWith(
            caches.match(event.request).then( function(response){
                if ( response ) {
                    return response;
                } else {
                    return fetch(event.request).then( (res) => {
                        return caches.open(CACHE_DYNAMIC).then( (cache) => {
                            cache.put(event.request.url, res.clone());
                            return res;
                        })
                    }).catch( (err) => {
                        return caches.open(CACHE_STATIC).then( (cache) => {
                            return cache.match('/offline.html');
                        })
                    });
                }
            }).catch( (err) => {
                console.log(err);
            })
        );
    }
});
