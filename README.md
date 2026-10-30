# DJ Play: wedding and corporate DJ site

Booking site for DJ Play (Dawaun Lucas), a wedding and corporate event DJ and MC in Los Angeles, and part of [Picture This Booth LA](https://picturethisboothla.com/).

**Live site:** https://tawaunl.github.io/djplay/

## Pages

| Page | Path | What's on it |
| --- | --- | --- |
| Home | `/` | Hero, weddings and corporate features, why DJ Play, about, photo booth promo, upcoming dates, Instagram feed |
| Weddings | `/weddings/` | The day timeline, wedding packages, planning process, photo booth, FAQ |
| Corporate | `/corporate/` | What you get, event types, recommended package, branded photo booth, FAQ |
| Packages | `/packages/` | Wedding packages, event packages, add-ons, FAQ |
| Photo Booth | `/photo-booth/` | Every booth with starting prices and a "Book this booth" link |
| Mixes | `/mixes/` | Mixcloud players and song requests |
| Events | `/events/` | Upcoming public dates and the Instagram feed |
| About | `/about/` | Bio, stats, sound, service area |
| Book | `/book/` | Booking request form for DJ, photo booth, or both |

## Edit content

All copy lives in [`content.json`](content.json). Edit it, then rebuild.

- **Upcoming events:** add entries to `dates` (format in `_dates_help`). Past dates hide automatically, and the site rebuilds daily.
- **Instagram feed:** for a live feed, create a free feed at [behold.so](https://behold.so), connect @djplay310, and paste the feed ID into `social_feed.behold_feed_id`. Or list post URLs in `social_feed.instagram_posts`. With both empty, a Follow card shows.
- **Booking form:** with `booking.form_endpoint` empty, the form opens the visitor's email app with the request filled in. To receive requests straight from the site, create a free form at [formspree.io](https://formspree.io) and paste its URL there.
- **Mixes:** add to `mixes`. `embed` takes a Mixcloud or SoundCloud player URL.
- **Packages and prices:** `weddings.packages`, `packages` and `addons`.

Booking links can prefill the form, for example `book/?type=Wedding&package=Signature%20(wedding)` or `book/?service=booth&booth=Glam%20Booth`.

## Build and preview

```bash
./build.py
python3 -m http.server -d dist 8000   # open http://localhost:8000
```

Python 3.9+ standard library only. Output goes to `dist/` (not committed).

## Deploy

`.github/workflows/pages.yml` builds the site and publishes it to GitHub Pages on every push to `main`, and once a day.

One-time setup: in the repo on GitHub go to **Settings → Pages** and set **Source** to **GitHub Actions**.

To use a custom domain, add it under Settings → Pages, point the domain's DNS at GitHub Pages, and update `site.url` in `content.json`.
