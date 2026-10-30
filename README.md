# DJ Play: wedding and corporate DJ site

Booking site for DJ Play (Dawaun Lucas), a wedding and corporate event DJ and MC in Los Angeles, and part of [Picture This Booth LA](https://picturethisboothla.com/).

**Live site:** https://tawaunl.github.io/djplay/

## Pages

| Page | Path | What's on it |
| --- | --- | --- |
| Home | `/` | Hero, weddings and corporate features, why DJ Play, about, featured mixes, photo booth promo, upcoming dates, Instagram feed |
| Weddings | `/weddings/` | The day timeline, wedding packages, planning process, photo booth, FAQ |
| Corporate | `/corporate/` | What you get, event types, recommended package, branded photo booth, FAQ |
| Packages | `/packages/` | Wedding packages, event packages, add-ons, FAQ |
| Photo Booth | `/photo-booth/` | Every booth with starting prices and a "Book this booth" link |
| Mixes | `/mixes/` | Mixcloud players and song requests |
| Events | `/events/` | Upcoming public dates and the Instagram feed |
| About | `/about/` | Bio, stats, sound, service area |
| Press kit | `/press/` | Copyable bios, quick facts, logo downloads, mixes, gear, contacts. "Save as PDF" prints a 2-page one-sheet |
| Book | `/book/` | Booking request form for DJ, photo booth, or both |

## Edit content

All copy lives in [`content/`](content/), one JSON file per topic (events, mixes, weddings, packages, FAQ, photo booth, about, contact, social, press).

### The easy way: Pages CMS

[Pages CMS](https://pagescms.org) gives the content files a form-based editor, set up in [`.pages.yml`](.pages.yml). No code needed.

1. Go to [app.pagescms.org](https://app.pagescms.org) and sign in with GitHub.
2. Install the Pages CMS GitHub app when asked and give it access to this repo.
3. Open the repo, pick a section in the sidebar (Upcoming events, Mixes, Weddings...), edit, and click **Save**.

Each save commits to `main`, and the site updates about a minute later. To give someone else editing access, add them as a collaborator on the repo (Settings → Collaborators); they then sign in to Pages CMS with their own GitHub account.

### By hand

Edit the files in `content/` directly, then rebuild. If you add a new key to a content file, add a matching field to `.pages.yml` so it shows up in Pages CMS. Run `git pull` first if someone may have saved from Pages CMS.

### Notes

- **Upcoming events:** past dates hide automatically, and the site rebuilds daily.
- **Mixes:** paste the Mixcloud link. The player is added automatically. The first two also show on the home page.
- **Instagram feed:** for a live feed, create a free feed at [behold.so](https://behold.so), connect @djplay310, and paste the feed ID under Social & feed. Or list post links to embed specific posts. With both empty, a Follow card shows.
- **Booking form:** with no Formspree link set, the form opens the visitor's email app with the request filled in. To receive requests straight from the site, create a free form at [formspree.io](https://formspree.io) and paste its link under Contact & booking. The form's package choices come from the package lists automatically.
- **FAQ:** every question shows on the Packages page. Each has checkboxes to also show it on the Weddings or Corporate page.
- **Press kit:** add press photos and venue requirements. Both sections stay hidden while empty. Uploaded images go to `static/assets/img/uploads/`.
- **Phone numbers:** DJ bookings use the phone under Contact & booking; photo booth spots use the phone under Photo booth.

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

To use a custom domain, add it under Settings → Pages, point the domain's DNS at GitHub Pages, and update `site.url` in `content/about.json` (hidden from Pages CMS, so edit it by hand).
