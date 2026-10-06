# Deployment Guide

This document describes the Vercel production deployment setup for SkillGraph, recorded on 2026-10-05.

## 1. Production URLs

- Web application: https://skillgraph-exp.vercel.app (alias: https://skillgraph-notionatul.vercel.app)
- API service: https://skillgraph-api-notionatul.vercel.app (alias: https://skillgraph-api-three.vercel.app)

The web client sends all requests to its own origin under `/api/*`. `frontend/vercel.json` rewrites these paths to the API production domain.

## 2. Project Settings

### API: skillgraph-api

- Project Name: `skillgraph-api`
- Root Directory: `.` (repo root)
- Framework Preset: FastAPI
- Runtime: Python 3.12 (specified in `.python-version`)
- Entrypoint: `app.py` (`from api.main import app`)
- Install Command: `pip install -r requirements.txt`
- Excluded Files: defined in `vercel.json` functions block to keep bundle size small and preserve `artifacts/*.json` and `taxonomy/`
- Git Connection: `https://github.com/AtulACleaver/SkillGraph` (production branch: `main`)

### Web: skillgraph

- Project Name: `skillgraph`
- Root Directory: `frontend`
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`
- Rewrites: `frontend/vercel.json` rewrites `/api/:path*` to `https://skillgraph-api-notionatul.vercel.app/api/:path*`
- Git Connection: `https://github.com/AtulACleaver/SkillGraph` (production branch: `main`)

## 3. Latency Benchmarks (Measured 2026-10-05)

Benchmarked `/api/analyze` using the payload:
`{"skills": ["python", "sql", "pandas"], "desired_role": "Data / BI Analyst"}`

- Cold start (initial invocation after fresh deployment): 2521.1 ms (2.52 s)
- Warm sequential calls (20 requests through web domain rewrite):
  - p50: 454.4 ms
  - p95: 728.8 ms
  - Min: 361.7 ms
  - Max: 1023.1 ms
  - Mean: 491.0 ms

Recorded from command:
```bash
for i in $(seq 1 20); do
  curl -w "%{time_total}\n" -o /dev/null -s -X POST "https://skillgraph-exp.vercel.app/api/analyze" \
    -H "Content-Type: application/json" \
    -d '{"skills":["python","sql","pandas"],"desired_role":"Data / BI Analyst"}'
done
```

## 4. Environment Variables

- `ALLOWED_ORIGINS`: Comma-separated list of origins allowed by CORS. Only matters for local development or cross-origin access. Not required in production because the web client uses same-origin `/api` rewrites.
- `PORT`: Set automatically by Vercel serverless environment.

## 5. How to Roll Back

### Via CLI

Run rollback inside the respective directory:

```bash
# Roll back API
vercel rollback <deployment-url>

# Roll back web frontend
cd frontend && vercel rollback <deployment-url>
```

### Via Dashboard

1. Open the project dashboard on Vercel:
   - API: `https://vercel.com/notionatul/skillgraph-api`
   - Web: `https://vercel.com/notionatul/skillgraph`
2. Open the **Deployments** tab.
3. Select the previous stable deployment.
4. Click the three dots icon (`...`) on the right.
5. Select **Promote to Production**.

## 6. How to Redeploy

### Via Git (Automated)

Both projects connect to `https://github.com/AtulACleaver/SkillGraph`. Merges or pushes to `main` trigger production deployments automatically. Pull requests receive isolated preview deployments with unique preview URLs.

### Via CLI (Manual)

To deploy directly from the CLI:

```bash
# Redeploy API
vercel deploy --prod

# Redeploy web frontend
cd frontend && vercel deploy --prod
```
