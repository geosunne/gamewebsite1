"""Regression checks for CSS Grid spans and complete homepage shelves."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path


class HomeGridTests(unittest.TestCase):
    def node(self, source):
        node = shutil.which('node')
        self.assertIsNotNone(node)
        path = str(Path('static/assets/js/home-grid.js').resolve())
        result = subprocess.check_output([node, '-e', source, path], text=True)
        return json.loads(result)

    def test_span_reads_both_sides_of_css_shorthand(self):
        result = self.node("""
const {span}=require(process.argv[1]);
console.log(JSON.stringify([span('span 2','auto'),span('auto','span 3'),span('auto','auto')]));
""")
        self.assertEqual(result, [2, 3, 1])

    def test_complete_prefix_accounts_for_featured_cards_and_sparse_last_rows(self):
        result = self.node("""
const {completePrefix}=require(process.argv[1]);
const hot=Array.from({length:32},(_,i)=>i===0||i===7?{columns:2,rows:2}:{columns:1,rows:1});
const normal=n=>Array.from({length:n},()=>({columns:1,rows:1}));
console.log(JSON.stringify({
 hot:[2,3,4,5,6,7,8,9].map(c=>completePrefix(hot,c)),
 regular:[completePrefix(normal(24),9),completePrefix(normal(36),8),completePrefix(normal(14),8)],
 lateFeature:completePrefix([...normal(7),{columns:2,rows:2}],4),
 empty:completePrefix([],8)
}));
""")
        self.assertEqual(result['hot'], [32, 30, 30, 29, 30, 29, 26, 30])
        self.assertEqual(result['regular'], [18, 32, 8])
        self.assertEqual(result['lateFeature'], 4)
        self.assertEqual(result['empty'], 0)


if __name__ == '__main__':
    unittest.main()
