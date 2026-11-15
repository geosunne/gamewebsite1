import json
import os
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

from catalog_quality import apply_catalog_provenance, is_recent_game, merge_catalog_record
from generate_static_pages import classify_game_category, game_guide, generate_game_page, normalize_game_data, prepare_catalog, save_all_games_json
from site_content_dates import content_hash, seed_content_dates, update_content_dates


class CatalogStatusTests(unittest.TestCase):
    def test_new_window_uses_catalog_date_and_expires_at_fourteen_days(self):
        now = datetime(2026, 11, 15, 10, tzinfo=timezone.utc)
        game = {"catalog_added_at": (now - timedelta(days=14)).isoformat(), "is_new": True, "release_date": now.isoformat()}
        self.assertFalse(is_recent_game(game, now))
        game["catalog_added_at"] = (now - timedelta(days=14) + timedelta(seconds=1)).isoformat()
        self.assertTrue(is_recent_game(game, now))
        game["catalog_added_at"] = (now + timedelta(seconds=1)).isoformat()
        self.assertFalse(is_recent_game(game, now))
        self.assertFalse(is_recent_game({"created_at": now.isoformat(), "is_new": True}, now))

    def test_existing_catalog_date_survives_source_refresh_and_old_alias_flag(self):
        stamp = "2025-09-01T00:00:00Z"
        game = apply_catalog_provenance({"slug": "old", "catalog_added_at": stamp, "created_at": "2026-11-15", "isNew": True})
        self.assertEqual(game["catalog_added_at"], stamp)
        self.assertFalse(game["is_new"])
        self.assertNotIn("isNew", game)

    def test_legacy_date_comes_from_first_committed_page(self):
        with patch('catalog_quality.first_catalog_entries', return_value={"example": ("2025-01-02T00:00:00Z", "abc123")}):
            game = apply_catalog_provenance({"slug": "example", "release_date": "2020-01-01", "created_at": "2026-11-15"})
        self.assertEqual(game["catalog_added_at"], "2025-01-02T00:00:00Z")
        self.assertEqual(game["catalog_added_commit"], "abc123")

    def test_source_date_is_not_an_editorial_review(self):
        guide = game_guide({"slug": "unlisted-test", "source": "crazygames", "content_guide": {
            "reviewed_on": "2026-11-11", "provenance": "Source description and controls",
        }})
        self.assertNotIn("reviewed_on", guide)
        self.assertEqual(guide["source_checked_on"], "2026-11-11")

    def test_newer_provider_facts_are_not_reverted_by_an_older_audit(self):
        with patch('generate_static_pages.FACT_CHECKS', {'fresh-test': {
            'source_checked_at':'2026-11-11T00:00:00Z', 'controls':{'Controls':'Old instructions'},
            'player_checked_at':'2026-11-10T00:00:00Z', 'player_check_scope':'Startup only',
        }}):
            game=normalize_game_data({'slug':'fresh-test','source_checked_at':'2026-11-15T00:00:00Z','controls':{'Controls':'Current source instructions'},'player_checked_at':'2026-11-16T00:00:00Z','player_check_scope':'Newer startup observation'})
        self.assertEqual(game['controls']['Controls'],'Current source instructions')
        self.assertEqual(game['source_checked_at'],'2026-11-15T00:00:00Z')
        self.assertEqual(game['player_check_scope'],'Newer startup observation')

    def test_older_source_file_cannot_revert_snapshot_facts_or_observations(self):
        old={'source_checked_at':'2026-11-20T00:00:00Z','source_check_status':'confirmed','controls':{'Controls':'Current'},
             'player_checked_at':'2026-11-22T00:00:00Z','player_check_scope':'Latest startup',
             'catalog_added_at':'2025-01-01T00:00:00Z','thumbnail_url':'/assets/thumbnails/current.webp'}
        extra={'source_checked_at':'2026-11-15T00:00:00Z','source_check_status':'unconfirmed','content_status':'needs_review','source_check_reason':'Old failure','controls':{'Controls':'Stale'},
               'player_checked_at':'2026-11-16T00:00:00Z','player_check_scope':'Older startup',
               'catalog_added_at':'2026-11-15T00:00:00Z','thumbnail_url':'https://example.com/remote.webp'}
        merged=merge_catalog_record(old,extra)
        self.assertEqual(merged['controls'],old['controls'])
        self.assertEqual(merged['source_checked_at'],old['source_checked_at'])
        self.assertEqual(merged['player_check_scope'],'Latest startup')
        self.assertEqual(merged['catalog_added_at'],old['catalog_added_at'])
        self.assertEqual(merged['thumbnail_url'],old['thumbnail_url'])
        self.assertNotIn('content_status',merged)
        self.assertNotIn('source_check_reason',merged)

    def test_new_confirmed_instructions_clear_an_older_pending_record(self):
        old={'content_status':'needs_review','source_check_status':'unconfirmed',
             'source_check_attempted_at':'2026-11-15T00:00:00Z','source_check_reason':'Missing record','controls':{}}
        extra={'source_check_status':'confirmed','source_checked_at':'2026-11-20T00:00:00Z','controls':{'Controls':'New source instructions'}}
        merged=merge_catalog_record(old,extra)
        self.assertNotIn('content_status',merged)
        self.assertNotIn('source_check_reason',merged)
        self.assertEqual(merged['controls'],extra['controls'])

    def test_arcade_description_is_not_overridden_by_worlds(self):
        game = {"slug": "space-waves-test", "title": "Space Waves", "description": "An arcade game across multiple worlds.", "category_name": "Casual"}
        self.assertEqual(classify_game_category(game), "Arcade")
        self.assertEqual(classify_game_category({"title":"Robbie", "description":"A simulation game inside an arcade world."}), "Simulation")

    def test_browser_new_rule_matches_python_boundary(self):
        node = shutil.which("node")
        self.assertIsNotNone(node)
        script = r"""
const fs = require('node:fs'); const vm = require('node:vm');
const context = {window:{},document:{readyState:'loading',addEventListener(){}},Date};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'), context);
const recent=context.window.BTWCatalogStatus.isRecent;
const now=Date.parse('2026-11-15T10:00:00Z');
for (const [stamp,expected] of [['2026-11-01T10:00:00Z',false],['2026-11-01T10:00:01Z',true],['2026-11-16T00:00:00Z',false],['',false]]) {
 if(recent({catalog_added_at:stamp},now)!==expected) throw Error('NEW boundary: '+stamp);
}
"""
        subprocess.run([node, '-e', script, str(Path('static/assets/js/catalog-status.js').resolve())], check=True)

    def test_empty_new_catalog_does_not_substitute_old_games(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory(dir=previous) as directory:
            try:
                os.chdir(directory)
                Path('static_html').mkdir()
                self.assertTrue(save_all_games_json([{"slug": "old", "is_new": False}]))
                self.assertEqual(json.loads(Path('static_html/new_games.json').read_text())["games"], [])
            finally:
                os.chdir(previous)

    def test_unconfirmed_controls_are_visible_without_guessed_mechanics(self):
        game = prepare_catalog([{
            "slug": "unconfirmed-example", "title": "Example", "description": "Source listing",
            "category_name": "Puzzle", "content_status": "needs_review", "controls": {},
            "source_check_status": "unconfirmed", "source_check_attempted_at": "2026-11-15T00:00:00Z",
            "content_guide": {"how_to": "Invented secret action", "tips": ["Invented strategy"]},
        }])[0]
        text = BeautifulSoup(generate_game_page(game, []), 'html.parser').get_text(' ', strip=True)
        self.assertIn("awaiting confirmation", text)
        self.assertIn("Not confirmed from the source listing", text)
        self.assertIn("No separate review record", text)
        self.assertNotIn("Invented secret action", text)
        self.assertNotIn("Invented strategy", text)

    def test_legacy_api_adapter_filters_stale_and_future_new_flags(self):
        script = r"""
const {GameDataAdapter}=require(process.argv[1]);
Date.now=()=>Date.parse('2026-11-15T10:00:00Z');
const adapter=new GameDataAdapter();
adapter.getStaticGames=async()=>[
 {slug:'old',catalog_added_at:'2026-11-01T10:00:00Z',is_new:true},
 {slug:'recent',catalog_added_at:'2026-11-10T10:00:00Z',is_new:false},
 {slug:'future',catalog_added_at:'2026-11-16T10:00:00Z',is_new:true}
];
adapter.getStaticGamesList({new:true}).then(games=>{
 if(games.length!==1||games[0].slug!=='recent'||games[0].isNew!==true) throw Error('adapter NEW status mismatch');
}).catch(error=>{console.error(error);process.exitCode=1});
"""
        subprocess.run([shutil.which('node'),'-e',script,str(Path('static/assets/js/api.js').resolve())],check=True)


class ContentDateTests(unittest.TestCase):
    def make_site(self, root):
        (root/'games').mkdir()
        page = root/'games/example.html'
        page.write_text('''<!doctype html><html><head><script type="application/ld+json">{"@type":"WebPage","dateModified":"2026-11-01"}</script></head><body><h1>Example</h1><p>Original fact</p><time data-check-timestamp datetime="2026-11-01">2026-11-01</time><time data-page-updated datetime="2026-11-01">2026-11-01</time></body></html>''')
        (root/'sitemap.xml').write_text('<urlset><url><loc>https://btwgame.com/games/example</loc><lastmod>2026-11-01</lastmod></url></urlset>')
        (root/'all_games.json').write_text('{"games":[{"slug":"example"}]}')
        return page

    def test_real_changes_update_dates_but_build_time_and_check_time_do_not(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory);page=self.make_site(root)
            seed_content_dates(root)
            first = update_content_dates(root, datetime(2026,11,15,tzinfo=timezone.utc))
            self.assertEqual(first['/games/example'], '2026-11-01')
            page.write_text(page.read_text().replace('Original fact','Corrected fact'))
            changed = update_content_dates(root, datetime(2026,11,15,tzinfo=timezone.utc))
            self.assertEqual(changed['/games/example'], '2026-11-15')
            before=(root/'content_dates.json').read_bytes()
            again=update_content_dates(root, datetime(2026,11,16,tzinfo=timezone.utc))
            self.assertEqual(changed, again)
            self.assertEqual(before,(root/'content_dates.json').read_bytes())
            page.write_text(page.read_text().replace('2026-11-01','2026-11-16'))
            self.assertEqual(update_content_dates(root,datetime(2026,11,17,tzinfo=timezone.utc)),changed)
            soup=BeautifulSoup(page.read_text(),'html.parser')
            self.assertEqual(json.loads(soup.script.string)['dateModified'],'2026-11-15')
            self.assertEqual(soup.select_one('[data-page-updated]').get_text(),'2026-11-15')
            self.assertEqual(json.loads((root/'all_games.json').read_text())['games'][0]['content_modified_at'],'2026-11-15')

    def test_missing_prior_dates_are_initialized_once(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root=Path(directory);(root/'index.html').write_text('<h1>New site</h1>')
            self.assertEqual(update_content_dates(root,datetime(2026,11,15,tzinfo=timezone.utc))['/'],'2026-11-15')
            self.assertEqual(update_content_dates(root,datetime(2026,11,19,tzinfo=timezone.utc))['/'],'2026-11-15')

    def test_schema_date_is_excluded_but_source_facts_are_not(self):
        first='<script type="application/ld+json">{"@type":"WebPage","dateModified":"2026-01-01","name":"A"}</script>'
        self.assertEqual(content_hash(first),content_hash(first.replace('2026-01-01','2026-11-15')))
        self.assertNotEqual(content_hash(first),content_hash(first.replace('"A"','"B"')))


if __name__ == '__main__':
    unittest.main()
