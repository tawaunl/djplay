# DJ Play

Website for DJ Play (Dawaun Lucas), an open-format DJ and MC based in So-Cal.

It's a static site (`index.html`, `styles.css`, `script.js`, `assets/`) with no build step, hosted on GitHub Pages.

## Preview locally

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploy

1. Push to `main`.
2. In the repo on GitHub go to **Settings → Pages**.
3. Under **Build and deployment**, set Source to **Deploy from a branch**, branch `main`, folder `/ (root)`.
4. The site goes live at https://tawaunl.github.io/djplay/ within a minute or two.

To use a custom domain, add it under Settings → Pages and point the domain's DNS at GitHub Pages.

## Editing content

All copy is in `index.html`, one `<section>` per block: hero, mixes, about, events, packages, photo booth, song request, book. Prices for packages and add-ons are in the `#packages` section.
