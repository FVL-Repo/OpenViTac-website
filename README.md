# OpenViTac project website

A responsive, dependency-free academic project page using the supplied paper figures and local fonts. Built for GitHub Pages with relative asset paths; no build step or external font/CDN requests are required.

## Preview

```sh
npm run dev
```

Open http://127.0.0.1:4173. Set the `PORT` environment variable if needed. `npm run check` verifies JavaScript syntax. Opening `index.html` directly also works; clipboard access depends on the browser, with a text-selection fallback.

## Release links and videos

Edit `site-config.js`:

- `resources`: GitHub is set to `https://github.com/FVL-Repo/OpenViTac`. Add the official Paper, Hugging Face, and ModelScope URLs when available. Empty URLs intentionally show a non-clickable **Coming soon** state.
- `demos`: add a local MP4/WebM file (for example `assets/videos/insert-usb.mp4`) or direct video URL to `src`. The placeholder becomes a native player automatically. `poster` is an optional image; `captions` is an optional English WebVTT file. Videos do not autoplay. YouTube watch pages are not direct video URLs.
- Demo slots cover the four capability groups. Add or remove entries as needed.

## Content

- `index.html`: title, authors, affiliations, narrative, figure captions, and preliminary BibTeX.
- `app.js`: 11 tasks, four filters, simulation/real result tables, citation copy, and media rendering.
- `styles.css`: responsive layout, locally hosted Space Grotesk and IBM Plex Mono, a fixed light theme, keyboard focus, reduced-motion support, and print styles.
- `assets/`: supplied figures, task sequences, fonts, and a small favicon. WebP previews reduce the total image payload by approximately 63%; figure links still open the original PNG/JPG files at full resolution.

Content is based on `../main.tex`, `../sec/3_method.tex`, and `../sec/4_experiments.tex`. Do not use the unrelated website URL or old appendix in the source manuscript. The unused affiliation 4 is omitted; the remaining author affiliation numbers are preserved. The spelling of Shanghai Innovation Institute is normalized.

The results table shows the five highest-scoring policies by default; readers can expand to all 13 simulation policies or all 9 real-world policies. Simulation covers 11 tasks, real-world evaluation covers 8. Reported averages are copied from the manuscript, and real-world fractions are converted to percentages (one decimal where needed). Pearson r = 0.913 is measured across the nine policies with complete shared-task results. These domain averages must not be interpreted as performance on identical task sets.

The BibTeX entry is explicitly preliminary: no arXiv identifier, venue, or release date has been invented. Confirm publication details before release. The GitHub link is the only confirmed release URL.

## Validation

Checked the four task filters, task detail switching, additional figures, both result domains (13 simulation / 9 real policies), expandable tables, citation copying, and the light theme. Layout checks at 320, 390, 768, and 1440 pixels found no page-level horizontal overflow. Local assets and section anchors resolve, and JavaScript syntax checks pass.

Local Lighthouse mobile audit after image optimization: Performance **97**, Accessibility **100**, Best Practices **100**, SEO **100**; LCP **2.4 s**, CLS **0.036**, TBT **0 ms**. Hosted performance can differ. Local reports and preview screenshots are in the ignored `.artifacts/` directory.

## GitHub Pages deployment

The website source remains in `FVL-Repo/OpenViTac-website`. A GitHub Actions workflow validates the JavaScript, prepares an allowlisted static artifact with `npm run build`, and publishes only that artifact to the orphan `gh-pages` branch of `FVL-Repo/OpenViTac`. The source repository and the benchmark's `main` branch therefore remain independent, while the public URL is:

```text
https://fvl-repo.github.io/OpenViTac/
```

### One-time repository setup

1. Generate a dedicated SSH key pair. Do not commit either key:

   ```sh
   ssh-keygen -t ed25519 -C "OpenViTac Pages deployment" -f openvitac-pages-key
   ```

2. In `FVL-Repo/OpenViTac`, open **Settings → Deploy keys → Add deploy key**, add `openvitac-pages-key.pub`, and enable **Allow write access**.
3. In `FVL-Repo/OpenViTac-website`, open **Settings → Secrets and variables → Actions**, create a repository secret named `OPENVITAC_PAGES_DEPLOY_KEY`, and paste the complete private key from `openvitac-pages-key`.
4. Push `main` or manually run the **Deploy OpenViTac website** workflow. This creates or updates the target `gh-pages` branch.
5. In `FVL-Repo/OpenViTac`, open **Settings → Pages**, select **Deploy from a branch**, choose `gh-pages` and `/ (root)`, then save.

Every subsequent push to `OpenViTac-website/main` automatically republishes the site. The workflow uses deployment concurrency to prevent an older run from overwriting a newer release. The generated `dist/` directory is ignored locally and must not be committed.

After choosing the final public URL, change `og:image` in `index.html` to its absolute public image URL and add a canonical link / `og:url` for reliable social sharing.

## Visual direction

Research figures are exported as transparent PNGs and WebPs from the source
`Tactilebench/figs` PDFs. To refresh them, install `pillow`, `pymupdf`, and
`pikepdf` in a Python environment, then run:

```bash
python scripts/export-figures.py /path/to/Tactilebench/figs
```

The exporter removes large white vector panels and adds transparency to the
outer white background of flattened task diagrams. Source PDFs, photos, and
small white details are preserved. Real-sim alignment removes only its page
background, preserving the white fills inside its Real-World and Simulation
labels. Tactile design and the radar plot retain their original white backgrounds.
These three figures use rounded image containers.

Research-first layout inspired by the organization of https://univtac.github.io/, using OpenViTac's own manuscript, imagery, and data. Centered project identity and authors lead into a full-width teaser, a selectable task viewer, illustrated methods, compact expandable results, video placeholders, and citation.

Palette: canvas `#ffffff`, surface `#f0f3fa`, text `#202a3b`, secondary `#566276`, accent `#2458b3`, rule `#d8dfeb`. Space Grotesk supplies headings; system sans-serif keeps prose easy to read; IBM Plex Mono is reserved for code and short task identifiers. Existing blue scientific figures guide the accent choice. No decorative animations or generated research imagery.
