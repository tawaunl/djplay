# CLAUDE.md

Notes for Claude Code (and other AI agents) working in this repo.

## Authorship: Tawaun only

Never list Claude as an author, co-author, or contributor anywhere in this repo.

- Before your first commit, set the git identity for this repo:
  `git config user.name "Tawaun Lucas"` and
  `git config user.email "86265976+tawaunl@users.noreply.github.com"`.
- No `Co-Authored-By: Claude`, `Claude-Session:`, or any other Claude trailer in commit messages.
- No "Generated with Claude Code" (or similar) line in PR titles, descriptions, or comments.

## Layout

- `content/*.json`: all site copy, one file per topic. Edit these, not the generated HTML. `build.py` merges them into one dict (top-level keys must be unique across files).
- `.pages.yml`: Pages CMS editor config. Every key in every content file must have a matching field here (use `hidden: true` for ones the owner shouldn't edit), so CMS saves never drop data. When you add or rename a content key, update `.pages.yml` in the same change. Dawaun (not a coder) edits content through Pages CMS, so `git pull` before editing content by hand.
- `build.py`: renders `dist/` from `content/` and `static/` (standard library only). One function per page. Phone `tel:` links, Mixcloud players and the booking form's package choices are derived, not stored.
- `static/`: CSS, JS and images copied into `dist/` as-is.
- `art/`: gold line-art gear illustrations (turntable, mixer, controller, speakers), inlined into pages by `gear()` so CSS can animate them.
- `.github/workflows/pages.yml`: builds and deploys to GitHub Pages on push to `main` and daily. The site lives at https://tawaunl.github.io/djplay/, so all links are relative (no leading `/`), except `404.html`, which uses `site.url`.

## Before you finish a change

```bash
./build.py
python3 -m http.server -d dist 8000   # check http://localhost:8000 at desktop and phone widths
```

## About DJ Play

- **Who:** Dawaun Lucas, DJing as **DJ Play**. From Compton, mixing since 2008, 15+ years of events. Open format, DJ and MC.
- **Focus:** weddings and corporate events first. Also private parties, church and gospel events, community events.
- **Business:** part of Picture This Booth LA (picturethisboothla.com), a photo booth rental company. The site promotes the booths and books them through the same form. Packages and prices come from their DJ and wedding DJ pages.
- **Links:** Instagram [@djplay310](https://www.instagram.com/djplay310/), [Mixcloud](https://www.mixcloud.com/Djplay310/), [Linktree](https://linktr.ee/Djplay310), song requests at app.nosongrequests.com/Djplay. Phones: DJ bookings 310-933-2227 (`contact.phone`), photo booth 626-766-0877 (`photobooth.phone`). Email: picturethisphotoboothla@gmail.com.

## Brand

- **Colors:** gold (`#ffd21f` and a gold gradient) on near-black, from the gold play-button logo in `static/assets/img/logo.jpg`.
- **Type:** Cormorant Garamond for display (light, elegant serif), Jost for body and small uppercase labels, Great Vibes script for the gold accent words in headings (`.display .gold-text`). Play-button triangles as the recurring motif.

## Writing style

- Clear, confident and warm. Written for couples, planners and corporate event organizers.
- Don't use em dashes. Use commas, periods, or colons.
- Don't invent facts (venues, clients, reviews, stats, quotes). Leave a TODO instead.
