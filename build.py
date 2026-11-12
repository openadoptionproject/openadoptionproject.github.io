#!/usr/bin/env python3
"""Builds the Open Adoption Project website into dist/ from feed.json (+ transcripts and quotes).
Run: python3 build.py   (re-run after refreshing feed.json to add new episodes)"""
import json, re, os, html, shutil, datetime, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
TX_DIR = os.path.join(ROOT, 'data', 'transcripts')
SITE = 'https://www.openadoptionproject.org'
APPLE = 'https://podcasts.apple.com/podcast/id1561566796'
SPOTIFY = 'https://open.spotify.com/show/2pcOqcQTlVX3OM8f8YkgiV'
RSSCOM = 'https://rss.com/podcasts/openadoptionproject/'
IG = 'https://www.instagram.com/openadoptionproject/'
FB = 'https://www.facebook.com/theopenadoptionproject'
EMAIL = 'openadoptionproject@gmail.com'
AMAZON = 'https://www.amazon.com/dp/B0F3X12V2X'
GUM_OPENNESS = 'https://openadoption.gumroad.com/l/opa'
GUM_SUBSTANCE = 'https://openadoption.gumroad.com/l/tlrxt'
e = lambda s: html.escape(str(s), quote=True)

F = json.load(open(os.path.join(ROOT, 'feed.json')))
TAGS = ['Adoptee voices', 'Birth parents', 'Openness 101', 'Research & practice', 'Identity & culture', 'Parenting & family', 'Book club']

def tag_for(t, d):
    tl, dl = t.lower(), d.lower()
    if 'book club' in tl: return 'Book club'
    sc = {
      'Adoptee voices': 2*len(re.findall(r'\badoptee\b', tl)) + len(re.findall(r'\b(an|as an|is an|fellow) adoptee|was adopted|adopted (at|as|in|from|out)|adoptees? (share|perspectives)|reunion|dna', dl)),
      'Birth parents': 2*len(re.findall(r'birth mom|birth mother|birth father|first mother', tl)) + len(re.findall(r'(a|as a|is a) birth (mom|mother|father|parent)|placing her|placed (her|his|my) (son|daughter|baby)|placement decision|expectant', dl)),
      'Openness 101': 2*len(re.findall(r'open adoption|openness|boundar|communication', tl)) + len(re.findall(r'open adoption|openness|boundar', dl)) * 0.5,
      'Research & practice': 2*len(re.findall(r'professor|dr\.|scholarly|trauma|attachment|history|grief|suicid|psychological|legal|ethic|professional', tl)) + len(re.findall(r'professor|research|therap|social worker|attorney|psycholog|trauma', dl)) * 0.6,
      'Identity & culture': 2*len(re.findall(r'racial|international|cultur|representation|juneteenth|madagascar|inclusiv|special needs|foster|children in care', tl)) + len(re.findall(r'transracial|international|culture|racial|foster', dl)) * 0.6,
    }
    best = max(sc, key=sc.get)
    return best if sc[best] >= 1 else 'Parenting & family'

def fmt_date(s):
    try: return datetime.datetime.strptime(s[:16], '%a, %d %b %Y').strftime('%b %-d, %Y')
    except Exception: return s

def mins(d):
    try: return f"{round(int(float(d))/60)} min"
    except Exception: return ''

TX_JSON = os.path.join(ROOT, 'data', 'transcripts.json')
TX_ALL = json.load(open(TX_JSON)) if os.path.exists(TX_JSON) else {}

def tx_for(link):
    eid = link.rstrip('/').split('/')[-1]
    f = glob.glob(f'{TX_DIR}/E*_{eid}.txt') + glob.glob(f'{TX_DIR}/ES_{eid}.txt')
    raw = open(f[0]).read() if f else TX_ALL.get(eid, '')
    out = []
    for l in raw.splitlines():
        m = re.match(r'\[(\d+:\d+(?::\d+)?)\] (.*)', l)
        if m: out.append((m[1], m[2].strip()))
    return out

# quotes from social posts and reels (verbatim-verified)
QUOTES = {}
try:
    for p in json.load(open(os.path.join(ROOT, 'data', 'posts.json'))):
        if p['type'] == 'quote' and p.get('speaker') not in ('Lanette & Shaun',):
            QUOTES.setdefault(p['ep'], []).append((p['display'], p['speaker'], p.get('role', '')))
except Exception: pass

EPS = []
for it in F['items']:
    n = it['n'].strip()
    eid = it['link'].rstrip('/').split('/')[-1]
    slug = n if n else f"special-{eid}"
    EPS.append(dict(n=n, slug=slug, title=it['t'], date=fmt_date(it['date']), dur=mins(it['dur']), mp3=it['mp3'], link=it['link'],
                    desc=re.sub(r'([a-z0-9][.!?])([A-Z])', r'\1 \2', it['desc']), tag=tag_for(it['t'], it['desc']), eid=eid))
NUM = [x for x in EPS if x['n']]
NUM.sort(key=lambda x: -int(x['n']))
SPECIAL = [x for x in EPS if not x['n']]
BY = {x['n']: x for x in NUM}
COUNT = max(int(x['n']) for x in NUM)
LATEST = NUM[0]

def ep_url(n, pre=''):
    return f"{pre}episodes/{n}.html"

ICON = {
 'play': '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4v16l13-8z"/></svg>',
 'head': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1v-6h3zM3 19a2 2 0 0 0 2 2h1v-6H3z"/></svg>',
 'person': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/></svg>',
 'heart': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.5 1-1.1a5.5 5.5 0 0 0 0-7.8z"/></svg>',
 'home': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/></svg>',
 'book': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
 'search': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
 'menu': '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
}

def page(title, desc, body, active='', pre='', canon=''):
    nav = [('start-here.html', 'Start Here'), ('episodes.html', 'Episodes'), ('resources.html', 'Resources'), ('about.html', 'About')]
    links = ''.join(f'<a href="{pre}{h}"{" aria-current=page" if h == active else ""}>{t}</a>' for h, t in nav)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{e(F['img'])}">
<link rel="canonical" href="{SITE}/{canon}">
<link rel="icon" href="{e(F['img'])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-h"><div class="wrap">
<a class="logo" href="{pre}index.html"><span class="dot"></span>Open Adoption Project</a>
<nav class="nav" id="nav" aria-label="Main">{links}</nav>
<div style="display:flex;gap:10px;align-items:center">
<a class="btn sage h-listen" href="{pre}index.html#listen" style="min-height:44px;padding:0 20px;font-size:16px">{ICON['head']}Listen</a>
<button class="menu-btn" aria-label="Menu" aria-controls="nav" aria-expanded="false">{ICON['menu']}</button>
</div>
</div></header>
<main id="main">
{body}
</main>
<footer class="site-f">
<div class="wrap g4 cols">
<div class="stack" style="gap:14px"><span class="logo" style="font-size:15px"><span class="dot" style="width:12px;height:12px;flex-basis:12px"></span>Open Adoption Project</span><span class="serif small" style="line-height:1.6">A community for listening, learning and building respectful relationships across the adoption constellation.</span></div>
<nav aria-label="Listen"><span class="k">Listen</span><a href="{APPLE}">Apple Podcasts</a><a href="{SPOTIFY}">Spotify</a><a href="{RSSCOM}">RSS.com</a></nav>
<nav aria-label="Explore"><span class="k">Explore</span><a href="{pre}start-here.html">Start Here</a><a href="{pre}episodes.html">All episodes</a><a href="{pre}resources.html">Resources</a><a href="{pre}about.html">About</a></nav>
<nav aria-label="Connect"><span class="k">Connect</span><a href="{IG}">Instagram</a><a href="{FB}">Facebook</a><a href="mailto:{EMAIL}">{EMAIL}</a><a href="{pre}about.html#contact">Contact us</a></nav>
</div>
<div class="wrap base">© {datetime.date.today().year} The Open Adoption Project</div>
</footer>
<script src="{pre}assets/app.js"></script>
</body>
</html>'''

def ep_card(n, tagline, pre=''):
    x = BY[str(n)]
    short = re.split(r'(?<=[.!?])\s', x['desc'])[0][:170] if x['desc'] else ''
    return f'''<a class="card" href="{ep_url(n, pre)}">
<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><span class="epn">EP. {n}</span><span class="tag">{e(tagline or x['tag'])}</span></div>
<h3 class="h3">{e(x['title'])}</h3>
<p class="serif muted" style="font-size:16px;line-height:1.55">{e(short)}</p>
<span style="margin-top:auto;display:inline-flex;align-items:center;gap:8px;color:var(--leaf);font-weight:600;font-size:15px">{ICON['play']}Listen · {e(x['dur'])}</span>
</a>'''

def listen_chips(dark=True, ep_link=None):
    return f'''<div class="chiprow">
<a class="chip" href="{APPLE}">Apple Podcasts</a><a class="chip" href="{SPOTIFY}">Spotify</a><a class="chip" href="{ep_link or RSSCOM}">RSS.com</a></div>'''

def tl(n, pre=''):
    x = BY[str(n)]
    return f'<a href="{ep_url(n, pre)}">Ep. {n} · {e(x["title"])}</a>'

# ---------------- HOME ----------------
home = f'''
<section class="dark"><div class="wrap split hero">
<div class="stack" style="gap:28px">
<span class="pill sage" style="align-self:flex-start">The podcast · {COUNT} episodes</span>
<h1 class="h1">Adoption conversations, centered on <em style="color:var(--sage)">adoptee voices.</em></h1>
<p class="lead" style="margin:0;color:var(--mist);max-width:600px">Since 2021, Lanette and Shaun Nelson have been listening to adoptees, birth parents, adoptive families and researchers to learn what openness really looks like, and how to do it well.</p>
<div class="chiprow"><a class="btn leaf" href="start-here.html">Start here</a><a class="btn line" href="episodes.html" style="color:var(--cream);border-color:var(--sage)">Browse episodes</a></div>
<div id="listen" style="display:flex;align-items:center;gap:12px;flex-wrap:wrap"><span class="small" style="font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--sage)">Listen free on</span>{listen_chips()}</div>
</div>
<a class="feat" href="{ep_url(LATEST['n'])}">
<div style="display:flex;justify-content:space-between;align-items:center;gap:12px"><span style="font-weight:600;font-size:13px;letter-spacing:.12em;text-transform:uppercase">Newest episode · {e(LATEST['date'])}</span><span class="epn" style="border-width:3px">EP. {LATEST['n']}</span></div>
<p class="q" style="margin:0">{e(LATEST['title'])}</p>
<p class="serif" style="margin:0;font-size:17px;line-height:1.55">{e(re.split(r'(?<=[.!?])\s', LATEST['desc'])[0][:220])}</p>
<span class="btn ink" style="align-self:flex-start;min-height:44px;font-size:16px">{ICON['play']}Play episode</span>
</a>
</div></section>

<section class="sec"><div class="wrap">
<div class="stack" style="gap:12px;max-width:720px;margin-bottom:44px"><h2 class="h2">Where would you like to start?</h2>
<p class="lead muted" style="margin:0">Everyone is welcome here. Wherever you sit in the adoption constellation, we hope you’ll start by listening to adoptees.</p></div>
<div class="g4">
<div class="card"><span class="icon">{ICON['person']}</span><h3 style="font-size:22px;font-weight:600">I’m an adoptee</h3><p class="serif muted" style="font-size:16px;line-height:1.55">Adoptees of every age on identity, search, reunion and belonging.</p><div class="stack small" style="gap:8px;margin-top:auto;font-weight:500">{tl(95)}{tl(120)}</div></div>
<div class="card"><span class="icon">{ICON['heart']}</span><h3 style="font-size:22px;font-weight:600">I’m a birth parent</h3><p class="serif muted" style="font-size:16px;line-height:1.55">Birth parents share their stories, and what child-centered openness can look like.</p><div class="stack small" style="gap:8px;margin-top:auto;font-weight:500">{tl(105)}{tl(69)}</div></div>
<div class="card"><span class="icon">{ICON['home']}</span><h3 style="font-size:22px;font-weight:600">I’m an adoptive or hopeful parent</h3><p class="serif muted" style="font-size:16px;line-height:1.55">What openness asks of you, why it matters for your child, and how to keep it going.</p><div class="stack small" style="gap:8px;margin-top:auto;font-weight:500">{tl(67)}{tl(80)}</div></div>
<div class="card"><span class="icon">{ICON['book']}</span><h3 style="font-size:22px;font-weight:600">I work with families</h3><p class="serif muted" style="font-size:16px;line-height:1.55">Research, language and practice for social workers, therapists and agencies.</p><div class="stack small" style="gap:8px;margin-top:auto;font-weight:500">{tl(85)}{tl(58)}</div></div>
</div></div></section>

<section class="sagebg"><div class="wrap split sec">
<div class="stack" style="gap:22px">
<span class="pill" style="align-self:flex-start">Openness 101</span>
<h2 class="h2">Open adoption is more than visits.</h2>
<p class="lead" style="margin:0">Openness has two sides, and adoptees need both. You can’t always control contact. You can always keep the conversation open.</p>
<div class="g2" style="gap:16px">
<div class="card" style="background:var(--cream);border:0;gap:8px"><span class="num" style="font-size:13px">1 · Structural</span><span style="font-weight:600;font-size:20px">Contact</span><span class="serif" style="font-size:16px;line-height:1.5">Names, letters and photos, calls, visits and holidays with birth family.</span></div>
<div class="card" style="background:var(--cream);border:0;gap:8px"><span class="num" style="font-size:13px">2 · Communicative</span><span style="font-weight:600;font-size:20px">Conversation</span><span class="serif" style="font-size:16px;line-height:1.5">Questions welcome, birth family spoken of with respect, room for grief.</span></div>
</div>
<a class="btn ink" href="start-here.html" style="align-self:flex-start">Read the Openness 101 guide →</a>
</div>
<figure class="dark" style="margin:0;border-radius:28px;padding:44px;display:flex;flex-direction:column;gap:22px">
<div class="quote-mark" aria-hidden="true">“</div>
<blockquote class="serif" style="font-size:32px;line-height:1.3;font-weight:500">Communicative openness is even more clearly related to outcomes.</blockquote>
<figcaption style="display:flex;justify-content:space-between;align-items:flex-end;gap:16px"><span><span style="display:block;font-weight:700;font-size:19px">Prof. Abbie Goldberg</span><span class="serif" style="font-style:italic;font-size:15px;color:var(--sage)">Adoption researcher, Clark University</span></span><a class="epn" href="{ep_url(85)}" style="color:var(--cream);text-decoration:none;border-width:3px">EP. 85</a></figcaption>
</figure>
</div></section>

<section class="sec"><div class="wrap">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap;margin-bottom:40px"><h2 class="h2">Conversations to begin with</h2><a href="episodes.html" style="font-weight:600">All {COUNT} episodes →</a></div>
<div class="g3">{ep_card(80,'Adoptee voices')}{ep_card(103,'Openness 101')}{ep_card(72,'Adoptee voices')}{ep_card(85,'Research')}{ep_card(58,'Language')}{ep_card(100,'Grief & loss')}</div>
</div></section>

<section class="dark"><div class="wrap sec">
<h2 class="h2" style="margin-bottom:40px">In their words</h2>
<div class="g3">
<figure class="qcard"><blockquote>“Adoption is a lifelong journey. It ebbs and it flows.”</blockquote><figcaption><b>Jori</b> · adoptee &amp; birth mom · <a href="{ep_url(95)}" style="color:var(--sage)">Ep. 95</a></figcaption></figure>
<figure class="qcard"><blockquote>“The adoption story belongs to the child, not to you.”</blockquote><figcaption><b>Allison Olson</b> · adoptee &amp; adoptive mom · <a href="{ep_url(80)}" style="color:var(--sage)">Ep. 80</a></figcaption></figure>
<figure class="qcard"><blockquote>“Don’t think that you’re broken or any less of a person because you’re hurting.”</blockquote><figcaption><b>Alexa</b> · birth mother · <a href="{ep_url(22)}" style="color:var(--sage)">Ep. 22</a></figcaption></figure>
</div></div></section>

<section class="sec"><div class="wrap split">
<div class="stack" style="gap:20px">
<span class="pill" style="align-self:flex-start">The book</span>
<h2 class="h2">The Openness Guide for Adoptive Parents</h2>
<p class="lead muted" style="margin:0">Lanette wrote the book she wished we’d had when we adopted our first child: the roles you play beyond “mom” or “dad,” the honest questions to work through, and how to keep openness centered on your child. Grounded in the voices of adoptees and birth parents.</p>
<div class="chiprow" style="align-items:center"><a class="btn leaf" href="{AMAZON}">Get it on Amazon</a><span class="small muted">Paperback &amp; Kindle</span></div>
</div>
<div style="display:flex;justify-content:center;padding:24px"><div class="book"><div><div class="t">The Openness Guide for Adoptive Parents</div><div class="s">What You Should Know About Open Adoption</div></div><div class="a">Lanette J. Nelson</div></div></div>
</div></section>

<section class="leafbg"><div class="wrap" style="padding:64px 32px;display:flex;justify-content:space-between;align-items:center;gap:32px;flex-wrap:wrap">
<div style="max-width:560px"><h2 class="serif" style="font-weight:500;font-size:34px;margin-bottom:8px">Never miss a conversation</h2><p class="serif" style="margin:0;font-size:18px;line-height:1.55;color:var(--sage-l)">Follow the show for new episodes, and join us on Instagram for daily quotes and stories from our guests.</p></div>
<div class="chiprow"><a class="btn ink" href="{APPLE}">Follow on Apple Podcasts</a><a class="btn ink" href="{SPOTIFY}">Follow on Spotify</a><a class="btn sage" href="{IG}">@openadoptionproject</a></div>
</div></section>
'''

# ---------------- START HERE ----------------
path_eps = [(67, 'What open adoption is, why it matters, and how to build relationships that last.'), (68, 'Openness in practice, from our own family and from adoptees we’ve interviewed.'),
            (103, 'The research on structural and communicative openness.'), (95, 'Adoptees in their own words.'), (58, 'How the words we use shape the story.')]
path_html = ''.join(f'''<li><span class="c">{i+1}</span><div class="stack" style="flex:1 1 320px;gap:4px"><a href="{ep_url(n)}" style="color:var(--ink);text-decoration:none;font-family:var(--serif);font-size:22px;font-weight:500">Ep. {n} · {e(BY[str(n)]['title'])}</a><span class="serif muted" style="font-size:16px">{e(w)}</span></div><label><input type="checkbox" id="p{n}">Listened</label></li>''' for i, (n, w) in enumerate(path_eps))
myths = [('Open adoption is a new idea.', 'Most adoptions had some openness until the early-to-mid 1900s. Secrecy is the newer idea.'),
         ('Openness confuses kids.', 'Studies found open adoption doesn’t confuse children or lower self-esteem. It’s linked to higher self-esteem and a more whole sense of self.'),
         ('If contact isn’t possible, openness is off the table.', 'Communicative openness is possible in every adoption. You can always keep the conversation open at home.'),
         ('Openness is a box to check at placement.', 'Parents who chose openness only because an agency pushed them were much less likely to keep it two years later. It lasts when families understand why it matters.')]
myth_html = ''.join(f'<button type="button" class="myth" aria-expanded="false"><span class="k m">Myth</span><span class="k f">Fact</span><span class="x m">{e(a)}</span><span class="x f">{e(b)}</span><span class="small m" style="font-weight:600;opacity:.8">Tap to see the fact</span><span class="small f" style="font-weight:600;opacity:.8">Tap to see the myth</span></button>' for a, b in myths)
def tabpanel(pid, kicker, d, note, looks, dos, hidden):
    return f'''<div id="{pid}" role="tabpanel" class="card panel g2" style="padding:40px;gap:24px"{' hidden' if hidden else ''}>
<div class="stack" style="gap:16px"><span class="num" style="font-size:13px">{kicker}</span><p class="serif" style="margin:0;font-size:30px;line-height:1.3;font-weight:500">{d}</p><p class="serif muted" style="margin:0;font-size:17px;line-height:1.6">{note}</p></div>
<div class="g2" style="gap:16px"><div class="stack" style="background:var(--cream);border-radius:20px;padding:24px;gap:12px"><span style="font-weight:600">It can look like</span><ul>{''.join(f'<li>{x}</li>' for x in looks)}</ul></div>
<div class="stack" style="background:var(--sage-l);border-radius:20px;padding:24px;gap:12px"><span style="font-weight:600">What you can do</span><ul>{''.join(f'<li>{x}</li>' for x in dos)}</ul></div></div></div>'''
start = f'''
<section class="sagebg"><div class="wrap stack" style="padding:72px 32px 64px;gap:22px">
<span class="pill" style="align-self:flex-start">Start here · Openness 101</span>
<h1 class="h1" style="max-width:900px">A beginner’s guide to openness in adoption</h1>
<p class="lead" style="margin:0;max-width:760px">Whether you’re an adoptee, a birth parent, an adoptive or hopeful parent, or you work with families, this page walks through the ideas we come back to in almost every episode. About a 10-minute read.</p>
<nav class="chiprow anchors" aria-label="On this page" style="margin-top:8px"><a href="#what">What is open adoption?</a><a href="#two">Two kinds of openness</a><a href="#research">What research says</a><a href="#myths">Myths &amp; facts</a><a href="#terms">Key terms</a><a href="#path">Your listening path</a></nav>
</div></section>

<section id="what" class="wrap" style="padding-top:88px;padding-bottom:40px"><div class="g2" style="gap:56px;align-items:center">
<div class="stack" style="gap:18px"><span class="num">01</span><h2 class="h2">What is open adoption?</h2>
<p class="body" style="margin:0">In an open adoption, a child’s birth family and adoptive family know who each other are and stay connected in some way.</p>
<p class="body" style="margin:0">It isn’t one arrangement. It can be shared names and medical history, letters and photos, video calls, or birth grandparents at every birthday. And it can change as a child grows and asks for more, or less.</p>
<p class="body" style="margin:0">Most of all, it’s for the adoptee. Openness keeps a child connected to their story, their heritage and the people they come from.</p></div>
<div class="dark stack" style="border-radius:28px;padding:40px;gap:18px"><span class="pill sage" style="align-self:flex-start;font-size:13px">Did you know?</span><p class="serif" style="margin:0;font-size:30px;line-height:1.3;font-weight:500">Openness isn’t a trend. It’s a return.</p><p class="serif" style="margin:0;font-size:17px;line-height:1.6;color:var(--mist)">Most adoptions had some openness until the early-to-mid 1900s. Secrecy and sealed records came later, and some of those policies are still on the books.</p><a href="{ep_url(103)}" style="color:var(--sage);font-weight:600">From Ep. 103, “Why Open Adoption?” →</a></div>
</div></section>

<section id="two" class="wrap" style="padding-top:48px;padding-bottom:40px">
<div class="stack" style="gap:18px;max-width:760px;margin-bottom:32px"><span class="num">02</span><h2 class="h2">Two kinds of openness</h2><p class="body" style="margin:0">Researchers describe openness in two ways. Adoptees need both, and only one of them is ever fully in your control.</p></div>
<div role="tablist" aria-label="Kinds of openness" class="chiprow" style="margin-bottom:20px"><button type="button" class="tabbtn" role="tab" aria-selected="false" aria-controls="tab-s">1 · Structural openness</button><button type="button" class="tabbtn" role="tab" aria-selected="true" aria-controls="tab-c">2 · Communicative openness</button></div>
{tabpanel('tab-s','Structural openness','Contact between an adoptee and their birth family.','How much contact is possible depends on everyone involved, and it can change over the years.',['Shared names and medical history','Letters, photos and texts','Calls and video chats','Visits, birthdays and holidays together'],['Keep the promises you make, even small ones','Plan for contact to grow and change as your child does','Let your child help decide as they get older','Use whatever tools actually work for both families'],True)}
{tabpanel('tab-c','Communicative openness','How freely a family talks about adoption.','This is possible in every adoption, even when contact isn’t. It’s the part adoptive parents fully control.',['Questions are always welcome','Birth family is spoken of with respect','Big feelings, including grief, are allowed','The story is the adoptee’s to share'],['Talk about adoption early and often, in age-appropriate ways','Answer honestly, even when you don’t know everything','Make room for mixed feelings without taking them personally','Ask before sharing your child’s story with others'],False)}
<figure class="dark" style="margin:24px 0 0;display:flex;gap:20px;align-items:center;flex-wrap:wrap;padding:28px 32px;border-radius:22px"><blockquote class="serif" style="flex:1 1 420px;font-size:24px;line-height:1.35">“Communicative openness is even more clearly related to outcomes.”</blockquote><figcaption class="small" style="color:var(--sage)"><b style="color:var(--cream);font-weight:600">Prof. Abbie Goldberg</b> · adoption researcher · <a href="{ep_url(85)}" style="color:var(--sage)">Ep. 85</a></figcaption></figure>
</section>

<section id="research" class="wrap" style="padding-top:48px;padding-bottom:40px">
<span class="num">03</span><h2 class="h2" style="margin:12px 0 28px">What the research says</h2>
<div class="g3">
<div class="card"><p class="serif" style="font-size:19px;line-height:1.5">Knowing about their birth family, however often contact happens, helps adoptees feel they belong in their adoptive family.</p><span class="small" style="margin-top:auto;color:var(--muted-2)">Siegel, 2012</span></div>
<div class="card"><p class="serif" style="font-size:19px;line-height:1.5">Teen adoptees whose families communicated openly with birth family reported more trust in their parents and felt less alienated.</p><span class="small" style="margin-top:auto;color:var(--muted-2)">Kohler et al., 2002</span></div>
<div class="card"><p class="serif" style="font-size:19px;line-height:1.5">How openly a family talks about adoption may predict an adoptee’s self-esteem more than how much contact there is.</p><span class="small" style="margin-top:auto;color:var(--muted-2)">Brodzinsky, 2005</span></div>
</div>
<p class="small" style="margin:18px 0 0;color:var(--muted-2)">Discussed in <a href="{ep_url(103)}">Ep. 103, “Why Open Adoption?”</a> Full citations are in the episode’s show notes.</p>
</section>

<section id="myths" class="wrap" style="padding-top:48px;padding-bottom:40px">
<span class="num">04</span><h2 class="h2" style="margin:12px 0 8px">Myths &amp; facts</h2><p class="serif muted" style="margin:0 0 28px;font-size:18px">Tap a myth to see the fact.</p>
<div class="g2" style="gap:16px">{myth_html}</div>
</section>

<section id="terms" class="wrap" style="padding-top:48px;padding-bottom:40px">
<span class="num">05</span><h2 class="h2" style="margin:12px 0 28px">Key terms</h2>
<dl class="terms g2" style="gap:0 48px">
<div><dt>Adoptee</dt><dd>A person who was adopted, at any age. Adoptees are the experts on their own experience.</dd></div>
<div><dt>Birth parent (first parent)</dt><dd>A child’s biological mother or father. Ask each person which term they prefer.</dd></div>
<div><dt>Adoption constellation</dt><dd>Everyone touched by an adoption: adoptees, birth families, adoptive families, and the people who support them.</dd></div>
<div><dt>Structural openness</dt><dd>Contact and shared information between an adoptee, their birth family and their adoptive family.</dd></div>
<div><dt>Communicative openness</dt><dd>How freely and warmly a family talks about adoption, birth family and the feelings that come with them.</dd></div>
<div><dt>Disenfranchised grief</dt><dd>Grief that society doesn’t recognize as valid. Adoptees, birth parents and adoptive parents can all carry it. <a href="{ep_url(100)}">Ep. 100</a></dd></div>
</dl></section>

<section id="path" class="wrap" style="padding-top:48px;padding-bottom:96px"><div class="card" style="padding:44px">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap;margin-bottom:12px">
<div><span class="num">06</span><h2 class="h2" style="margin-top:12px">Your listening path</h2></div>
<div style="min-width:240px"><div id="pcount" style="font-weight:600;font-size:15px;margin-bottom:8px">0 of 5 listened</div><div class="bar"><i id="pbar"></i></div></div></div>
<ol class="path" style="list-style:none;margin:0;padding:0">{path_html}</ol>
</div></section>
'''

# ---------------- EPISODES ----------------
rows = ''.join(f'''<li data-tag="{e(x['tag'])}" data-n="{x['n']}" data-search="{e((x['title']+' '+x['desc'][:400]).lower())}"><a class="eprow" href="{ep_url(x['n'])}"><span class="n">EP. {x['n']}</span><span class="t">{e(x['title'])}</span><span class="tag">{e(x['tag'])}</span><span class="d">{e(x['date'])}</span><span class="play">{ICON['play']}</span></a></li>''' for x in NUM)
chips = ''.join(f'<button type="button" class="fchip" data-tag="{e(t)}" aria-pressed="{"true" if t=="All" else "false"}">{e(t)}</button>' for t in ['All'] + TAGS)
specials = ''.join(f'<a class="card" href="{ep_url(x["slug"])}" style="gap:8px"><span class="tag" style="align-self:flex-start">Special</span><span class="serif" style="font-size:19px;font-weight:500;line-height:1.35">{e(x["title"])}</span><span class="small" style="color:var(--muted-2)">{e(x["date"])}</span></a>' for x in SPECIAL)
episodes = f'''
<section class="dark"><div class="wrap" style="padding:56px 32px 64px;display:flex;gap:40px;flex-wrap:wrap;align-items:flex-end;justify-content:space-between">
<div class="stack" style="flex:1 1 520px;gap:16px"><h1 class="h1">Every episode</h1><p class="lead" style="margin:0;color:var(--mist);max-width:560px">{COUNT} conversations since April 2021. Search by name or topic, or filter by the part of the adoption constellation you want to hear from.</p></div>
<a class="feat" href="{ep_url(LATEST['n'])}" style="flex:0 1 440px;flex-direction:row;align-items:center;gap:18px;padding:24px 26px;border-radius:22px;box-shadow:none"><span class="btn ink" style="width:56px;height:56px;padding:0;flex:0 0 56px">{ICON['play']}</span><span class="stack" style="gap:4px"><span style="font-weight:700;font-size:12px;letter-spacing:.12em;text-transform:uppercase">Newest · Ep. {LATEST['n']} · {e(LATEST['date'])}</span><span class="serif" style="font-size:19px;line-height:1.3;font-weight:500">{e(LATEST['title'])}</span></span></a>
</div></section>
<section class="wrap stack" style="padding-top:40px;padding-bottom:24px;gap:20px">
<div class="chiprow" style="align-items:center"><label for="q" class="sr">Search episodes</label><div class="search">{ICON['search']}<input id="q" type="search" placeholder="Search by guest, topic or episode number" autocomplete="off"></div><button type="button" id="sort" class="btn line" style="min-height:56px">Newest first</button></div>
<div class="chiprow" role="group" aria-label="Filter by topic">{chips}</div>
<div id="count" aria-live="polite" class="small" style="font-weight:500;color:var(--muted-2)"></div>
</section>
<section class="wrap" style="padding-bottom:40px">
<ul class="eplist" id="eplist">{rows}</ul>
<p id="empty" hidden class="serif" style="font-size:19px;padding:32px 0">No episodes match that yet. Try another word.</p>
<div style="display:flex;justify-content:center;padding-top:28px"><button type="button" id="more" class="btn ink">Show more episodes</button></div>
</section>
<section class="wrap" style="padding-top:24px;padding-bottom:40px"><h2 class="h2" style="font-size:32px;margin-bottom:20px">Specials &amp; announcements</h2><div class="g3">{specials}</div></section>
<section class="wrap" style="padding-top:24px;padding-bottom:88px"><div class="sagebg" style="border-radius:28px;padding:40px;display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap">
<div style="max-width:640px"><h2 class="serif" style="font-weight:500;font-size:32px;margin-bottom:8px">New to the show?</h2><p class="serif" style="margin:0;font-size:18px;line-height:1.55">Our five-episode listening path walks through openness from the ground up.</p></div>
<a class="btn ink" href="start-here.html#path">Start the listening path →</a></div></section>
'''

# ---------------- RESOURCES ----------------
def guide(name, eps, tagq):
    return f'<a class="card" href="episodes.html?tag={e(tagq)}" style="flex-direction:row;justify-content:space-between;align-items:center;gap:16px"><span><span style="display:block;font-weight:600;font-size:20px">{name}</span><span class="serif muted" style="font-size:16px">{eps}</span></span><span style="font-size:24px" aria-hidden="true">→</span></a>'
def eplinks(ns): return ', '.join(f'<span>Ep. {n}</span>' for n in ns)
resources = f'''
<section class="wrap stack" style="padding-top:72px;padding-bottom:40px;gap:16px"><h1 class="h1">Resources</h1><p class="lead" style="margin:0;max-width:720px">Guides we’ve written, organizations we’ve learned from, and the episodes we point people to most.</p></section>
<section class="wrap" style="padding-bottom:56px"><div class="sagebg split" style="border-radius:32px;padding:48px;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr)">
<div style="display:flex;justify-content:center"><div class="book" style="box-shadow:20px 24px 0 var(--ink)"><div><div class="t">The Openness Guide for Adoptive Parents</div><div class="s">What You Should Know About Open Adoption</div></div><div class="a">Lanette J. Nelson</div></div></div>
<div class="stack" style="gap:18px"><span class="pill ink" style="align-self:flex-start;font-size:13px">The book</span>
<h2 class="h2" style="font-size:40px">The book Lanette wishes we’d had when we adopted our first child</h2>
<ul class="serif" style="margin:0;padding-left:20px;display:flex;flex-direction:column;gap:10px;font-size:18px;line-height:1.5"><li>The roles you play beyond “mom” or “dad”: advocate, protector and connector</li><li>Honest questions to work through before and after you adopt</li><li>Grounded in the voices of adoptees and birth parents</li></ul>
<div class="chiprow" style="align-items:center"><a class="btn ink" href="{AMAZON}">Get it on Amazon</a><span class="small">Paperback &amp; Kindle</span></div></div>
</div></section>
<section class="wrap" style="padding-bottom:56px"><h2 class="h2" style="font-size:36px;margin-bottom:24px">Guides &amp; workbooks</h2><div class="g2">
<div class="card"><span class="tag" style="align-self:flex-start">Guide &amp; workbook</span><h3 class="h3">The Openness Guide for Adoptive Parents (workbook edition)</h3><p class="serif muted" style="font-size:16px;line-height:1.55">More than 90 pages of guidance and exercises: visit schedules, conversations with birth parents, and the mindset shifts that make openness work.</p><a href="{GUM_OPENNESS}" style="margin-top:auto;font-weight:600">Get the workbook →</a></div>
<div class="card"><span class="tag" style="align-self:flex-start">Guide</span><h3 class="h3">Substance Exposure in Utero: A Guide for Prospective Adoptive Parents</h3><p class="serif muted" style="font-size:16px;line-height:1.55">What to know and ask before saying yes to a placement involving prenatal substance exposure.</p><a href="{GUM_SUBSTANCE}" style="margin-top:auto;font-weight:600">Get the guide →</a></div>
</div></section>
<section class="wrap" style="padding-bottom:56px"><h2 class="h2" style="font-size:36px;margin-bottom:8px">Listening guides</h2><p class="serif muted" style="margin:0 0 24px;font-size:18px">Hand-picked starting points, or browse every episode on a topic.</p><div class="g2" style="gap:16px">
{guide('Hear from adoptees', 'Ep. 95, 72, 120, 80, 64', 'Adoptee voices')}
{guide('Birth parent stories', 'Ep. 105, 69, 108, 93', 'Birth parents')}
{guide('Openness 101', 'Ep. 67, 68, 103, 104, 110', 'Openness 101')}
{guide('Research &amp; practice', 'Ep. 85, 82, 91, 96, 100', 'Research & practice')}
{guide('Identity, race &amp; culture', 'Ep. 63, 83, 90, 102, 123', 'Identity & culture')}
{guide('Adoption book club', 'Ep. 113, 114, 115, 116, 124, 125', 'Book club')}
</div></section>
<section class="wrap" style="padding-bottom:88px"><h2 class="h2" style="font-size:36px;margin-bottom:24px">Organizations we’ve learned from</h2><div class="g2" style="gap:16px">
<div class="card" style="gap:8px"><span style="font-weight:600;font-size:20px">Brave Love</span><span class="serif muted" style="font-size:16px;line-height:1.55">Support and honor for birth mothers. Hear executive director Janelle Basham in <a href="{ep_url(121)}">Ep. 121</a>.</span></div>
<div class="card" style="gap:8px"><span style="font-weight:600;font-size:20px">Destiny Adoption Foundation</span><span class="serif muted" style="font-size:16px;line-height:1.55">Partners on our Juneteenth specials about Black adoptees and families.</span></div>
</div></section>
'''

# ---------------- ABOUT ----------------
about = f'''
<section class="wrap" style="padding-top:72px;padding-bottom:56px"><div class="g2" style="gap:56px;align-items:center">
<div class="stack" style="gap:20px"><span class="pill" style="align-self:flex-start">About us</span><h1 class="h1">Hi, we’re the Nelsons.</h1>
<p class="body" style="margin:0">We’re Lanette and Shaun, adoptive parents of four kids. Every one of their adoptions is open, with regular visits with their birth families. Our kids would tell you they have more than 16 grandparents who love them.</p>
<p class="body" style="margin:0">We started this podcast in April 2021 to answer the questions friends kept asking us about open adoption. It quickly became something bigger: a place to listen to adoptees, birth parents, adoptive families and professionals, and to keep learning how to do better.</p></div>
<div style="aspect-ratio:4/5;background:var(--sage);border-radius:32px;display:flex;align-items:center;justify-content:center;text-align:center;padding:32px;border:2px dashed var(--leaf)"><span style="font-weight:600;font-size:18px;color:var(--leaf-d)">[Photo of Lanette &amp; Shaun]</span></div>
</div></section>
<section class="dark"><div class="wrap stack sec" style="gap:36px">
<div class="stack" style="max-width:820px;gap:16px"><span class="num" style="color:var(--sage)">Our mission</span><p class="serif" style="margin:0;font-size:clamp(24px,3vw,32px);line-height:1.4;font-weight:500">This podcast is about connecting. It’s about growing. It’s about stretching. The Open Adoption Project is a community dedicated to listening and learning, and building relationships based on healthy respect and communication.</p></div>
<div class="g3">
<div class="qcard" style="gap:10px"><span style="font-weight:600;font-size:20px">Open communication</span><span class="serif" style="font-size:16px;line-height:1.55;color:var(--mist)">Honest conversation between adoptees, birth families and adoptive families.</span></div>
<div class="qcard" style="gap:10px"><span style="font-weight:600;font-size:20px">Lasting relationships</span><span class="serif" style="font-size:16px;line-height:1.55;color:var(--mist)">Supporting open adoption relationships that hold up for a lifetime, not just at placement.</span></div>
<div class="qcard" style="gap:10px"><span style="font-weight:600;font-size:20px">Ethical practice</span><span class="serif" style="font-size:16px;line-height:1.55;color:var(--mist)">Promoting adoption practices that put children’s needs first.</span></div>
</div></div></section>
<section class="wrap" style="padding-top:80px;padding-bottom:40px"><div class="g2">
<div class="sagebg stack" style="border-radius:28px;padding:40px;gap:14px"><h2 class="serif" style="font-weight:500;font-size:34px;line-height:1.2">Share your story on the show</h2><p class="serif" style="margin:0;font-size:18px;line-height:1.6">We especially want to hear from adoptees and birth parents. Every story is different, and every one helps someone listening feel less alone.</p><a class="btn ink" href="#contact" style="align-self:flex-start;margin-top:6px">Tell us about you</a></div>
<div class="card" style="padding:40px"><h2 class="serif" style="font-weight:500;font-size:34px;line-height:1.2">Invite us to speak</h2><p class="serif muted" style="font-size:18px;line-height:1.6">We lead talks, trainings and adoptee panels on openness for agencies, conferences and parent groups, including the Utah Foster Care Annual Symposium.</p><a class="btn leaf" href="#contact" style="align-self:flex-start;margin-top:6px">Ask about speaking</a></div>
</div></section>
<section id="contact" class="wrap" style="padding-top:40px;padding-bottom:96px"><div class="g2" style="gap:56px;align-items:flex-start">
<div class="stack" style="gap:16px"><h2 class="h2">Contact us</h2><p class="lead muted" style="margin:0">Episode requests, questions, guest ideas, speaking requests or just a hello. We read every message.</p>
<p class="serif" style="margin:0;font-size:18px">Email <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<div class="chiprow"><a class="btn line" href="{IG}" style="color:var(--ink)">Instagram</a><a class="btn line" href="{FB}" style="color:var(--ink)">Facebook</a></div></div>
<form id="contact-form" class="card" style="padding:36px;gap:18px">
<div id="cf-status" role="status" hidden style="background:var(--sage-l);color:var(--leaf-d);border-radius:16px;padding:18px 20px;font-weight:600">Your email app should open with your message ready to send. If it doesn’t, email us at {EMAIL}.</div>
<div class="field"><label for="nm">Name</label><input id="nm" autocomplete="name" required></div>
<div class="field"><label for="em">Email</label><input id="em" type="email" autocomplete="email" required></div>
<div class="field"><label for="ab">What’s this about?</label><select id="ab"><option>I’d like to share my story on the show</option><option>Speaking or training request</option><option>Episode request or question</option><option>Something else</option></select></div>
<div class="field"><label for="ms">Message</label><textarea id="ms" required></textarea></div>
<button type="submit" class="btn ink" style="min-height:54px">Send message</button>
</form></div></section>
'''

# ---------------- EPISODE PAGES ----------------
def related(x):
    pool = [y for y in NUM if y['tag'] == x['tag'] and y['n'] != x['n']]
    if x['n']: pool.sort(key=lambda y: abs(int(y['n']) - int(x['n'])))
    return pool[:3]

def episode_page(x, prev=None, nxt=None):
    pre = '../'
    paras = [p.strip() for p in re.split(r'(?<=[.!?])\s+(?=[A-Z“"])', x['desc']) if p.strip()]
    # group sentences into ~3-sentence paragraphs
    grp = [' '.join(paras[i:i+3]) for i in range(0, len(paras), 3)] or ['']
    desc_html = ''.join(f'<p class="body" style="margin:0">{e(g)}</p>' for g in grp)
    tx = tx_for(x['link'])
    tx_html = ''
    if tx:
        tx_html = f'''<section class="tx stack" style="gap:16px"><h2 class="serif" style="font-weight:500;font-size:32px">Transcript</h2>
<details><summary>Read the full transcript</summary>{''.join(f'<p><b>{t}</b>{e(s)}</p>' for t, s in tx)}<p class="small" style="font-family:var(--sans);color:var(--muted-2)">Transcripts are generated automatically and may contain errors.</p></details></section>'''
    q_html = ''
    if x['n'] and int(x['n']) in QUOTES:
        qs = QUOTES[int(x['n'])][:2]
        q_html = ''.join(f'''<figure class="sagebg stack" style="margin:0;border-radius:28px;padding:40px;gap:16px"><div class="quote-mark" aria-hidden="true">“</div><blockquote class="serif" style="font-size:30px;line-height:1.3;font-weight:500">{e(d)}</blockquote><figcaption><b>{e(s)}</b>{(" · " + e(r)) if r else ""}</figcaption></figure>''' for d, s, r in qs)
    rel = ''.join(f'<a class="card" href="{ep_url(y["n"], pre)}" style="gap:10px"><span style="font-weight:700;font-size:14px;color:var(--leaf)">EP. {y["n"]}</span><span class="serif" style="font-size:21px;font-weight:500;line-height:1.3">{e(y["title"])}</span></a>' for y in related(x))
    pn = '<nav class="pnav" aria-label="More episodes">' + (f'<a href="{ep_url(prev["n"], pre)}">← Ep. {prev["n"]}</a>' if prev else '<span></span>') + (f'<a href="{ep_url(nxt["n"], pre)}">Ep. {nxt["n"]} →</a>' if nxt else '') + '</nav>'
    label = f'EP. {x["n"]}' if x['n'] else 'SPECIAL'
    body = f'''
<section class="dark"><div class="wrap stack" style="padding:40px 32px 56px;gap:20px">
<nav aria-label="Breadcrumb" class="small" style="color:var(--sage)"><a href="{pre}episodes.html" style="color:var(--sage)">Episodes</a> / {label.title()}</nav>
<div class="chiprow small" style="align-items:center"><span class="epn" style="font-size:15px">{label}</span><span class="pill sage" style="font-size:13px;letter-spacing:.04em;text-transform:none">{e(x['tag'])}</span><span style="color:var(--mist)">{e(x['date'])}{' · ' + e(x['dur']) if x['dur'] else ''}</span></div>
<h1 class="h1" style="font-size:clamp(34px,5vw,56px);max-width:920px">{e(x['title'])}</h1>
<div class="player" style="margin-top:8px"><audio controls preload="none" src="{e(x['mp3'])}" aria-label="Play episode"></audio>{listen_chips(ep_link=x['link'])}</div>
</div></section>
<div class="wrap layout" style="padding-top:56px;padding-bottom:40px">
<main class="stack" style="gap:48px">
<section class="stack" style="gap:16px"><h2 class="serif" style="font-weight:500;font-size:32px">About this episode</h2>{desc_html}</section>
{q_html}
{tx_html}
{pn}
</main>
<aside>
<div class="dark stack" style="border-radius:22px;padding:26px;gap:14px"><span class="num" style="color:var(--sage);font-size:13px">New here?</span><span class="serif" style="font-size:18px;line-height:1.5">Start with our beginner’s guide to openness and a five-episode listening path.</span><a class="btn sage" href="{pre}start-here.html" style="align-self:flex-start;min-height:44px;font-size:16px">Start here</a></div>
<div class="card" style="gap:12px"><span class="num" style="font-size:13px">Share this episode</span><button type="button" class="btn leaf" data-copy>Copy episode link</button></div>
<div class="card" style="gap:12px"><span class="num" style="font-size:13px">The book</span><span class="serif" style="font-size:18px;font-weight:500;line-height:1.35">The Openness Guide for Adoptive Parents</span><a href="{AMAZON}" style="font-weight:600">Get it on Amazon →</a></div>
</aside></div>
<section class="wrap" style="padding-top:24px;padding-bottom:88px"><h2 class="serif" style="font-weight:500;font-size:32px;margin-bottom:24px">Keep listening</h2><div class="g3">{rel}</div></section>'''
    d = (x['desc'][:155] + '…') if len(x['desc']) > 155 else x['desc']
    return page(f"{x['title']} | Open Adoption Project", d, body, 'episodes.html', pre, f"episodes/{x['slug']}.html")

# ---------------- WRITE ----------------
if os.path.exists(DIST): shutil.rmtree(DIST)
os.makedirs(f'{DIST}/assets'); os.makedirs(f'{DIST}/episodes')
shutil.copy(f'{ROOT}/src/style.css', f'{DIST}/assets/style.css'); shutil.copy(f'{ROOT}/src/app.js', f'{DIST}/assets/app.js')
W = lambda p, s: open(f'{DIST}/{p}', 'w').write(s)
W('index.html', page('Open Adoption Project | Adoption conversations centered on adoptee voices', 'A podcast with Lanette & Shaun Nelson, listening to adoptees, birth parents, adoptive families and researchers to learn what openness in adoption really looks like.', home, '', '', ''))
W('start-here.html', page('Start Here: Openness 101 | Open Adoption Project', 'A beginner’s guide to openness in adoption: structural and communicative openness, research, myths and facts, key terms and a listening path.', start, 'start-here.html', '', 'start-here.html'))
W('episodes.html', page('All Episodes | Open Adoption Project', f'Search all {COUNT} episodes of the Open Adoption Project podcast by guest or topic.', episodes, 'episodes.html', '', 'episodes.html'))
W('resources.html', page('Resources | Open Adoption Project', 'The Openness Guide for Adoptive Parents, workbooks, listening guides and organizations for the adoption community.', resources, 'resources.html', '', 'resources.html'))
W('about.html', page('About & Contact | Open Adoption Project', 'Meet Lanette & Shaun Nelson, share your story on the show, or invite us to speak.', about, 'about.html', '', 'about.html'))
for i, x in enumerate(NUM):
    W(f"episodes/{x['n']}.html", episode_page(x, NUM[i+1] if i+1 < len(NUM) else None, NUM[i-1] if i > 0 else None))
for x in SPECIAL:
    W(f"episodes/{x['slug']}.html", episode_page(x))
# sitemap
urls = ['', 'start-here.html', 'episodes.html', 'resources.html', 'about.html'] + [f"episodes/{x['slug']}.html" for x in EPS]
W('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE}/{u}</loc></url>' for u in urls) + '</urlset>')
W('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
from collections import Counter
print('pages:', len(urls), 'tags:', Counter(x['tag'] for x in NUM))
