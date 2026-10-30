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

- `content.json`: all site copy. Edit this, not the generated HTML.
- `build.py`: renders `dist/` from `content.json` and `static/` (standard library only). One function per page.
- `static/`: CSS, JS and images copied into `dist/` as-is.
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
- **Links:** Instagram [@djplay310](https://www.instagram.com/djplay310/), [Mixcloud](https://www.mixcloud.com/Djplay310/), [Linktree](https://linktr.ee/Djplay310), song requests at app.nosongrequests.com/Djplay. Contact: 626-766-0877, picturethisphotoboothla@gmail.com.

## Brand

- **Colors:** gold (`#ffd21f` and a gold gradient) on near-black, from the gold play-button logo in `static/assets/img/logo.jpg`.
- **Type:** Barlow Condensed italic for display, Barlow for body. Play-button triangles as the recurring motif.

## Writing style

- Clear, confident and warm. Written for couples, planners and corporate event organizers.
- Don't use em dashes. Use commas, periods, or colons.
- Don't invent facts (venues, clients, reviews, stats, quotes). Leave a TODO instead.
