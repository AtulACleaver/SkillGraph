import json
import pandas as pd
import os

def generate_autocomplete():
    print("Generating skills_autocomplete.json...")
    
    with open('artifacts/skill_vocab.json', 'r') as f:
        vocab = json.load(f)
        
    try:
        aliases_df = pd.read_csv('taxonomy/skill_aliases.csv')
        has_aliases = True
    except FileNotFoundError:
        has_aliases = False

    autocomplete_list = []
    
    # vocab is a list of canonical skill names
    if isinstance(vocab, list):
        items = vocab
    else:
        items = list(vocab.keys())
        
    for name in items:
        entry = {
            "name": name.title(),
            "aliases": []
        }
        if has_aliases:
            # Find aliases where the canonical mapping equals this name
            matches = aliases_df[aliases_df['canonical'] == name]['alias']
            entry['aliases'] = matches.tolist()
            
        autocomplete_list.append(entry)
        
    os.makedirs('artifacts', exist_ok=True)
    with open('artifacts/skills_autocomplete.json', 'w') as f:
        json.dump(autocomplete_list, f, indent=2)
        
    print(f"Generated {len(autocomplete_list)} autocomplete entries.")

if __name__ == "__main__":
    generate_autocomplete()
