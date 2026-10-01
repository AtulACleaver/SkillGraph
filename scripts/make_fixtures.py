import os
import json
import random
import pickle
import pandas as pd
import numpy as np

class FakePredictor:
    def __init__(self, classes):
        self.classes_ = np.array(classes)
        
    def predict_proba(self, X):
        n_samples = getattr(X, 'shape', [1])[0] if hasattr(X, 'shape') else len(X) if isinstance(X, list) else 1
        probs = np.random.dirichlet(np.ones(len(self.classes_)) * 0.5, size=n_samples)
        return probs
        
    def predict(self, X):
        probs = self.predict_proba(X)
        indices = np.argmax(probs, axis=1)
        return self.classes_[indices]

class FakeLabelEncoder:
    def __init__(self, classes):
        self.classes_ = np.array(classes)
        
    def transform(self, y):
        return np.array([list(self.classes_).index(item) for item in y])
        
    def inverse_transform(self, y):
        return self.classes_[y]

def create_fixtures(output_dir="fixtures"):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. skill_vocab.json - 40 real-sounding skills
    skills = [
        "Python", "Java", "C++", "JavaScript", "TypeScript", "React", "Angular",
        "Vue.js", "Node.js", "Django", "Flask", "FastAPI", "Spring Boot",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform",
        "Jenkins", "Git", "Linux", "Bash", "Machine Learning", "Deep Learning",
        "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "Data Analysis",
        "Data Engineering", "Apache Spark", "Apache Kafka"
    ]
    
    # Map each skill to an ID
    skill_vocab = {skill.lower(): i for i, skill in enumerate(skills)}
    
    with open(os.path.join(output_dir, "skill_vocab.json"), "w") as f:
        json.dump(skill_vocab, f, indent=4)
        
    # 2. role_profiles.json - 6 role families and their top skills
    role_families = [
        "Software Engineer", 
        "Data Scientist", 
        "Data Engineer", 
        "Frontend Developer", 
        "Backend Developer", 
        "DevOps Engineer"
    ]
    
    role_profiles = {}
    for role in role_families:
        num_skills = random.randint(5, 10)
        role_skills = random.sample(skills, num_skills)
        role_profiles[role] = {
            "n_postings": random.randint(500, 5000),
            "top_skills": role_skills
        }
        
    with open(os.path.join(output_dir, "role_profiles.json"), "w") as f:
        json.dump(role_profiles, f, indent=4)
        
    # 3. rules.parquet - 200 plausible rules
    rules_data = []
    for _ in range(200):
        skill = random.choice(skills)
        role = random.choice(role_families)
        learn_with = random.sample([s for s in skills if s != skill], k=random.randint(1, 3))
        rules_data.append({
            "skill": skill,
            "role": role,
            "coverage_pct": round(random.uniform(0.1, 0.9), 2),
            "readiness_gain": round(random.uniform(0.05, 0.3), 2),
            "learn_with": learn_with
        })
        
    df = pd.DataFrame(rules_data)
    df.to_parquet(os.path.join(output_dir, "rules.parquet"))
    
    # 4. Predictor and Label Encoder
    predictor = FakePredictor(role_families)
    with open(os.path.join(output_dir, "classifier.pkl"), "wb") as f:
        pickle.dump(predictor, f)
        
    label_encoder = FakeLabelEncoder(role_families)
    with open(os.path.join(output_dir, "label_encoder.pkl"), "wb") as f:
        pickle.dump(label_encoder, f)

    print("✅ Fixtures generated successfully in 'fixtures/' directory!")

if __name__ == "__main__":
    create_fixtures()
