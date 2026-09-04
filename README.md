# Cliffs to Clouds

A cinematic, mobile-first trip site for the Tirupati → Varkala → Ponmudi → Munroe Island → Palaruvi road trip, 5–9 September 2026.

## Open locally

The finished static site lives in `dist/`. Serve that directory with any local static server; opening `dist/index.html` directly also works.

## Publish with GitHub Pages

1. Push this project to a GitHub repository with `main` as the default branch.
2. Open **Settings → Pages**.
3. Under **Build and deployment**, choose **GitHub Actions**.
4. Run the included **Deploy Cliffs to Clouds** workflow, or push another commit to `main`.

All site links are relative, so the same files work at a repository subpath, a custom domain, or another static host.

## Content

- `dist/index.html` — cinematic trip overview
- `dist/trip-book.html` — complete animated five-day itinerary
- `dist/trip-book.css` and `dist/trip-book.js` — Trip Book layout, scroll motion and interactive readiness checks
- `dist/styles.css` — responsive visual system and motion
- `dist/app.js` — journey scenes, budget calculator, checklist and sharing
- `dist/assets/Cliffs-to-Clouds-Detailed-Trip-Book.pdf` — downloadable 11-page offline plan
- `dist/assets/` — optimized destination imagery and trip document

The budget defaults to the ₹10,000 vehicle-and-driver arrangement. Visitors can switch between ₹0, ₹5,000, ₹8,000 and ₹10,000 scenarios. The detailed plan uses the ₹45,000 ceiling case and treats Palaruvi as a weather-dependent return stop.
