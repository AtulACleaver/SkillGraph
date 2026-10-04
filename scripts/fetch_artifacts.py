import urllib.request
import os

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
            with urllib.request.urlopen(req) as response:
                with open(os.path.join('artifacts', filename), 'wb') as f:
                    f.write(response.read())
        except Exception as e:
            print(f"Failed to download {filename}: {e}")

print("Done fetching artifacts!")
