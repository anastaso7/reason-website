# Reason Fitness Concept website

- `public/` is the built site that Netlify publishes (EN at `/`, EL at `/el/`).
- `reason/project/Main.dc.html` holds the texts, prices and schedule (COPY and LISTS blocks).
- Rebuild: `cd site && node vals.js && SITE_URL=https://reason-fitness-concept.netlify.app python3 build.py`, then copy `site/dist` to `public/`.
