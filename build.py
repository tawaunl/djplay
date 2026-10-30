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
    ("Mixes", "mixes/"),
    ("Events", "events/"),
    ("Packages", "packages/"),
    ("Photo Booth", "photo-booth/"),
    ("About", "about/"),
]

EXT = 'target="_blank" rel="noopener"'


def e(value: object) -> str:
    return escape(str(value), quote=True)


def home_href(base: str) -> str:
    return base or "./"


def current_attr(href: str, current: str) -> str:
    return ' aria-current="page"' if href == current else ""


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
        f'<a href="{base}{href}"{current_attr(href, current)}>{e(label)}</a>'
        for label, href in NAV
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
      <p class="muted small">{e(site['tagline'])}</p>
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
        <li><a href="tel:{e(ct['phone_href'])}">{e(ct['phone'])}</a></li>
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

def page_hero(eyebrow: str, title: str, lede: str = "") -> str:
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    return f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">{e(eyebrow)}</p>
    <h1 class="display">{title}</h1>
    {lede_html}
  </div>
</section>"""


def section_head(eyebrow: str, title: str, sub: str = "") -> str:
    sub_html = f'<p class="section-sub">{e(sub)}</p>' if sub else ""
    return f'<div class="section-head reveal"><p class="eyebrow">{e(eyebrow)}</p><h2 class="display">{title}</h2>{sub_html}</div>'


def marquee(c: dict) -> str:
    words = "".join(f"<span>{e(g)}</span>" for g in c["genres"])
    return f"""<div class="marquee" role="img" aria-label="Genres: {e(', '.join(c['genres']))}">
  <div class="marquee-track" aria-hidden="true">{words}{words}</div>
</div>"""


def stats(c: dict) -> str:
    return '<ul class="stats">' + "".join(
        f'<li><strong>{e(s["value"])}</strong><span>{e(s["label"])}</span></li>' for s in c["stats"]
    ) + "</ul>"


def tags(items: list[str]) -> str:
    return '<ul class="tags">' + "".join(f"<li>{e(t)}</li>" for t in items) + "</ul>"


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


def event_cards(c: dict) -> str:
    return '<div class="event-grid">' + "".join(
        f'<article class="event-card reveal"><h3>{e(ev["title"])}</h3><p>{e(ev["text"])}</p></article>'
        for ev in c["events"]
    ) + "</div>"


def package_cards(c: dict, base: str) -> str:
    cards = []
    for p in c["packages"]:
        featured = p.get("featured")
        items = "".join(f"<li>{e(i)}</li>" for i in p["items"])
        btn = "btn-gold" if featured else "btn-ghost"
        cards.append(f"""<article class="pkg{' pkg-featured' if featured else ''} reveal">
  <h3>{e(p['name'])}</h3>
  <p class="pkg-guests">{e(p['guests'])}</p>
  <p class="pkg-price"><span>from</span> {e(p['price'])}</p>
  <ul>{items}</ul>
  <a class="btn {btn}" href="{base}book/?package={e(p['name'])}">Book {e(p['name'])}</a>
</article>""")
    return '<div class="pkg-grid">' + "".join(cards) + "</div>"


def addons(c: dict) -> str:
    rows = "".join(f'<li><span>{e(a["name"])}</span><strong>{e(a["price"])}</strong></li>' for a in c["addons"])
    return f"""<div class="addons reveal">
  <h3>Add-ons</h3>
  <ul>{rows}</ul>
  <p class="fine">{e(c['packages_note'])}</p>
</div>"""


def faq(c: dict) -> str:
    return '<div class="faq">' + "".join(
        f'<details class="reveal"><summary>{e(f["q"])}</summary><p>{e(f["a"])}</p></details>' for f in c["faq"]
    ) + "</div>"


def booth_cards(c: dict, limit: int | None = None, book_base: str | None = None) -> str:
    booths = c["photobooth"]["booths"][:limit] if limit else c["photobooth"]["booths"]
    cards = []
    for b in booths:
        price = f'<p class="booth-price"><span>from</span> {e(b["from"])}</p>' if b.get("from") else ""
        book = (
            f'<a class="text-link booth-book" href="{book_base}book/?service=booth&amp;booth={quote(b["name"])}">Book this booth &rarr;</a>'
            if book_base is not None else ""
        )
        cards.append(f'<li><strong>{e(b["name"])}</strong><span>{e(b["text"])}</span>{price}{book}</li>')
    return '<ul class="booth-types">' + "".join(cards) + "</ul>"


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


def cta_band(c: dict, base: str) -> str:
    ct = c["contact"]
    return f"""<section class="section cta">
  <div class="wrap cta-inner reveal">
    <p class="eyebrow">Ready when you are</p>
    <h2 class="display">Lock in <span class="gold-text">your date</span></h2>
    <p class="section-sub">{e(ct['response_time'])}</p>
    <div class="actions center-actions">
      <a class="btn btn-gold" href="{base}book/">Book DJ Play</a>
      <a class="btn btn-ghost" href="tel:{e(ct['phone_href'])}">Call {e(ct['phone'])}</a>
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
  <div class="field"><label for="f-date">Event date</label><input id="f-date" name="event_date" type="date" required></div>
  <div class="field"><label for="f-type">Event type</label><select id="f-type" name="event_type" required><option value="">Choose one</option>{options(b['event_types'])}</select></div>
  <div class="field"><label for="f-guests">Expected guests</label><input id="f-guests" name="guests" type="number" min="1" inputmode="numeric"></div>
  <div class="field" data-for="dj"><label for="f-package">DJ package</label><select id="f-package" name="package"><option value="">Choose one</option>{options(b['package_options'])}</select></div>
  <div class="field" data-for="booth"><label for="f-booth">Photo booth</label><select id="f-booth" name="booth"><option value="">Choose one</option>{options(booths)}</select></div>
  <div class="field field-wide"><label for="f-venue">Venue and city</label><input id="f-venue" name="venue" required></div>
  <div class="field field-wide"><label for="f-hours">Start and end time</label><input id="f-hours" name="hours" placeholder="e.g. 6pm to 11pm"></div>
  <div class="field field-wide"><label for="f-msg">Tell us about the event</label><textarea id="f-msg" name="message" rows="5" placeholder="The vibe, the crowd, must-play songs, anything to avoid."></textarea></div>
  <div class="hp" aria-hidden="true"><label for="f-company">Leave this empty</label><input id="f-company" name="company" tabindex="-1" autocomplete="off"></div>
  <div class="field-wide form-actions">
    <button class="btn btn-gold" type="submit">Send booking request</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </div>
</form>"""


# ---------------------------------------------------------------------- pages

def home(c: dict) -> str:
    site, ct, pb = c["site"], c["contact"], c["photobooth"]
    featured = c["mixes"][0] if c["mixes"] else None
    mix_html = f"""<section class="section">
  <div class="wrap">
    {section_head("Mixes", "Hear the sound", c["mixes_intro"])}
    {mix_card(featured)}
    <div class="center reveal"><a class="btn btn-ghost" href="mixes/">All mixes &rarr;</a></div>
  </div>
</section>""" if featured else ""
    next_dates = upcoming(c)[:3]
    dates_html = f"""<section class="section section-alt">
  <div class="wrap">
    {section_head("Upcoming", "Catch DJ Play live")}
    {date_rows(next_dates)}
    <div class="center reveal"><a class="btn btn-ghost" href="events/">All events &rarr;</a></div>
  </div>
</section>""" if next_dates else ""
    body = f"""<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Open Format &middot; So-Cal &middot; Since {e(site['since'])}</p>
      <h1 class="display">Press play<br>on your <span class="gold-text">party.</span></h1>
      <p class="lede">Hip-hop, funk, R&amp;B, old school and today's hits, mixed live by {e(site['full_name'].split()[0])} &ldquo;{e(site['name'])}&rdquo; {e(site['full_name'].split()[-1])}. He reads the room and keeps it moving at weddings, private parties, church celebrations and corporate events across Los Angeles.</p>
      <div class="actions">
        <a class="btn btn-gold" href="book/">Book DJ Play</a>
        <a class="btn btn-ghost" href="mixes/"><span class="play-icon" aria-hidden="true"></span>Listen to mixes</a>
      </div>
    </div>
    <div class="hero-art">
      <div class="logo-glow" aria-hidden="true"></div>
      <img class="hero-logo" src="{e(site['logo'])}" alt="{e(site['name'])} logo: gold play button" width="900" height="931" fetchpriority="high">
    </div>
  </div>
  <div class="eq" aria-hidden="true"></div>
</section>
{marquee(c)}

<section class="section">
  <div class="wrap about-grid">
    <div class="reveal">
      <p class="eyebrow">About</p>
      <h2 class="display">Reads the room.<br><span class="gold-text">Holds the room.</span></h2>
    </div>
    <div class="reveal">
      <p class="body-copy">{e(c['bio']['long'][0])}</p>
      {stats(c)}
      <p><a class="text-link" href="about/">More about DJ Play &rarr;</a></p>
    </div>
  </div>
</section>

{mix_html}

<section class="section section-alt">
  <div class="wrap">
    {section_head("What we play for", "Built for any crowd")}
    {event_cards(c)}
    <div class="center reveal"><a class="btn btn-gold" href="packages/">See packages &amp; pricing</a></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="booth reveal">
      <div class="booth-copy">
        <p class="eyebrow">{e(pb['name'])}</p>
        <h2 class="display">Add a photo booth.<br><span class="gold-text">Make it an experience.</span></h2>
        <p>{e(pb['intro'])}</p>
        <div class="actions">
          <a class="btn btn-gold" href="photo-booth/">See the booths</a>
          <a class="btn btn-ghost" href="{e(pb['url'])}" {EXT}>Visit {e(pb['name'])}</a>
        </div>
      </div>
      {booth_cards(c, limit=4)}
    </div>
  </div>
</section>

{dates_html}
{social_feed(c)}
{request_band(c)}
{cta_band(c, "")}"""
    return page(c, title=f"{site['name']} | Open Format DJ in Los Angeles", description=c["bio"]["short"],
                base="", path="", body=body)


def mixes(c: dict) -> str:
    cards = "".join(mix_card(m) for m in c["mixes"])
    mixcloud = next((s["url"] for s in c["socials"] if s["label"] == "Mixcloud"), "")
    body = f"""{page_hero("Mixes", 'Hear the <span class="gold-text">sound</span>', e(c["mixes_intro"]))}
<section class="section section-tight">
  <div class="wrap">
    <div class="mix-list">{cards}</div>
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
  <p class="muted">New dates land here first. Planning a private event? DJ Play is taking bookings.</p>
  <div class="actions"><a class="btn btn-gold" href="../book/">Book a date</a></div>
</div>"""
    body = f"""{page_hero("Events", 'Catch DJ Play <span class="gold-text">live</span>', "Public dates, parties and pop-ups. Private events don't show here.")}
<section class="section section-tight">
  <div class="wrap">{listing}</div>
</section>
{social_feed(c)}
{cta_band(c, "../")}"""
    return page(c, title=f"Events | {c['site']['name']}", description="Upcoming DJ Play dates and events in Southern California.",
                base="../", path="events/", body=body)


def packages(c: dict) -> str:
    body = f"""{page_hero("Packages & Pricing", 'Pick your <span class="gold-text">package</span>', e(c["packages_intro"]))}
<section class="section section-tight">
  <div class="wrap">
    {package_cards(c, "../")}
    {addons(c)}
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    {section_head("What we play for", "Built for any crowd")}
    {event_cards(c)}
  </div>
</section>

<section class="section">
  <div class="wrap faq-grid">
    {section_head("FAQ", "Good to know")}
    {faq(c)}
  </div>
</section>
{cta_band(c, "../")}"""
    return page(c, title=f"Packages & Pricing | {c['site']['name']}",
                description="DJ Play packages for weddings, parties, church and corporate events in Los Angeles. Silver, Gold and Diamond, plus add-ons.",
                base="../", path="packages/", body=body)


def photo_booth(c: dict) -> str:
    pb = c["photobooth"]
    body = f"""{page_hero(pb["name"], 'Add a photo booth.<br><span class="gold-text">Make it an experience.</span>', e(pb["intro"]))}
<section class="section section-tight">
  <div class="wrap">
    <div class="actions reveal">
      <a class="btn btn-gold" href="../book/?service=booth">Book a photo booth</a>
      <a class="btn btn-ghost" href="{e(pb['url'])}" {EXT}>Visit {e(pb['name'])}</a>
      <a class="btn btn-ghost" href="{e(pb['pricing_url'])}" {EXT}>Full booth pricing</a>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    {section_head("The booths", "Pick your booth", "Starting prices from " + pb["name"] + ". See their site for full package details.")}
    <div class="reveal">{booth_cards(c, book_base="../")}</div>
    <div class="also reveal">
      <p class="eyebrow">Also available</p>
      {tags(pb['also'])}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap bundle reveal">
    <div>
      <p class="eyebrow">Music + photo booth</p>
      <h2 class="display">One booking. <span class="gold-text">Both covered.</span></h2>
      <p class="body-copy">Planning a wedding, birthday or company party? Book DJ Play and a booth together and plan both in one go. Pick DJ + photo booth on the booking form and we'll quote both.</p>
    </div>
    <div class="actions">
      <a class="btn btn-gold" href="../book/?service=both">Book DJ + photo booth</a>
      <a class="btn btn-ghost" href="../book/?service=booth">Book a booth only</a>
    </div>
  </div>
</section>"""
    return page(c, title=f"Photo Booth | {c['site']['name']} x {pb['name']}",
                description=f"Add a photo booth from {pb['name']} to your DJ Play booking: 360, glam, open air, enclosed, magazine and digital booths.",
                base="../", path="photo-booth/", body=body)


def about(c: dict) -> str:
    site, ct = c["site"], c["contact"]
    long_bio = "".join(f'<p class="body-copy">{e(p)}</p>' for p in c["bio"]["long"])
    body = f"""{page_hero("About", f'{e(site["full_name"].split()[0])} &ldquo;<span class="gold-text">{e(site["name"])}</span>&rdquo; {e(site["full_name"].split()[-1])}', e(site["tagline"]))}
<section class="section section-tight">
  <div class="wrap about-page">
    <div class="reveal">
      {long_bio}
      <div class="actions">
        <a class="btn btn-gold" href="../book/">Book DJ Play</a>
        <a class="btn btn-ghost" href="{e(ct['instagram_url'])}" {EXT}>Follow {e(ct['instagram_handle'])}</a>
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
      <p class="body-copy">Open format means the music follows the room. Expect golden-era hip-hop and funk at the core, with R&amp;B, old school, throwbacks, Top 40 and gospel when the crowd calls for it.</p>
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
        <a class="contact-row" href="tel:{e(ct['phone_href'])}"><span class="contact-label">Call or text</span><span class="contact-value">{e(ct['phone'])}</span></a>
        <a class="contact-row" href="mailto:{e(ct['email'])}?subject=DJ%20Play%20booking%20inquiry"><span class="contact-label">Email</span><span class="contact-value">{e(ct['email'])}</span></a>
        <a class="contact-row" href="{e(ct['instagram_url'])}" {EXT}><span class="contact-label">DM on Instagram</span><span class="contact-value">{e(ct['instagram_handle'])}</span></a>
      </div>
      <p class="contact-label area-label">Serving</p>
      {tags(b['service_area'])}
    </div>
    <div class="form-card reveal">
      <h2 class="display">Booking request</h2>
      {booking_form(c)}
    </div>
  </div>
</section>"""
    return page(c, title=f"Book | {c['site']['name']}",
                description="Book DJ Play for your wedding, party, church or corporate event in Los Angeles and Orange County.",
                base="../", path="book/", body=body)


def not_found(c: dict) -> str:
    # GitHub Pages serves this for any missing path at any depth, so links use the absolute site URL.
    base = c["site"]["url"]
    body = f"""{page_hero("404", 'Track <span class="gold-text">not found</span>', "That page skipped. Let's get you back on the floor.")}
<section class="section section-tight">
  <div class="wrap"><div class="actions"><a class="btn btn-gold" href="{base}">Back to home</a><a class="btn btn-ghost" href="{base}book/">Book DJ Play</a></div></div>
</section>"""
    return page(c, title=f"Page not found | {c['site']['name']}", description="Page not found.",
                base=base, path="404.html", body=body)


# ----------------------------------------------------------------------- main

PAGES = {
    "index.html": home,
    "mixes/index.html": mixes,
    "events/index.html": events,
    "packages/index.html": packages,
    "photo-booth/index.html": photo_booth,
    "about/index.html": about,
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
