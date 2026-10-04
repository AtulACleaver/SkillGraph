import os
import urllib.error
import urllib.request

os.makedirs('artifacts', exist_ok=True)

files = {
    'rules-v1': ['rules.parquet'],
    'model-v3': [
        'classifier.pkl', 'label_encoder.pkl', 'role_profiles.json',
        'skills_autocomplete.json', 'skill_vocab.json'
    ]
}

for release, filenames in files.items():
    for filename in filenames:
        url = f"https://github.com/AtulACleaver/SkillGraph/releases/download/{release}/{filename}"
        print(f"Downloading {filename} from {release}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(os.path.join('artifacts', filename), 'wb') as f:
                f.write(response.read())
        except urllib.error.URLError as e:
            print(f"Failed to download {filename}: {e}")

print("Done fetching artifacts!")
