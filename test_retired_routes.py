import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from site_retirements import write_retired_game_routes


class RetirementRouteTests(unittest.TestCase):
    def test_generated_routes_are_limited_to_retired_games_and_allow_replacements(self):
        catalog = json.loads(Path("static_html/all_games.json").read_text())["games"]
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            self.assertEqual(write_retired_game_routes(catalog, directory), 23)
            routes = json.loads(Path(directory, "_routes.json").read_text())["include"]
            self.assertEqual(len(routes), 69)
            self.assertIn("/games/epic-mine", routes)
            self.assertIn("/games/epic-mine.html", routes)
            self.assertIn("/games/epic-mine/", routes)
            self.assertNotIn("/games/thief-puzzle-stick-hero-rescue", routes)
            self.assertNotIn("/*", routes)
            write_retired_game_routes(catalog + [{"slug": "epic-mine"}], directory)
            routes = json.loads(Path(directory, "_routes.json").read_text())["include"]
            self.assertFalse(any(route.startswith("/games/epic-mine") for route in routes))

    def test_reactivated_catalog_removes_the_unused_worker(self):
        manifest = json.loads(Path("retired_games.json").read_text())
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            write_retired_game_routes([], directory)
            active = [{"slug": slug} for slug in manifest["retired_game_slugs"]]
            self.assertEqual(write_retired_game_routes(active, directory), 0)
            self.assertFalse(Path(directory, "_worker.js").exists())
            self.assertFalse(Path(directory, "_routes.json").exists())

    def test_worker_overrides_stale_assets_and_preserves_live_requests(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node.js is required to verify the deployed Worker behavior")
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            write_retired_game_routes([], directory)
            script = r"""
import assert from 'node:assert/strict';
import fs from 'node:fs';
const code = fs.readFileSync(process.argv[1], 'utf8');
const {default: worker} = await import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'));
const calls = [];
const env = {ASSETS: {async fetch(request) {
  calls.push(request);
  const isError = new URL(request.url).pathname === '/404';
  return new Response(isError ? '<h1>Page not found</h1>' : '<h1>Stale game</h1>', {
    status: 200,
    headers: {'Content-Type': 'text/html', 'ETag': 'old', 'Age': '50000', 'Cache-Control': 'public, s-maxage=604800'},
  });
}}};
for (const suffix of ['', '.html', '/']) {
  for (const method of ['GET', 'HEAD']) {
    const request = new Request('https://btwgame.com/games/epic-mine' + suffix + '?source=test', {method, headers: {'If-None-Match': 'old'}});
    const response = await worker.fetch(request, env);
    assert.equal(response.status, 404);
    assert.equal(response.headers.get('Cache-Control'), 'no-store');
    assert.equal(response.headers.get('Cloudflare-CDN-Cache-Control'), 'no-store');
    assert.equal(response.headers.get('X-Robots-Tag'), 'noindex, follow');
    assert.equal(response.headers.get('Age'), null);
    assert.equal(response.headers.get('ETag'), null);
    assert.equal(new URL(calls.at(-1).url).pathname, '/404');
    assert.equal(calls.at(-1).headers.get('If-None-Match'), null);
    assert.equal(await response.text(), method === 'HEAD' ? '' : '<h1>Page not found</h1>');
  }
}
const live = new Request('https://btwgame.com/games/thief-puzzle-stick-hero-rescue');
const response = await worker.fetch(live, env);
assert.equal(calls.at(-1), live);
assert.equal(response.status, 200);
assert.equal(await response.text(), '<h1>Stale game</h1>');
"""
            subprocess.run([node, "--input-type=module", "-e", script, str(Path(directory, "_worker.js"))], check=True)


if __name__ == "__main__":
    unittest.main()
