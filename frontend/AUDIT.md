# Frontend Audit

## Framework and Build Tool
- **Framework**: React 18.3.1
- **Build Tool**: Vite 6.0.7 (with Tailwind CSS plugin)

## Components and Data Shown
- **App (`App.jsx`)**: State orchestrator holding `selectedSkills`, `desiredRole`, `roles`, and `result` from the API. Renders input and results views.
- **Header / Footer (`App.jsx`)**: Displays static branding and disclaimer text.
- **SkillInput (`components/SkillInput.jsx`)**: Autocomplete for skills. Expects a list of matching skills (`{skill_id, name, aliases}`).
- **RoleSelect (`components/RoleSelect.jsx`)**: Dropdown for roles. Expects a list of roles (`{role_family, n_postings, top_skills}`).
- **ReadinessPanel (`components/ReadinessPanel.jsx`)**: Shows readiness score, band ("Ready", "Close", "Not yet"), coverage metrics, and covered core skills. Expects `probability`, `band`, `coverage`, `covered`, `missing_count`.
- **GapPanel (`components/GapPanel.jsx`)**: Shows the top missing skills to learn next. Expects `recommendations` containing `skill`, `coverage_pct`, `readiness_gain`, and `learn_with`.
- **MatchPanel (`components/MatchPanel.jsx`)**: Shows the top 3 role fits. Expects `matches` containing `role` and `probability`.
- **RoleSkillMix (`components/ui/RoleSkillMix.jsx`)**: Visualizes covered vs missing top skills for the chosen role.

## Where Data Comes From Today
Data is fetched via `frontend/src/api/client.js`, which conditionally delegates to `frontend/src/api/mock.js` based on the `VITE_USE_MOCK` environment variable. The mock file generates realistic plausible responses using hardcoded dataset fixtures (`ROLE_DATA`, `SKILLS`, `PAIRS`).

## API Calls
1. `GET /skills?q={query}` (via `searchSkills`): Fetches skill autocomplete suggestions.
2. `GET /roles` (via `getRoles`): Fetches the available role families.
3. `POST /analyze` (via `analyze`): Submits `{skills, desired_role}` and returns a combined payload for match, readiness, and gap.

## Mismatches (Design vs `/api/analyze` Contract)
| Field | Design / Mock Expectation | Real `/api/analyze` Contract | Impact / Fix Required |
|---|---|---|---|
| `gap.recommendations[].learn_with` | String or `null` | `list[str]` | The API returns an array (or empty list), but the UI (`GapPanel.jsx`) expects a single string or null/falsy for the partner skill. We must update the UI to handle arrays of strings and treat empty lists as falsy. |
