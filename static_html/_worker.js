const retiredPaths = new Set(["/games/chess", "/games/dta-6", "/games/epic-mine", "/games/five-nights-at-candys", "/games/five-nights-at-cat-freddy", "/games/granny", "/games/granny-2", "/games/idle-vlogger", "/games/immortal-dark-slayer", "/games/jelly-car-simulator", "/games/obby-but-youre-on-a-bike", "/games/obby-draw-and-jump", "/games/obby-find-100-cats", "/games/obby-find-sprunki", "/games/obby-parkour-lava", "/games/obby-prison-escape", "/games/only-up-obby", "/games/rainbow-obby-parkour", "/games/space-waves", "/games/survival-race", "/games/tb-world", "/games/thief-puzzle", "/games/words-of-wonders"]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '').replace(/\.html$/, '');
    if (!retiredPaths.has(path)) {
      return env.ASSETS.fetch(request);
    }

    const page = await env.ASSETS.fetch(new Request(new URL('/404', url), {method: 'GET'}));
    const headers = new Headers(page.headers);
    headers.set('Cache-Control', 'no-store');
    headers.set('CDN-Cache-Control', 'no-store');
    headers.set('Cloudflare-CDN-Cache-Control', 'no-store');
    headers.set('X-Robots-Tag', 'noindex, follow');
    headers.delete('ETag');
    headers.delete('Age');
    return new Response(request.method === 'HEAD' ? null : page.body, {
      status: 404,
      statusText: 'Not Found',
      headers,
    });
  },
};
