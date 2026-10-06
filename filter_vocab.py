import json

with open('artifacts/skill_vocab.json') as f:
    vocab = json.load(f)

keywords = ['development', 'developer', 'engineer', 'manager', 'fullstack', 'full stack', 'backend', 'frontend', 'front end', 'stack', 'sr', 'senior', 'data analyst', 'data science', 'ai', 'ml', 'devops', 'data', 'boot', 'end', 'front', 'part time', 's', 'part', 'machine', 'bricks', 'core', 'administration', 'application', 'software', 'engineering', 'operations', 'production', 'programming', 'writing', 'qa', 'qc', 'architect']

results = []
for v in vocab:
    if any(k == v or k in v.split() or (k in v and k in ['fullstack', 'backend', 'frontend', 'development']) for k in keywords) or v in ['ml', 'ai', 'devops', 'backend', 'full stack', 'data', 'front end', 'frontend', 'boot', 'stack', 'mern stack', 'qa', 'qc', 'sdet', 'architect', 'sr', 'senior', 's', 'part', 'front', 'end', 'core', 'bricks', 'machine', 'automation']:
        results.append(v)

for r in sorted(set(results)):
    print(r)
