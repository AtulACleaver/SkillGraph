# SkillGraph frontend

React + Vite (JavaScript), Tailwind CSS v4 (`@tailwindcss/vite`, tokens in `src/index.css` `@theme`), axios, lucide-react.

## Run it

1. `cd frontend && npm install`
2. `cp .env.example .env`, then set `VITE_API_URL` to your API (no trailing slash)
3. To run without a backend, set `VITE_USE_MOCK=true` (fixtures in `src/api/mock.js`, 600 ms delay)
4. `npm run dev`, then open http://localhost:5173
5. `npm run build && npm run preview` to check the production bundle

## Mock-mode scenarios

Append these to the URL while `VITE_USE_MOCK=true`:

- `?mock=slow` makes /analyze take 9 s, so the "server is waking up" message appears after 5 s
- `?mock=error` makes the first /analyze time out; Try again resends the same payload and succeeds
- `?mock=offline` makes /roles fail on first load; it auto-retries after 15 s, or click Try again now

`src/api/mock.js` lists skill + role combinations that give a lopsided result, an empty gap list, a chosen role missing from the top 3, and unrecognized skills.

## Notes

- **Base URL:** read only from `import.meta.env.VITE_API_URL`; it is never hardcoded.
- **Request timeout:** 45 s. Raw errors are mapped to readable copy in `toFriendlyError`.
- **Readiness change:** shown as `readiness.probability → readiness.probability + readiness_gain`, rounded to whole percent.
- **`coverage_pct`:** expected as a 0–1 share; a 0–100 value is also handled.
