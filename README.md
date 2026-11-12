# openadoptionproject.org

The website for The Open Adoption Project podcast.

- `build.py` builds every page into `dist/` from `feed.json`, `data/transcripts/` and `data/posts.json`.
- `fetch_feed.py` refreshes `feed.json` from the RSS.com feed.
- `.github/workflows/build.yml` runs both every day and publishes to GitHub Pages, so new episodes appear on their own.
- Design files live in `src/` (`style.css`, `app.js`).

To add a transcript for a new episode, drop a text file into `data/transcripts/` named like the others.
