"""Generate narrowly scoped Cloudflare Pages routes for retired game URLs."""
import json
import re
from pathlib import Path


WORKER_SOURCE = """const retiredPaths = new Set(__RETIRED_PATHS__);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\\/+$/, '').replace(/\\.html$/, '');
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
"""


def write_retired_game_routes(games, output_dir="static_html", manifest_path=None):
    manifest_path = Path(manifest_path) if manifest_path else Path(__file__).with_name("retired_games.json")
    retired = json.loads(manifest_path.read_text(encoding="utf-8"))["retired_game_slugs"]
    if any(not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) for slug in retired):
        raise ValueError("Retired game slugs must be literal game identifiers")
    active = {game["slug"] for game in games}
    paths = sorted(f"/games/{slug}" for slug in set(retired) - active)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if not paths:
        for name in ("_worker.js", "_routes.json"):
            (output_dir / name).unlink(missing_ok=True)
        return 0
    routes = [path + suffix for path in paths for suffix in ("", ".html", "/")]
    if len(routes) > 100 or any(len(route) > 100 for route in routes):
        raise ValueError("Retired game routes exceed Cloudflare Pages invocation limits")
    (output_dir / "_worker.js").write_text(
        WORKER_SOURCE.replace("__RETIRED_PATHS__", json.dumps(paths)), encoding="utf-8"
    )
    (output_dir / "_routes.json").write_text(
        json.dumps({"version": 1, "include": routes, "exclude": []}, indent=2) + "\n", encoding="utf-8"
    )
    return len(paths)
