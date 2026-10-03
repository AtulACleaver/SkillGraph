# Model: Role Predictor and Readiness

The model's purpose is to take a set of tech skills and predict the most likely role family. 
By treating each job posting as a "skill profile" of a role, we converted the problem of "readiness" into a multiclass classification problem.

## Model Choice and Calibration
We trained a **Multinomial Logistic Regression** model. We compared this baseline to a LightGBM challenger.
The logistic regression was chosen because:
1. **Calibrated Probabilities**: A probability of 0.7 from a logistic regression maps closely to 70% confidence. This is critical because the UI displays this probability as "Readiness". LightGBM often produces uncalibrated probabilities.
2. **Speed and Sparsity**: Training logistic regression on sparse multi-hot vectors is extremely fast (under 2 seconds).

## The Augmentation Trick
Training data comes from job postings, which often contain up to 8 skill tags.
Users are students who typically input 3 to 6 skills.
If we trained only on the full job postings, the model would be overconfident on short inputs.
To address this distribution shift, we augmented the training data by creating shortened versions of the skill lists (keeping a random 40%, 60%, and 80% of skills). This forces the model to recognize roles from partial signals.

## Evaluation
- **Baseline Accuracy**: ~67.1% (Test Set)
- **Top-3 Accuracy**: ~90.6%
- **Thresholds**: 
  - Ready: >= 60%
  - Close: 30% - 60%
  - Not Yet: < 30%

### Limitations
1. Postings describe what employers *ask for*, not what the hired person actually knew.
2. The dataset caps skill tags at 8 tokens, meaning every training row is a truncated view. Absence of a skill tag does not mean the employer didn't want it. This caps the possible accuracy ceiling.
