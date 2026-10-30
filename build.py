#!/usr/bin/env python3
"""Build the DJ Play site from content.json.

Usage:
    ./build.py              # writes dist/
    ./build.py --out DIR    # writes DIR/

Standard library only. Static files in static/ are copied as-is; every page
is rendered from content.json. Links are relative so the site works both at
a domain root and under a GitHub Pages project path (/djplay/).
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent

# (label, path) for the main menu; "Book now" is added as a button.
NAV = [
    ("Weddings", "weddings/"),
    ("Corporate", "corporate/"),
    ("Packages", "packages/"),
    ("Photo Booth", "photo-booth/"),
    ("Mixes", "mixes/"),
    ("Events", "events/"),
    ("About", "about/"),
    ("Press", "press/"),
]

EXT = 'target="_blank" rel="noopener"'


def e(value: object) -> str:
    return escape(str(value), quote=True)


def home_href(base: str) -> str:
    return base or "./"


def current_attr(href: str, current: str) -> str:
    return ' aria-current="page"' if href == current else ""


def book_link(base: str, **params: str) -> str:
    query = "&amp;".join(f"{k}={quote(v)}" for k, v in params.items())
    return f"{base}book/" + (f"?{query}" if query else "")


# --------------------------------------------------------------------- chrome

def head(c: dict, title: str, description: str, base: str, path: str) -> str:
    site = c["site"]
    url = site["url"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="theme-color" content="#0a0a0a">
<link rel="canonical" href="{e(url + path)}">
<link rel="icon" href="{base}assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{base}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,600;0,800;1,700;1,800;1,900&family=Barlow:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{base}assets/css/site.css">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(url + path)}">
<meta property="og:image" content="{e(url + site['og_image'])}">
<meta name="twitter:card" content="summary_large_image">
</head>"""


def header(c: dict, base: str, current: str) -> str:
    links = "".join(
        f'<a href="{base}{href}"{current_attr(href, current)}>{e(label)}</a>' for label, href in NAV
    )
    return f"""<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap nav-bar">
    <a class="brand" href="{home_href(base)}" aria-label="{e(c['site']['name'])} home"><img src="{base}{e(c['site']['logo'])}" alt="" width="44" height="45"><span>{e(c['site']['name'])}</span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu"><span></span><span></span><span></span></button>
    <nav class="nav" id="site-nav" aria-label="Main">
      {links}
      <a class="btn btn-gold btn-sm" href="{base}book/"{current_attr("book/", current)}>Book now</a>
    </nav>
  </div>
</header>"""


def socials(c: dict) -> str:
    return '<ul class="socials">' + "".join(
        f'<li><a href="{e(s["url"])}" rel="me noopener" target="_blank">{e(s["label"])}</a></li>'
        for s in c["socials"]
    ) + "</ul>"


def footer(c: dict, base: str) -> str:
    site, ct, pb = c["site"], c["contact"], c["photobooth"]
    pages = "".join(f'<li><a href="{base}{href}">{e(label)}</a></li>' for label, href in NAV)
    return f"""<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <a class="brand" href="{home_href(base)}"><img src="{base}{e(site['logo'])}" alt="" width="44" height="45"><span>{e(site['name'])}</span></a>
      <p class="muted small">{e(site['tagline'])} {e(site['region'])}.</p>
    </div>
    <div>
      <p class="footer-label">Pages</p>
      <ul class="footer-list">{pages}<li><a href="{base}book/">Book</a></li></ul>
    </div>
    <div>
      <p class="footer-label">Follow</p>
      {socials(c)}
    </div>
    <div>
      <p class="footer-label">Contact</p>
      <ul class="footer-list">
        <li><a href="tel:{e(ct['phone_href'])}">DJ: {e(ct['phone'])}</a></li>
        <li><a href="tel:{e(pb['phone_href'])}">Photo booth: {e(pb['phone'])}</a></li>
        <li><a href="mailto:{e(ct['email'])}">Email us</a></li>
        <li><a href="{e(pb['url'])}" {EXT}>{e(pb['name'])}</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap">
    <p class="copyright">&copy; {date.today().year} {e(site['name'])} &middot; A <a href="{e(pb['url'])}" {EXT}>{e(pb['name'])}</a> company</p>
  </div>
</footer>
<script src="{base}assets/js/site.js" defer></script>
</body>
</html>
"""


def page(c: dict, *, title: str, description: str, base: str, path: str, body: str) -> str:
    return f"""{head(c, title, description, base, path)}
{header(c, base, path)}
<main id="main">
{body}
</main>
{footer(c, base)}"""


# --------------------------------------------------------------------- pieces

def gear(name: str) -> str:
    """Inline one of the gold line-art gear illustrations from art/ (inline so CSS can animate it)."""
    svg = (ROOT / "art" / f"{name}.svg").read_text()
    return f'<div class="gear gear-{e(name)}" aria-hidden="true">{svg}</div>'


def page_hero(eyebrow: str, title: str, lede: str = "", actions: str = "", art: str = "") -> str:
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    actions_html = f'<div class="actions">{actions}</div>' if actions else ""
    copy = f"""<p class="eyebrow">{e(eyebrow)}</p>
    <h1 class="display">{title}</h1>
    {lede_html}
    {actions_html}"""
    inner = f'<div class="page-hero-grid"><div>{copy}</div>{gear(art)}</div>' if art else copy
    return f"""<section class="page-hero">
  <div class="wrap">
    {inner}
  </div>
</section>"""


def section_head(eyebrow: str, title: str, sub: str = "") -> str:
    sub_html = f'<p class="section-sub">{e(sub)}</p>' if sub else ""
    return f'<div class="section-head reveal"><p class="eyebrow">{e(eyebrow)}</p><h2 class="display">{title}</h2>{sub_html}</div>'


def marquee(words: list[str]) -> str:
    spans = "".join(f"<span>{e(w)}</span>" for w in words)
    return f"""<div class="marquee" role="img" aria-label="{e(', '.join(words))}">
  <div class="marquee-track" aria-hidden="true">{spans}{spans}</div>
</div>"""


def stats(c: dict) -> str:
    return '<ul class="stats">' + "".join(
        f'<li><strong>{e(s["value"])}</strong><span>{e(s["label"])}</span></li>' for s in c["stats"]
    ) + "</ul>"


def tags(items: list[str]) -> str:
    return '<ul class="tags">' + "".join(f"<li>{e(t)}</li>" for t in items) + "</ul>"


def cards(items: list[dict], base: str = "") -> str:
    """Generic title + text cards; an item with "href" becomes a link card."""
    out = []
    for it in items:
        inner = f'<h3>{e(it["title"])}</h3><p>{e(it["text"])}</p>'
        if it.get("href"):
            out.append(f'<a class="card card-link reveal" href="{base}{e(it["href"])}">{inner}<span class="text-link">Learn more &rarr;</span></a>')
        else:
            out.append(f'<article class="card reveal">{inner}</article>')
    cols = " card-grid-3" if len(items) % 3 == 0 else ""
    return f'<div class="card-grid{cols}">' + "".join(out) + "</div>"


def timeline(items: list[dict]) -> str:
    return '<ol class="timeline">' + "".join(
        f'<li class="reveal"><strong>{e(it["title"])}</strong><span>{e(it["text"])}</span></li>' for it in items
    ) + "</ol>"


def mix_card(m: dict) -> str:
    if m.get("embed"):
        media = (
            f'<iframe src="{e(m["embed"])}" title="{e(m["title"])} by DJ Play" width="100%" height="120" '
            f'loading="lazy" allow="encrypted-media; fullscreen; autoplay"></iframe>'
        )
    else:
        media = f'<a class="btn btn-ghost" href="{e(m["url"])}" {EXT}><span class="play-icon" aria-hidden="true"></span>Listen</a>'
    return f"""<article class="mix reveal">
  <div class="mix-media">{media}</div>
  <div class="mix-info">
    <h3>{e(m['title'])}</h3>
    <p class="muted">{e(m['description'])}</p>
  </div>
</article>"""


def package_cards(packages: list[dict], base: str, suffix: str = "") -> str:
    """suffix matches the package to its option in the booking form, e.g. " (wedding)"."""
    out = []
    for p in packages:
        featured = p.get("featured")
        items = "".join(f"<li>{e(i)}</li>" for i in p["items"])
        tag = f'<p class="pkg-tag">{e(p["tag"])}</p>' if p.get("tag") else ""
        btn = "btn-gold" if featured else "btn-ghost"
        out.append(f"""<article class="pkg{' pkg-featured' if featured else ''} reveal">
  {tag}
  <h3>{e(p['name'])}</h3>
  <p class="pkg-guests">{e(p['guests'])}</p>
  <p class="pkg-price"><span>from</span> {e(p['price'])}</p>
  <ul>{items}</ul>
  <a class="btn {btn}" href="{book_link(base, package=p['name'] + suffix)}">Book {e(p['name'])}</a>
</article>""")
    return '<div class="pkg-grid">' + "".join(out) + "</div>"


def addons(c: dict) -> str:
    rows = "".join(f'<li><span>{e(a["name"])}</span><strong>{e(a["price"])}</strong></li>' for a in c["addons"])
    return f"""<div class="addons reveal">
  <h3>Add-ons</h3>
  <ul>{rows}</ul>
  <p class="fine">{e(c['packages_note'])}</p>
</div>"""


def faq(items: list[dict]) -> str:
    return '<div class="faq">' + "".join(
        f'<details class="reveal"><summary>{e(f["q"])}</summary><p>{e(f["a"])}</p></details>' for f in items
    ) + "</div>"


def faq_section(items: list[dict]) -> str:
    return f"""<section class="section">
  <div class="wrap faq-grid">
    {section_head("FAQ", "Good to know")}
    {faq(items)}
  </div>
</section>"""


def booth_cards(c: dict, limit: int | None = None, book_base: str | None = None) -> str:
    booths = c["photobooth"]["booths"][:limit] if limit else c["photobooth"]["booths"]
    out = []
    for b in booths:
        price = f'<p class="booth-price"><span>from</span> {e(b["from"])}</p>' if b.get("from") else ""
        book = (
            f'<a class="text-link booth-book" href="{book_link(book_base, service="booth", booth=b["name"])}">Book this booth &rarr;</a>'
            if book_base is not None else ""
        )
        out.append(f'<li><strong>{e(b["name"])}</strong><span>{e(b["text"])}</span>{price}{book}</li>')
    return '<ul class="booth-types">' + "".join(out) + "</ul>"


def booth_promo(c: dict, base: str, headline: str, text: str) -> str:
    pb = c["photobooth"]
    return f"""<section class="section">
  <div class="wrap">
    <div class="booth reveal">
      <div class="booth-copy">
        <p class="eyebrow">{e(pb['name'])}</p>
        <h2 class="display">{headline}</h2>
        <p>{e(text)}</p>
        <div class="actions">
          <a class="btn btn-gold" href="{base}photo-booth/">See the booths</a>
          <a class="btn btn-ghost" href="{e(pb['url'])}" {EXT}>Visit {e(pb['name'])}</a>
        </div>
      </div>
      {booth_cards(c, limit=4)}
    </div>
  </div>
</section>"""


def upcoming(c: dict) -> list[dict]:
    today = date.today().isoformat()
    return sorted((d for d in c["dates"] if d["date"] >= today), key=lambda d: d["date"])


def date_rows(dates: list[dict]) -> str:
    rows = []
    for d in dates:
        day = date.fromisoformat(d["date"])
        link = (
            f'<a class="btn btn-ghost btn-sm" href="{e(d["url"])}" {EXT}>{e(d.get("link_label") or "Details")}</a>'
            if d.get("url") else ""
        )
        when = " &middot; ".join(e(x) for x in (day.strftime("%A"), d.get("time", "")) if x)
        rows.append(f"""<li class="date-row reveal" data-date="{e(d['date'])}">
  <time datetime="{e(d['date'])}"><span>{day.strftime('%b').upper()}</span><b>{day.day}</b></time>
  <div class="date-info">
    <p class="date-title">{e(d['title'])}</p>
    <p class="muted">{when}<br>{e(d['venue'])}, {e(d['city'])}</p>
  </div>
  {link}
</li>""")
    return '<ul class="dates">' + "".join(rows) + "</ul>"


def social_feed(c: dict) -> str:
    feed, ct = c["social_feed"], c["contact"]
    if feed.get("behold_feed_id"):
        media = (
            f'<behold-widget feed-id="{e(feed["behold_feed_id"])}"></behold-widget>'
            '<script type="module" src="https://w.behold.so/widget.js"></script>'
        )
    elif feed.get("instagram_posts"):
        posts = "".join(
            f'<blockquote class="instagram-media" data-instgrm-permalink="{e(u)}" data-instgrm-version="14">'
            f'<a href="{e(u)}" {EXT}>View this post on Instagram</a></blockquote>'
            for u in feed["instagram_posts"]
        )
        media = f'<div class="ig-grid">{posts}</div><script async src="https://www.instagram.com/embed.js"></script>'
    else:
        media = f"""<a class="ig-follow" href="{e(ct['instagram_url'])}" {EXT}>
  <span class="ig-tiles" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></span>
  <span class="ig-cta"><strong>{e(ct['instagram_handle'])}</strong><span class="muted">Clips, flyers and nights out. Tap to follow.</span></span>
</a>"""
    return f"""<section class="section">
  <div class="wrap">
    <div class="feed-head reveal">
      <div><p class="eyebrow">Social</p><h2 class="display">On the <span class="gold-text">feed</span></h2></div>
      <a class="btn btn-ghost" href="{e(ct['instagram_url'])}" {EXT}>Follow {e(ct['instagram_handle'])}</a>
    </div>
    <div class="feed reveal">{media}</div>
  </div>
</section>"""


def mixes_feature(c: dict, base: str) -> str:
    if not c["mixes"]:
        return ""
    mixcloud = next((s["url"] for s in c["socials"] if s["label"] == "Mixcloud"), "")
    players = "".join(mix_card(m) for m in c["mixes"][:2])
    return f"""<section class="section section-alt">
  <div class="wrap mixes-feature">
    <div class="reveal">
      <p class="eyebrow">Mixes</p>
      <h2 class="display">Hear the <span class="gold-text">sound</span></h2>
      <p class="body-copy">{e(c['mixes_intro'])} Press play and hear what your guests will be dancing to.</p>
      {tags(c['genres'])}
      <div class="actions">
        <a class="btn btn-gold" href="{base}mixes/">All mixes</a>
        <a class="btn btn-ghost" href="{e(mixcloud)}" {EXT}>Follow on Mixcloud</a>
      </div>
    </div>
    <div class="mix-list">{players}</div>
  </div>
</section>"""


def request_band(c: dict) -> str:
    return f"""<section class="band band-gold">
  <div class="wrap band-inner reveal">
    <div>
      <p class="eyebrow">At the party?</p>
      <h2 class="display">Request a song</h2>
    </div>
    <a class="btn btn-dark" href="{e(c['song_request_url'])}" {EXT}>Send a request &rarr;</a>
  </div>
</section>"""


def cta_band(c: dict, base: str, title: str = 'Lock in <span class="gold-text">your date</span>',
             booth_phone: bool = False, **params: str) -> str:
    ct = c["photobooth"] if booth_phone else c["contact"]
    return f"""<section class="section cta">
  <div class="wrap cta-inner reveal">
    <p class="eyebrow">Ready when you are</p>
    <h2 class="display">{title}</h2>
    <p class="section-sub">{e(c['contact']['response_time'])}</p>
    <div class="actions center-actions">
      <a class="btn btn-gold" href="{book_link(base, **params)}">Check your date</a>
      <a class="btn btn-ghost" href="tel:{e(ct['phone_href'])}">Call {e(ct['phone'])}</a>
    </div>
  </div>
</section>"""


def options(values: list[str], selected: str = "") -> str:
    return "".join(
        f'<option value="{e(v)}"{" selected" if v == selected else ""}>{e(v)}</option>' for v in values
    )


def booking_form(c: dict) -> str:
    b, pb = c["booking"], c["photobooth"]
    booths = [x["name"] for x in pb["booths"]] + ["Not sure yet"]
    return f"""<form class="booking-form" data-endpoint="{e(b['form_endpoint'])}" data-email="{e(c['contact']['email'])}" novalidate>
  <div class="field field-wide"><label for="f-service">What are you booking?</label><select id="f-service" name="service" required>{options(b['service_options'], b['service_options'][0])}</select></div>
  <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required></div>
  <div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
  <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
  <div class="field"><label for="f-company-name">Company (if corporate)</label><input id="f-company-name" name="company_name" autocomplete="organization"></div>
  <div class="field"><label for="f-date">Event date</label><input id="f-date" name="event_date" type="date" required></div>
  <div class="field"><label for="f-type">Event type</label><select id="f-type" name="event_type" required><option value="">Choose one</option>{options(b['event_types'])}</select></div>
  <div class="field" data-for="dj"><label for="f-package">DJ package</label><select id="f-package" name="package"><option value="">Choose one</option>{options(b['package_options'])}</select></div>
  <div class="field" data-for="booth"><label for="f-booth">Photo booth</label><select id="f-booth" name="booth"><option value="">Choose one</option>{options(booths)}</select></div>
  <div class="field"><label for="f-guests">Expected guests</label><input id="f-guests" name="guests" type="number" min="1" inputmode="numeric"></div>
  <div class="field"><label for="f-hours">Start and end time</label><input id="f-hours" name="hours" placeholder="e.g. 5pm to 11pm"></div>
  <div class="field field-wide"><label for="f-venue">Venue and city</label><input id="f-venue" name="venue" required></div>
  <div class="field field-wide"><label for="f-msg">Tell us about the event</label><textarea id="f-msg" name="message" rows="5" placeholder="The vibe, the crowd, key moments, must-play songs, anything to avoid."></textarea></div>
  <div class="hp" aria-hidden="true"><label for="f-website">Leave this empty</label><input id="f-website" name="website" tabindex="-1" autocomplete="off"></div>
  <div class="field-wide form-actions">
    <button class="btn btn-gold" type="submit">Send booking request</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </div>
</form>"""


# ---------------------------------------------------------------------- pages

def home(c: dict) -> str:
    site, w, corp = c["site"], c["weddings"], c["corporate"]
    first, last = site["full_name"].split()[0], site["full_name"].split()[-1]
    next_dates = upcoming(c)[:3]
    dates_html = f"""<section class="section section-alt">
  <div class="wrap">
    {section_head("Upcoming", "Catch DJ Play live")}
    {date_rows(next_dates)}
    <div class="center reveal"><a class="btn btn-ghost" href="events/">All events &rarr;</a></div>
  </div>
</section>""" if next_dates else ""
    w_items = "".join(f"<li>{e(m['title'])}</li>" for m in w["moments"])
    c_items = "".join(f"<li>{e(t)}</li>" for t in corp["event_types"][:5])
    w_from = w["packages"][0]["price"]
    body = f"""<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Wedding &amp; Corporate DJ + MC &middot; Los Angeles</p>
      <h1 class="display">Press play<br>on your <span class="gold-text">big day.</span></h1>
      <p class="lede">{e(first)} &ldquo;{e(site['name'])}&rdquo; {e(last)} is the DJ and MC for weddings and corporate events across Los Angeles. Music for every generation, a polished MC who keeps the timeline on track, and pro sound from the first toast to the last dance.</p>
      <div class="actions">
        <a class="btn btn-gold" href="book/">Check your date</a>
        <a class="btn btn-ghost" href="weddings/">Weddings</a>
        <a class="btn btn-ghost" href="corporate/">Corporate</a>
      </div>
    </div>
    <div class="hero-art">
      <div class="logo-glow" aria-hidden="true"></div>
      <img class="hero-logo" src="{e(site['logo'])}" alt="{e(site['name'])} logo: gold play button" width="900" height="931" fetchpriority="high">
    </div>
  </div>
  <div class="eq" aria-hidden="true"></div>
</section>
{marquee(c['marquee'])}

<section class="section">
  <div class="wrap">
    {section_head("What we do best", 'Two rooms. <span class="gold-text">One DJ.</span>')}
    <div class="feature-grid">
      <a class="feature reveal" href="weddings/">
        <p class="eyebrow">Weddings</p>
        <h3 class="display">{w['headline']}</h3>
        <p>{e(w['intro'])}</p>
        <ul class="feature-list">{w_items}</ul>
        <span class="feature-foot"><span>Wedding packages from <strong>{e(w_from)}</strong></span><span class="text-link">Explore weddings &rarr;</span></span>
      </a>
      <a class="feature reveal" href="corporate/">
        <p class="eyebrow">Corporate</p>
        <h3 class="display">{corp['headline']}</h3>
        <p>{e(corp['intro'])}</p>
        <ul class="feature-list">{c_items}</ul>
        <span class="feature-foot"><span>Polished MC, mics and pro sound</span><span class="text-link">Explore corporate &rarr;</span></span>
      </a>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    {section_head("Why DJ Play", 'Reads the room.<br><span class="gold-text">Holds the room.</span>')}
    {cards(c['reasons'])}
  </div>
</section>

<section class="section">
  <div class="wrap about-grid">
    <div class="reveal">
      <p class="eyebrow">About</p>
      <h2 class="display">Mixing since <span class="gold-text">{e(site['since'])}</span></h2>
      {gear("turntable")}
    </div>
    <div class="reveal">
      <p class="body-copy">{e(c['bio']['long'][0])}</p>
      {stats(c)}
      <p class="also-line">Also booking private parties, church celebrations and community events. <a class="text-link" href="packages/">See all packages &rarr;</a></p>
    </div>
  </div>
</section>

{mixes_feature(c, "")}
{booth_promo(c, "", 'Add a photo booth.<br><span class="gold-text">Make it an experience.</span>', c['photobooth']['intro'])}
{dates_html}
{social_feed(c)}
{cta_band(c, "")}"""
    return page(c, title=f"{site['name']} | Wedding & Corporate DJ in Los Angeles", description=c["bio"]["short"],
                base="", path="", body=body)


def weddings(c: dict) -> str:
    w = c["weddings"]
    wedding_faq = [f for f in c["faq"] if f["q"] in {
        "Do you play the ceremony?", "Will you work with our planner and venue?", "Can I send song requests?",
        "Do you travel?", "How far ahead should I book?", "How do I lock in my date?"}]
    body = f"""{page_hero("Weddings", w["headline"], e(w["intro"]),
        f'<a class="btn btn-gold" href="{book_link("../", type="Wedding")}">Check your date</a><a class="btn btn-ghost" href="#wedding-packages">Wedding packages</a>',
        art="controller")}
{marquee(["Ceremony", "Cocktail Hour", "Grand Entrance", "First Dance", "Toasts", "Reception", "Last Dance"])}

<section class="section">
  <div class="wrap">
    {section_head("The day", 'Every moment, <span class="gold-text">planned with you</span>')}
    {timeline(w['moments'])}
  </div>
</section>

<section class="section section-alt" id="wedding-packages">
  <div class="wrap">
    {section_head("Wedding packages", 'Pick your <span class="gold-text">package</span>', "DJ performance and MC hosting in every package. Travel fees may apply depending on location.")}
    {package_cards(w['packages'], "../", " (wedding)")}
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="reveal">
      <p class="eyebrow">How planning works</p>
      <h2 class="display">You plan the day. <span class="gold-text">We plan the sound.</span></h2>
      <p class="body-copy">Every wedding starts with a conversation. By the time you walk in, the music, the timeline and the announcements are already worked out with you and your vendors.</p>
    </div>
    <div>{timeline(w['planning'])}</div>
  </div>
</section>

{booth_promo(c, "../", 'Add a <span class="gold-text">photo booth</span>', "The Elite package includes a 2-hour Glam Photo Booth. Or add any booth from Picture This Booth LA to your wedding and book it all in one request.")}
{faq_section(wedding_faq)}
{cta_band(c, "../", 'Is your date <span class="gold-text">open?</span>', type="Wedding")}"""
    return page(c, title=f"Wedding DJ & MC in Los Angeles | {c['site']['name']}",
                description="Wedding DJ and MC in Los Angeles: ceremony, cocktail hour and reception, with personalized music planning. Packages from " + w["packages"][0]["price"] + ".",
                base="../", path="weddings/", body=body)


def corporate(c: dict) -> str:
    corp = c["corporate"]
    corp_pkgs = [p for p in c["packages"] if p.get("featured")] or c["packages"][-1:]
    corp_faq = [f for f in c["faq"] if f["q"] in {
        "Can you handle speeches and announcements?", "Can you keep the music clean?", "Do you travel?",
        "What if something goes wrong with the equipment?", "How do I lock in my date?"}]
    body = f"""{page_hero("Corporate Events", corp["headline"], e(corp["intro"]),
        f'<a class="btn btn-gold" href="{book_link("../", type="Corporate event")}">Request a quote</a><a class="btn btn-ghost" href="../packages/#event-packages">See packages</a>',
        art="speakers")}
{marquee(corp['event_types'])}

<section class="section">
  <div class="wrap">
    {section_head("What you get", 'Professional from <span class="gold-text">setup to send-off</span>')}
    {cards(corp['features'])}
  </div>
</section>

<section class="section section-alt">
  <div class="wrap split">
    <div class="reveal">
      <p class="eyebrow">Built for</p>
      <h2 class="display">Any company <span class="gold-text">occasion</span></h2>
      <p class="body-copy">From a team dinner to a full gala, DJ Play brings the right setup for the room and keeps the program on schedule.</p>
      {tags(corp['event_types'])}
    </div>
    <div class="reveal">
      {package_cards(corp_pkgs, "../")}
    </div>
  </div>
</section>

{booth_promo(c, "../", 'Put your brand <span class="gold-text">in the photos</span>', "Add a digital photo booth with your logo and colors, or a 360 booth for slow-mo video made for sharing. Book it with the DJ in one request.")}
{faq_section(corp_faq)}
{cta_band(c, "../", 'Planning a <span class="gold-text">company event?</span>', type="Corporate event")}"""
    return page(c, title=f"Corporate Event DJ & MC in Los Angeles | {c['site']['name']}",
                description="Corporate event DJ and MC in Los Angeles for holiday parties, galas and company celebrations. Polished MC, wireless mics and pro sound.",
                base="../", path="corporate/", body=body)


def packages(c: dict) -> str:
    w = c["weddings"]
    body = f"""{page_hero("Packages & Pricing", 'Pick your <span class="gold-text">package</span>', e(c["packages_intro"]))}
<section class="section section-tight">
  <div class="wrap">
    {section_head("Weddings", "Wedding packages", "DJ performance and MC hosting in every wedding package.")}
    {package_cards(w['packages'], "../", " (wedding)")}
    <p class="center reveal"><a class="text-link" href="../weddings/">How wedding planning works &rarr;</a></p>
  </div>
</section>

<section class="section section-alt" id="event-packages">
  <div class="wrap">
    {section_head("Corporate & events", "Event packages", "For corporate functions, galas, parties and celebrations. Up to 5 hours, professional setup, transport and breakdown, plus a pre-event consultation.")}
    {package_cards(c['packages'], "../")}
    {addons(c)}
  </div>
</section>

<section class="section">
  <div class="wrap">
    {section_head("What we play for", "Built for any crowd")}
    {cards(c['events'], "../")}
  </div>
</section>
{faq_section(c['faq'])}
{cta_band(c, "../")}"""
    return page(c, title=f"Packages & Pricing | {c['site']['name']}",
                description="DJ Play wedding packages from " + w["packages"][0]["price"] + " and event packages from " + c["packages"][0]["price"] + " for corporate events, parties and celebrations in Los Angeles.",
                base="../", path="packages/", body=body)


def photo_booth(c: dict) -> str:
    pb = c["photobooth"]
    body = f"""{page_hero(pb["name"], 'Add a photo booth.<br><span class="gold-text">Make it an experience.</span>', e(pb["intro"]),
        f'<a class="btn btn-gold" href="{book_link("../", service="booth")}">Book a photo booth</a><a class="btn btn-ghost" href="tel:{e(pb["phone_href"])}">Call {e(pb["phone"])}</a><a class="btn btn-ghost" href="{e(pb["url"])}" {EXT}>Visit {e(pb["name"])}</a>')}
<section class="section">
  <div class="wrap">
    {section_head("The booths", "Pick your booth", "Starting prices from " + pb["name"] + ". See their site for full package details.")}
    <div class="reveal">{booth_cards(c, book_base="../")}</div>
    <div class="also reveal">
      <p class="eyebrow">Also available</p>
      {tags(pb['also'])}
      <p class="fine"><a class="text-link" href="{e(pb['pricing_url'])}" {EXT}>Full booth pricing on {e(pb['name'])} &rarr;</a></p>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap split">
    <a class="feature reveal" href="{book_link("../", service="both", type="Wedding")}">
      <p class="eyebrow">For weddings</p>
      <h3 class="display">Glam, 360 <span class="gold-text">and more</span></h3>
      <p>Black-and-white glam portraits and slow-mo 360 video made for sharing. The Elite wedding package includes a 2-hour Glam Photo Booth.</p>
      <span class="feature-foot"><span></span><span class="text-link">Book DJ + booth &rarr;</span></span>
    </a>
    <a class="feature reveal" href="{book_link("../", service="both", type="Corporate event")}">
      <p class="eyebrow">For corporate</p>
      <h3 class="display">Your brand, <span class="gold-text">in every photo</span></h3>
      <p>A digital booth with your logo and colors, ready to share. Pair it with DJ Play for one booking that covers music, MC and photos.</p>
      <span class="feature-foot"><span></span><span class="text-link">Book DJ + booth &rarr;</span></span>
    </a>
  </div>
</section>
{cta_band(c, "../", 'Book the booth. <span class="gold-text">Or both.</span>', booth_phone=True, service="both")}"""
    return page(c, title=f"Photo Booth | {c['site']['name']} x {pb['name']}",
                description=f"Add a photo booth from {pb['name']} to your wedding or corporate event: glam, 360, digital, open air, enclosed and magazine booths.",
                base="../", path="photo-booth/", body=body)


def mixes(c: dict) -> str:
    mixcloud = next((s["url"] for s in c["socials"] if s["label"] == "Mixcloud"), "")
    body = f"""{page_hero("Mixes", 'Hear the <span class="gold-text">sound</span>', e(c["mixes_intro"]), art="mixer")}
<section class="section section-tight">
  <div class="wrap">
    <div class="mix-list">{"".join(mix_card(m) for m in c["mixes"])}</div>
    <div class="follow reveal">
      <div>
        <h2 class="display">More on Mixcloud</h2>
        <p class="muted">Follow DJ Play to catch new mixes as they drop.</p>
      </div>
      <a class="btn btn-gold" href="{e(mixcloud)}" {EXT}>Follow on Mixcloud</a>
    </div>
  </div>
</section>
{request_band(c)}
{cta_band(c, "../")}"""
    return page(c, title=f"Mixes | {c['site']['name']}", description=c["mixes_intro"],
                base="../", path="mixes/", body=body)


def events(c: dict) -> str:
    dates = upcoming(c)
    listing = date_rows(dates) if dates else """<div class="empty reveal">
  <h2 class="display">No public dates <span class="gold-text">right now</span></h2>
  <p class="muted">New public dates land here first. Planning a wedding or company event? DJ Play is taking bookings.</p>
  <div class="actions"><a class="btn btn-gold" href="../book/">Check your date</a></div>
</div>"""
    body = f"""{page_hero("Events", 'Catch DJ Play <span class="gold-text">live</span>', "Public dates, parties and pop-ups. Private weddings and corporate events don't show here.")}
<section class="section section-tight">
  <div class="wrap">{listing}</div>
</section>
{social_feed(c)}
{request_band(c)}"""
    return page(c, title=f"Events | {c['site']['name']}", description="Upcoming public DJ Play dates and events in Southern California.",
                base="../", path="events/", body=body)


def about(c: dict) -> str:
    site, ct = c["site"], c["contact"]
    first, last = site["full_name"].split()[0], site["full_name"].split()[-1]
    long_bio = "".join(f'<p class="body-copy">{e(p)}</p>' for p in c["bio"]["long"])
    body = f"""{page_hero("About", f'{e(first)} &ldquo;<span class="gold-text">{e(site["name"])}</span>&rdquo; {e(last)}', e(site["tagline"]))}
<section class="section section-tight">
  <div class="wrap about-page">
    <div class="reveal">
      {long_bio}
      <div class="actions">
        <a class="btn btn-gold" href="../book/">Check your date</a>
        <a class="btn btn-ghost" href="../press/">Press kit</a>
      </div>
    </div>
    <div class="about-art reveal">
      <div class="logo-glow" aria-hidden="true"></div>
      <img class="hero-logo" src="../{e(site['logo'])}" alt="{e(site['name'])} logo" width="900" height="931" loading="lazy">
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    {section_head("By the numbers", "Since " + e(site["since"]))}
    <div class="reveal">{stats(c)}</div>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="reveal">
      <p class="eyebrow">The sound</p>
      <h2 class="display">Every era</h2>
      <p class="body-copy">Open format means the music follows the room. Golden-era hip-hop and funk at the core, with R&amp;B, old school, throwbacks, Top 40 and gospel when the crowd calls for it.</p>
      {tags(c['genres'])}
    </div>
    <div class="reveal">
      <p class="eyebrow">Where he plays</p>
      <h2 class="display">All over So-Cal</h2>
      <p class="body-copy">{e(site['region'])}.</p>
      {tags(c['booking']['service_area'])}
    </div>
  </div>
</section>
{cta_band(c, "../")}"""
    return page(c, title=f"About | {site['name']}", description=c["bio"]["short"],
                base="../", path="about/", body=body)


def book(c: dict) -> str:
    b, ct = c["booking"], c["contact"]
    steps = "".join(f'<li><strong>{e(s["title"])}</strong><span>{e(s["text"])}</span></li>' for s in b["steps"])
    body = f"""{page_hero("Book", 'Lock in <span class="gold-text">your date</span>', "Book DJ Play, a photo booth, or both. " + e(ct["response_time"]))}
<section class="section section-tight">
  <div class="wrap book-grid">
    <div class="reveal">
      <ol class="steps">{steps}</ol>
      <p class="fine">{e(b['lead_time'])}</p>
      <div class="contact-card">
        <a class="contact-row" href="tel:{e(ct['phone_href'])}"><span class="contact-label">DJ Play: call or text</span><span class="contact-value">{e(ct['phone'])}</span></a>
        <a class="contact-row" href="tel:{e(c['photobooth']['phone_href'])}"><span class="contact-label">Photo booth questions</span><span class="contact-value">{e(c['photobooth']['phone'])}</span></a>
        <a class="contact-row" href="mailto:{e(ct['email'])}?subject=DJ%20Play%20booking%20inquiry"><span class="contact-label">Email</span><span class="contact-value">{e(ct['email'])}</span></a>
        <a class="contact-row" href="{e(ct['instagram_url'])}" {EXT}><span class="contact-label">DM on Instagram</span><span class="contact-value">{e(ct['instagram_handle'])}</span></a>
      </div>
      <p class="contact-label area-label">Serving</p>
      {tags(b['service_area'])}
    </div>
    <div class="form-card reveal" id="request">
      <h2 class="display">Booking request</h2>
      {booking_form(c)}
    </div>
  </div>
</section>"""
    return page(c, title=f"Book | {c['site']['name']}",
                description="Book DJ Play and a photo booth for your wedding or corporate event in Los Angeles and Orange County.",
                base="../", path="book/", body=body)


def press(c: dict) -> str:
    site, bio, ct, pr = c["site"], c["bio"], c["contact"], c["press"]
    logo = pr["logos"][0]["src"] if pr["logos"] else site["logo"]
    long_bio = "\n\n".join(bio["long"])
    logos = "".join(
        f'<figure class="asset-card"><div class="asset-img"><img src="../{e(l["src"])}" alt="{e(l["label"])}" loading="lazy"></div>'
        f'<figcaption><span><strong>{e(l["label"])}</strong><span class="muted small">{e(l.get("meta", ""))}</span></span>'
        f'<a class="btn btn-ghost btn-sm no-print" href="../{e(l["src"])}" download>Download</a></figcaption></figure>'
        for l in pr["logos"]
    )
    photos = "".join(
        f'<figure class="asset-card"><div class="asset-img asset-photo"><img src="../{e(ph["src"])}" alt="{e(ph["alt"])}" loading="lazy"></div>'
        f'<figcaption><span class="muted small">{e(ph.get("credit", ""))}</span>'
        f'<a class="btn btn-ghost btn-sm no-print" href="../{e(ph["src"])}" download>Download</a></figcaption></figure>'
        for ph in pr["photos"]
    )
    photos_html = f"""<section class="section">
  <div class="wrap">
    {section_head("Photos", "Press photos", "High resolution. Credit the photographer when you use them.")}
    <div class="asset-grid">{photos}</div>
  </div>
</section>""" if photos else ""
    mix_rows = "".join(
        f'<li><a href="{e(m["url"])}" {EXT}>{e(m["title"])}</a> <span class="muted">{e(m["description"])}</span></li>'
        for m in c["mixes"]
    )
    brings = "".join(f"<li>{e(x)}</li>" for x in pr["brings"])
    venue = (
        f'<div class="reveal"><h2 class="display">Venue needs</h2><ul class="checklist">{"".join(f"<li>{e(x)}</li>" for x in pr["venue_needs"])}</ul></div>'
        if pr["venue_needs"] else ""
    )
    body = f"""<section class="page-hero press-hero">
  <div class="wrap press-hero-grid">
    <div>
      <p class="eyebrow">Electronic press kit</p>
      <h1 class="display">{e(site['name'])}</h1>
      <p class="lede">{e(site['tagline'])} {e(pr['intro'])}</p>
      <div class="actions no-print">
        <button class="btn btn-gold" type="button" data-print>Save as PDF</button>
        <a class="btn btn-ghost" href="../{e(logo)}" download>Download logo</a>
        <a class="btn btn-ghost" href="../book/">Book a date</a>
      </div>
    </div>
    <img class="press-logo" src="../{e(site['logo'])}" alt="{e(site['name'])} logo" width="900" height="931">
  </div>
</section>

<section class="section section-tight">
  <div class="wrap">
    <dl class="facts reveal">
      <div><dt>Name</dt><dd>{e(site['full_name'])}</dd></div>
      <div><dt>Based in</dt><dd>{e(site['location'])}</dd></div>
      <div><dt>Mixing since</dt><dd>{e(site['since'])}</dd></div>
      <div><dt>Style</dt><dd>Open format DJ + MC</dd></div>
    </dl>
    <div class="split press-split">
      <div class="reveal"><p class="eyebrow">Sound</p>{tags(c['genres'])}</div>
      <div class="reveal"><p class="eyebrow">Books</p>{tags(pr['focus'])}</div>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap bios">
    <div class="bio-block reveal">
      <div class="bio-head"><h2 class="display">Short bio</h2><button class="btn btn-ghost btn-sm no-print" type="button" data-copy="bio-short">Copy</button></div>
      <p id="bio-short" class="body-copy">{e(bio['short'])}</p>
    </div>
    <div class="bio-block reveal">
      <div class="bio-head"><h2 class="display">Full bio</h2><button class="btn btn-ghost btn-sm no-print" type="button" data-copy="bio-long">Copy</button></div>
      <div id="bio-long" class="body-copy prewrap">{e(long_bio)}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    {section_head("Brand", "Logos", "Use these on flyers, programs and event pages. Keep them unaltered.")}
    <div class="asset-grid">{logos}</div>
  </div>
</section>
{photos_html}
<section class="section section-alt">
  <div class="wrap split">
    <div class="reveal">
      <h2 class="display">Mixes</h2>
      <ul class="plain">{mix_rows}</ul>
    </div>
    <div class="reveal">
      <h2 class="display">DJ Play brings</h2>
      <ul class="checklist">{brings}</ul>
    </div>
    {venue}
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="reveal">
      <h2 class="display">Contact</h2>
      <ul class="contact-list">
        <li><span class="contact-label">Booking</span><a href="tel:{e(ct['phone_href'])}">{e(ct['phone'])}</a></li>
        <li><span class="contact-label">Email</span><a href="mailto:{e(ct['email'])}">{e(ct['email'])}</a></li>
        <li><span class="contact-label">Website</span><a href="{e(site['url'])}">{e(site['url'].split('://')[-1].rstrip('/'))}</a></li>
      </ul>
    </div>
    <div class="reveal">
      <h2 class="display">Socials</h2>
      <ul class="contact-list">{"".join(f'<li><span class="contact-label">{e(s["label"])}</span><a href="{e(s["url"])}" {EXT}>{e(s["url"].split("://")[-1].removeprefix("www.").rstrip("/"))}</a></li>' for s in c["socials"])}</ul>
    </div>
  </div>
</section>"""
    return page(c, title=f"Press kit | {site['name']}",
                description=f"Press kit for {site['name']}: bios, logos, mixes and booking contacts.",
                base="../", path="press/", body=body)


def not_found(c: dict) -> str:
    # GitHub Pages serves this for any missing path at any depth, so links use the absolute site URL.
    base = c["site"]["url"]
    body = page_hero("404", 'Track <span class="gold-text">not found</span>', "That page skipped. Let's get you back on the floor.",
                     f'<a class="btn btn-gold" href="{base}">Back to home</a><a class="btn btn-ghost" href="{base}book/">Check your date</a>')
    return page(c, title=f"Page not found | {c['site']['name']}", description="Page not found.",
                base=base, path="404.html", body=body)


# ----------------------------------------------------------------------- main

PAGES = {
    "index.html": home,
    "weddings/index.html": weddings,
    "corporate/index.html": corporate,
    "packages/index.html": packages,
    "photo-booth/index.html": photo_booth,
    "mixes/index.html": mixes,
    "events/index.html": events,
    "about/index.html": about,
    "press/index.html": press,
    "book/index.html": book,
    "404.html": not_found,
}


def build(out: Path) -> None:
    content = json.loads((ROOT / "content.json").read_text())
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(ROOT / "static", out)
    for rel, render in PAGES.items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(content))
    print(f"Built {len(PAGES)} pages into {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    build(parser.parse_args().out.resolve())
