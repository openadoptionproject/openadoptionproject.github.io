"""Refreshes feed.json from the podcast's RSS feed. Keeps the old file if the feed can't be read."""
import json, re, sys, html, urllib.request, xml.etree.ElementTree as ET
URL = 'https://media.rss.com/openadoptionproject/feed.xml'
IT = '{http://www.itunes.com/dtds/podcast-1.0.dtd}'
def text(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    return html.unescape(s).strip()
try:
    req = urllib.request.Request(URL, headers={'User-Agent': 'OAP-site-builder'})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=60).read())
except Exception as e:
    print('Feed not reachable, keeping existing feed.json:', e); sys.exit(0)
ch = root.find('channel')
old = json.load(open('feed.json'))
img = ch.find(IT + 'image')
out = {'title': ch.findtext('title'), 'img': img.get('href') if img is not None else old['img'],
       'desc': ch.findtext('description') or old['desc'], 'items': []}
for i in ch.findall('item'):
    enc = i.find('enclosure'); im = i.find(IT + 'image')
    dur = i.findtext(IT + 'duration') or ''
    if ':' in dur:
        p = [int(x) for x in dur.split(':')]; dur = str(sum(v * 60 ** k for k, v in enumerate(reversed(p))))
    out['items'].append({'n': (i.findtext(IT + 'episode') or '').strip(), 't': text(i.findtext('title')),
        'link': i.findtext('link'), 'date': i.findtext('pubDate'), 'dur': dur,
        'mp3': enc.get('url') if enc is not None else '', 'img': im.get('href') if im is not None else '',
        'type': i.findtext(IT + 'episodeType') or 'full', 'season': i.findtext(IT + 'season') or '',
        'desc': text(i.findtext('description'))})
if len(out['items']) < len(old['items']):
    print('Feed has fewer episodes than before; keeping existing feed.json'); sys.exit(0)
json.dump(out, open('feed.json', 'w'), ensure_ascii=False, indent=1)
print('feed.json updated:', len(out['items']), 'items')
