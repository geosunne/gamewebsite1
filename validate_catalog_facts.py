"""Validate catalog identity, explicit fact status, content dates and publication."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

from catalog_quality import is_recent_game


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sitemap_urls(raw):
    return [node.text for node in ET.fromstring(raw).findall('{*}url/{*}loc')]


def check_game_page(raw, game, modified):
    soup = BeautifulSoup(raw, 'lxml')
    canonical = soup.find('link', rel='canonical')
    require(canonical and canonical.get('href') == f"https://btwgame.com/games/{game['slug']}", f"canonical: {game['slug']}")
    schemas = [json.loads(s.string) for s in soup.select('script[type="application/ld+json"]')]
    entity = next(x for x in schemas if x.get('@type') == 'VideoGame')
    page = next(x for x in schemas if x.get('@type') == 'WebPage')
    require(entity['genre'] == game['category_name'], f"category: {game['slug']}")
    require(page.get('dateModified') == modified, f"schema date: {game['slug']}")
    require(soup.select_one('[data-page-updated]').get_text() == modified, f"visible date: {game['slug']}")
    text = ' '.join(soup.stripped_strings)
    require('Listing notes reviewed:' not in text, f"legacy automatic review label: {game['slug']}")
    require(len(soup.find_all('h1')) == 1, f"H1: {game['slug']}")
    if not game.get('controls'):
        require('awaiting confirmation' in text.lower() or 'not been confirmed' in text.lower(), f"missing control notice: {game['slug']}")
    if game.get('content_status') == 'needs_review':
        require('Source instructions awaiting confirmation' in text, f"pending source notice: {game['slug']}")
    if game.get('player_checked_at'):
        require(game['player_check_scope'] in text, f"player scope: {game['slug']}")
    faq = next(x for x in schemas if x.get('@type') == 'FAQPage')
    require([x['name'] for x in faq['mainEntity']] == [x.get_text() for x in soup.select('.faq-item summary')], f"FAQ: {game['slug']}")


def local_audit(baseline, audit):
    root = Path('static_html')
    games = json.loads((root/'all_games.json').read_text())['games']
    require(len(games) == baseline['game_count'], 'catalog size changed')
    rows = sorted([{key:g.get(key) for key in baseline['identity_fields']} for g in games], key=lambda x:x['slug'])
    digest = hashlib.sha256(json.dumps(rows,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    require(digest == baseline['identities_sha256'], 'game identities or addresses changed')
    by_slug = {g['slug']:g for g in games}
    require(len(by_slug) == len(games), 'duplicate slugs')
    require({p.stem for p in (root/'games').glob('*.html')} == set(by_slug), 'game page inventory mismatch')
    dates = json.loads((root/'content_dates.json').read_text())['pages']
    urls = sitemap_urls((root/'sitemap.xml').read_bytes())
    require(urls == (root/'sitemap.txt').read_text().splitlines() and len(set(urls)) == len(urls), 'sitemap mismatch')
    for node in ET.parse(root/'sitemap.xml').getroot().findall('{*}url'):
        path = node.find('{*}loc').text.removeprefix('https://btwgame.com')
        require(node.find('{*}lastmod').text == dates[path]['lastmod'], 'sitemap content date: '+path)
    for game in games:
        require(bool(game['is_new']) == is_recent_game(game), 'NEW window: '+game['slug'])
        check_game_page((root/'games'/f"{game['slug']}.html").read_text(),game,dates['/games/'+game['slug']]['lastmod'])
    require({g['slug'] for g in json.loads((root/'new_games.json').read_text())['games']} == {g['slug'] for g in games if g['is_new']}, 'new_games.json mismatch')
    links = 0
    for file in root.rglob('*.html'):
        soup = BeautifulSoup(file.read_text(),'lxml')
        for node in soup.select('a[href],link[href],script[src],img[src]'):
            url=urlsplit(urljoin('https://btwgame.com/'+file.relative_to(root).as_posix(),node.get('href') or node['src']))
            if url.netloc not in {'btwgame.com','www.btwgame.com'} or url.scheme not in {'http','https'}:
                continue
            target=root/unquote(url.path).lstrip('/')
            require(target.is_file() or (target/'index.html').is_file() or Path(str(target)+'.html').is_file(), f"internal link: {file} -> {url.path}")
            links+=1
    require(len(audit['selection']['priority']) == 20 and len(audit['selection']['pending']) == 19, 'source audit selection mismatch')
    for row in audit['results']:
        game=by_slug[row['slug']]
        require(game['source_check_status']==row['status'],'source check status: '+game['slug'])
        if row['group']=='priority20':
            require(game.get('controls'),'priority controls missing: '+game['slug'])
    return games, dates, {'total_games':len(games),'new_games':sum(g['is_new'] for g in games),'pending_source_records':sum(g.get('content_status')=='needs_review' for g in games),'source_records_checked':len(audit['results']),'priority_sources_confirmed':20,'sitemap_urls':len(urls),'internal_references_checked':links,'identity_digest':digest}


def online_audit(base, games, dates, audit):
    base=base.rstrip('/')
    def get(path):
        r=requests.get(base+path,timeout=30)
        require(r.status_code==200,f"online HTTP {r.status_code}: {path}")
        return r
    require(get('/all_games.json').json()['games']==games,'online catalog does not match publication')
    require(get('/content_dates.json').json()['pages']==dates,'online date manifest mismatch')
    require(get('/new_games.json').json()['games']==json.loads(Path('static_html/new_games.json').read_text())['games'],'online new list mismatch')
    xml=get('/sitemap.xml').content;txt=get('/sitemap.txt').text
    require(sitemap_urls(xml)==txt.splitlines()==sitemap_urls(Path('static_html/sitemap.xml').read_bytes()),'online sitemap mismatch')
    by_slug={g['slug']:g for g in games}
    def check(slug):
        r=get('/games/'+slug);check_game_page(r.text,by_slug[slug],dates['/games/'+slug]['lastmod'])
        return {'slug':slug,'status':r.status_code,'canonical':'https://btwgame.com/games/'+slug}
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(check,[row['slug'] for row in audit['results']]))
    home=BeautifulSoup(get('/').text,'lxml')
    require('Games players open most often.' not in home.get_text(),'old popularity claim remains online')
    policy=get('/editorial-policy').text
    require('not a directly comparable count' in policy and 'last 14 days' in policy,'online editorial policy mismatch')
    return {'base_url':base,'catalog_count':len(games),'target_pages_checked':len(results),'sitemap_urls':len(sitemap_urls(xml)),'results':results}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',required=True);p.add_argument('--source-audit',required=True);p.add_argument('--output',required=True);p.add_argument('--online')
    args=p.parse_args();baseline=json.loads(Path(args.baseline).read_text());audit=json.loads(Path(args.source_audit).read_text())
    games,dates,report=local_audit(baseline,audit)
    if args.online:report['online']=online_audit(args.online,games,dates,audit)
    report['checked_at']=datetime.now(timezone.utc).isoformat(timespec='seconds')
    Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='online'},ensure_ascii=False))
    if args.online:print(json.dumps({k:v for k,v in report['online'].items() if k!='results'},ensure_ascii=False))


if __name__=='__main__':main()
