"""Training-set augmentation.

Job postings list ~7-8 skills, but a student typically enters only a few.
To make the classifier robust to short, partial skill lists we add copies of
each training posting with a random subset of its skills dropped.
Augmentation is applied to the TRAIN split only, never to validation/test.
"""
import numpy as np


def drop_skills(skill_id_lists, labels, n_copies: int = 2, keep_frac=(0.3, 0.7),
                min_keep: int = 2, seed: int = 42):
    """Return (augmented_skill_lists, augmented_labels), originals included."""
    rng = np.random.default_rng(seed)
    out_x, out_y = list(skill_id_lists), list(labels)
    for ids, y in zip(skill_id_lists, labels):
        ids = list(ids)
        if len(ids) <= min_keep:
            continue
        for _ in range(n_copies):
            k = max(min_keep, int(round(len(ids) * rng.uniform(*keep_frac))))
            out_x.append(list(rng.choice(ids, size=k, replace=False)))
            out_y.append(y)
    return out_x, out_y
