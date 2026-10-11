# API Reference

This document provides endpoint documentation, validation rules, and sample requests and responses captured from production (`https://skillgraph-api-notionatul.vercel.app`).

## Production Base URLs

- Web Application: `https://skillgraph-exp.vercel.app`
- API Direct: `https://skillgraph-api-notionatul.vercel.app`
- Interactive OpenAPI Docs: `https://skillgraph-api-notionatul.vercel.app/docs`

The web application proxies requests from `https://skillgraph-exp.vercel.app/api/*` to the API domain via Vercel rewrites.

## Input Constraints and Validations

- Maximum skills per request: 30 skills (`api/schemas.py`).
- Maximum characters per skill: 60 characters.
- Empty skills list: Returns HTTP 400 with detail message.
- All-unrecognized skills: Returns HTTP 400 listing unrecognized inputs.
- Unknown desired role: Returns HTTP 400 listing invalid role string.

---

## Endpoints

### 1. GET `/api/health`

Returns service health, loaded artifact versions, posting count, and vocabulary size.

#### Request
```bash
curl -s "https://skillgraph-api-notionatul.vercel.app/api/health"
```

#### Response
```json
{
  "status": "ok",
  "artifacts_loaded": true,
  "n_postings": 8941,
  "n_skills": 800,
  "built_at": "2026-10-06T04:14:21Z",
  "model": "model-v4",
  "rules": "rules-v2"
}
```

---

### 2. GET `/api/roles`

Returns all 10 role families, posting counts in training data, and top 20 skills.

#### Request
```bash
curl -s "https://skillgraph-api-notionatul.vercel.app/api/roles"
```

#### Response (Truncated)
```json
[
  {
    "role_family": "DevOps / Cloud",
    "n_postings": 1584,
    "top_skills": [
      "Kubernetes",
      "AWS",
      "DevOps",
      "Python",
      "Continuous Integration",
      "Azure",
      "CI/CD",
      "Cloud",
      "Terraform",
      "Docker",
      "Java",
      "Automation",
      "SQL",
      "GCP",
      "Oracle",
      "Linux",
      "Troubleshooting",
      "Ansible",
      "Jenkins",
      "Azure DevOps"
    ]
  },
  {
    "role_family": "QA / Test",
    "n_postings": 1134,
    "top_skills": [
      "QA",
      "Selenium",
      "Java",
      "Automation",
      "Python",
      "Test Cases",
      "Quality Assurance",
      "API Testing",
      "Continuous Integration",
      "Regression Testing",
      "Performance Testing",
      "Automation Framework",
      "JavaScript",
      "SQL",
      "Quality Engineering",
      "Quality",
      "Agile",
      "CI/CD",
      "Quality Control",
      "Jira"
    ]
  }
]
```

---

### 3. GET `/api/skills?q={query}`

Provides skill autocomplete over canonical names and aliases.

#### Request
```bash
curl -s "https://skillgraph-api-notionatul.vercel.app/api/skills?q=react"
```

#### Response
```json
[
  {
    "skill_id": 9,
    "name": "React",
    "aliases": [
      "reactjs",
      "react js",
      "reacts js"
    ]
  },
  {
    "skill_id": 166,
    "name": "React Native",
    "aliases": []
  }
]
```

---

### 4. POST `/api/match`

Predicts the top matching roles from a candidate skill list.

#### Request
```bash
curl -s -X POST "https://skillgraph-api-notionatul.vercel.app/api/match" \
  -H "Content-Type: application/json" \
  -d '{"skills":["python","sql","machine learning"]}'
```

#### Response
```json
{
  "matches": [
    {
      "role": "Data Science / ML",
      "probability": 0.6305
    },
    {
      "role": "Data / BI Analyst",
      "probability": 0.1883
    },
    {
      "role": "Support / IT Ops",
      "probability": 0.0719
    }
  ],
  "unrecognized": []
}
```

---

### 5. POST `/api/readiness`

Evaluates readiness probability, qualitative band, and role coverage.

#### Request
```bash
curl -s -X POST "https://skillgraph-api-notionatul.vercel.app/api/readiness" \
  -H "Content-Type: application/json" \
  -d '{"skills":["python","sql","machine learning"],"desired_role":"Data Science / ML"}'
```

#### Response
```json
{
  "probability": 0.6305,
  "band": "Close",
  "coverage": 0.15,
  "covered": [
    "Python",
    "ML",
    "SQL"
  ],
  "missing_count": 17
}
```

---

### 6. POST `/api/gap`

Recommends the top 5 skills to learn next with companion skills.

#### Request
```bash
curl -s -X POST "https://skillgraph-api-notionatul.vercel.app/api/gap" \
  -H "Content-Type: application/json" \
  -d '{"skills":["python","sql","machine learning"],"desired_role":"Data Science / ML"}'
```

#### Response
```json
{
  "recommendations": [
    {
      "skill": "NLP",
      "coverage_pct": 0.1643,
      "readiness_gain": 0.3107,
      "learn_with": []
    },
    {
      "skill": "Generative AI",
      "coverage_pct": 0.1381,
      "readiness_gain": 0.3425,
      "learn_with": []
    },
    {
      "skill": "TensorFlow",
      "coverage_pct": 0.1202,
      "readiness_gain": 0.3356,
      "learn_with": []
    },
    {
      "skill": "Image Processing",
      "coverage_pct": 0.0798,
      "readiness_gain": 0.3562,
      "learn_with": []
    },
    {
      "skill": "PyTorch",
      "coverage_pct": 0.0881,
      "readiness_gain": 0.3139,
      "learn_with": []
    }
  ]
}
```

---

### 7. POST `/api/analyze`

Executes match, readiness, and gap ranking in a single request.

#### Request
```bash
curl -s -X POST "https://skillgraph-api-notionatul.vercel.app/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"skills":["python","sql","pandas"],"desired_role":"Data / BI Analyst"}'
```

#### Response
```json
{
  "match": {
    "matches": [
      {
        "role": "Backend",
        "probability": 0.4906
      },
      {
        "role": "Data Science / ML",
        "probability": 0.1957
      },
      {
        "role": "Data / BI Analyst",
        "probability": 0.108
      }
    ],
    "unrecognized": []
  },
  "readiness": {
    "probability": 0.108,
    "band": "Not yet",
    "coverage": 0.1,
    "covered": [
      "Python",
      "SQL"
    ],
    "missing_count": 18
  },
  "gap": {
    "recommendations": [
      {
        "skill": "Power BI",
        "coverage_pct": 0.1447,
        "readiness_gain": 0.4881,
        "learn_with": []
      },
      {
        "skill": "Data Engineering",
        "coverage_pct": 0.1583,
        "readiness_gain": 0.4357,
        "learn_with": []
      },
      {
        "skill": "PySpark",
        "coverage_pct": 0.1593,
        "readiness_gain": 0.3163,
        "learn_with": []
      },
      {
        "skill": "Data Analysis",
        "coverage_pct": 0.1583,
        "readiness_gain": 0.2766,
        "learn_with": []
      },
      {
        "skill": "Snowflake",
        "coverage_pct": 0.0943,
        "readiness_gain": 0.4271,
        "learn_with": []
      }
    ]
  }
}
```
