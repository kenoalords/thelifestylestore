let CACHE_STATIC = 'static-v6.1';
let CACHE_DYNAMIC = 'dynamic-v2';

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_STATIC).then( (cache) => {
            return cache.addAll([
                '/static/css/main.css',
                '/static/js/main.js',
                '/static/images/the-lifestyle-shop.logo.svg',
                '/static/images/shopping-basket-solid.svg',
                '/static/images/instagram.svg',
                '/static/images/menu-options.svg',
                '/static/images/telephone.svg',
                '/static/images/twitter.svg',
                '/static/images/proposition-img-0.svg',
                '/static/images/proposition-img-3.svg',
                '/static/images/shopping-basket-solid-white.svg',
                '/static/images/heart-solid.svg',
                '/offline.html',
                '/static/images/locked.svg',
                '/static/images/the-lifestyle-shop.logo-white.svg',
                '/static/images/paystack-cards-white.png',
                '/static/images/signup-background.jpg'
            ]);
        }).catch( (err) => {
            console.log(err)
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
    // if ( event.request.url.match(/\.(jpeg|jpg|gif|png|css|js|svg|woff|woff2)$/) ){
    //
    // } else {
    //     event.respondWith(
    //
    //     )
    // }
    event.respondWith(
        caches.match(event.request).then( function(response){
            if ( response ) {
                return response;
            } else {
                return fetch(event.request).then( (res) => {
                    if ( event.request.url.match(/\.(jpeg|jpg|gif|png|css|js|svg|woff|woff2)$/) ){
                        return caches.open(CACHE_STATIC).then( (cache) => {
                            cache.put(event.request.url, res.clone());
                            return res;
                        }).catch((err)=>{
                            console.log(err)
                        })
                    } else {
                        return res;
                    }
                }).catch( (err) => {
                    return caches.open(CACHE_STATIC).then( (cache) => {
                        return cache.match('/offline.html');
                    })
                });
            }
        }).catch( (err) => {
            return cache.match('/offline.html');
        })
    );
});

// Listen for notification clicks
self.addEventListener('notificationclick', function(e){
    var notification = e.notification;
    var action = e.action;
});

self.addEventListener('notificationclose', function(e){
    var notification = e.notification;
})

self.addEventListener('push', function(event){
    console.log(event);
});
