# Frontend QA Report

This document records the verification matrix, responsive layout testing, accessibility audits, and Lighthouse scores for the SkillGraph web client.

## 1. Test Matrix

| Case | Expected | Actual | Fix Commit |
| :--- | :--- | :--- | :--- |
| 1. 1 skill | Submit stays disabled with a hint. | Submit button remained disabled. `#submit-reason` displayed hint: "Add 1 more skill to continue, one skill isn't enough to compare against postings." | 377f56f |
| 2. 2 skills | Works and renders results. | Selecting 2 skills (Python, SQL) with Backend role enabled submit; submitting loaded results view. | 377f56f |
| 3. 20 skills | Layout holds, chips wrap. | Added 20 skills; chips wrapped within container with zero horizontal overflow (`scrollWidth` = `clientWidth` = 1280 px). | 377f56f |
| 4. 31st skill | Input refuses it with a message. | Attempting to add 31st skill was rejected; count remained 30 and alert message displayed: "You can add up to 30 skills. Remove one before adding more." | 377f56f |
| 5. 60-character skill name | Chip truncates with an ellipsis, full name on hover. | 60-character skill truncated via CSS ellipsis; full skill name was present in the `title` attribute for native hover tooltip. | 377f56f |
| 6. "Python" then "python" | The second is ignored. | "Python" added first; typing "python" was detected as existing and ignored without creating a duplicate chip. | 377f56f |
| 7. Role Mobile with android, kotlin | Results render. | Selected Mobile role with skills android and kotlin; `/api/analyze` returned 200 OK and rendered readiness score and recommendations. | 377f56f |
| 8. Only unknown skills | Error state, never a blank screen. | Submitting unrecognized skills returned 400 Bad Request; displayed error card with title "We couldn't recognize your skills", listed unrecognized skills, and provided retry and edit actions. | 377f56f |
| 9. API stopped | Error and Retry. Restart the API, Retry works. | When API server was stopped, error card with "Try again" appeared; restarting uvicorn on port 8000 and clicking "Try again" recovered and rendered results. | 377f56f |
| 10. Slow API | Add temporary 30 s sleep to `/api/analyze` locally (never commit it). Timeout message appears after 25 s. Remove the sleep. | Added temporary `time.sleep(30)` to `/api/analyze` in `api/main.py`. Timeout message appeared at 25.5 seconds: "The server didn't respond within 25 seconds. This sometimes happens right after it wakes up - trying again usually works." Removed sleep before commit. | 377f56f |
| 11. Edit chips after results and resubmit | Results replace, no stale panels. | Clicked "Edit my answers", added flutter, and resubmitted; results view re-rendered with new figures and no stale panels. | 377f56f |
| 12. Double-click submit | Exactly one network request. | Submission guarded with submission lock ref; rapid double-click dispatched exactly 1 network request to `/api/analyze`. | 377f56f |

## 2. Responsive Layout Verification

Tested across four target viewports using automated Playwright browser execution:

- **375 px**: `scrollWidth` = 375 px, `clientWidth` = 375 px. No horizontal scrolling. All interactive tap targets measured at least 44 px by 44 px.
- **390 px**: `scrollWidth` = 390 px, `clientWidth` = 390 px. No horizontal scrolling. All interactive tap targets measured at least 44 px by 44 px.
- **768 px**: `scrollWidth` = 768 px, `clientWidth` = 768 px. No horizontal scrolling. Grid layout shifted to tablet two-column arrangement without text overlaps.
- **1280 px**: `scrollWidth` = 1280 px, `clientWidth` = 1280 px. No horizontal scrolling. Layout balanced with desktop proportions.

## 3. Accessibility Verification

- **Form Labels**: Every input element has an explicit accessible label (`label[for]` or wrapped parent label). Checked 11 input elements with 0 missing labels.
- **Live Regions**: The results section container has `aria-live="polite"` (`#results-region`). Status messages and input limit warnings also announce through live regions.
- **Focus Management**: Focus moves to the results heading (`#results-region h1`, `tabIndex={-1}`) upon submission.
- **Focus Rings**: Defined `:focus-visible` outline styles with 2 px solid accent color and 2 px offset across all focusable elements in `src/index.css`.
- **Color Contrast**: Base ink colors tuned in `src/index.css` (`--color-ink-2: #3e4e5b` and `--color-ink-3: #52606d`) to satisfy WCAG AA contrast ratio (> 5.5:1 against `#f8f8f6`).

## 4. Lighthouse Audit Scores

Ran against production build (`npm run build && npx vite preview --port 4173`) using Google Lighthouse CLI (v13.5.0):

- **Performance**: 90
- **Accessibility**: 100
- **Best Practices**: 100

Commands executed:
```bash
npm run build
npx vite preview --port 4173
npx -y lighthouse http://localhost:4173 --no-enable-error-reporting --output=json --output-path=frontend/lighthouse-report.json --chrome-flags="--headless" --only-categories=performance,accessibility,best-practices
```

## 5. Copy and Assets

- Cleaned up copy: no lorem ipsum, no placeholder names, and no console.log statements.
- Page title set to "SkillGraph" in `frontend/index.html`.
- Added SVG favicon at `frontend/public/favicon.svg` and linked via `<link rel="icon" type="image/svg+xml" href="/favicon.svg" />`.
- Refreshed all 6 persona screenshots in `docs/screenshots/` across desktop and mobile viewports.
