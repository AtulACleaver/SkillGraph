
import pytest

from mining.apriori import run_apriori, run_apriori_l2
from mining.gap import load_gap_artifacts, rank_gap
from mining.rules import generate_rules


def test_apriori_l2():
    # 10 baskets, 5 items to test C1 -> L1 -> C2 -> L2
    baskets = [
        ["python", "sql", "aws"],
        ["python", "sql"],
        ["sql", "aws"],
        ["python", "aws", "docker"],
        ["python", "sql", "aws", "docker"],
        ["java", "sql"],
        ["python", "java"],
        ["python", "sql", "docker"],
        ["sql", "aws", "docker"],
        ["java", "aws"],
    ]

    # min_sup_pct = 0.3 means ceil(10 * 0.3) = 3 baskets minimum
    L1, L2 = run_apriori_l2(baskets, 0.3)

    # Expected L1 items: python(6), sql(7), aws(6), docker(4), java(3)
    assert frozenset(["python"]) in L1
    assert L1[frozenset(["python"])] == 6
    assert L1[frozenset(["sql"])] == 7
    assert L1[frozenset(["aws"])] == 6
    assert L1[frozenset(["docker"])] == 4
    assert L1[frozenset(["java"])] == 3

    # Expected L2 items that occur in >= 3 baskets:
    assert L2[frozenset(["python", "sql"])] == 4
    assert L2[frozenset(["python", "aws"])] == 3
    assert L2[frozenset(["python", "docker"])] == 3
    assert L2[frozenset(["sql", "aws"])] == 4
    assert L2[frozenset(["sql", "docker"])] == 3
    assert L2[frozenset(["aws", "docker"])] == 3

    # java & sql: 1 (should not be in L2)
    assert frozenset(["java", "sql"]) not in L2

    print("Day 3 paper-test passed! The code matches the manual L1/L2 calculation.")


def test_full_apriori_k():
    baskets = [
        ["python", "sql", "aws"],
        ["python", "sql"],
        ["sql", "aws"],
        ["python", "aws", "docker"],
        ["python", "sql", "aws", "docker"],
        ["java", "sql"],
        ["python", "java"],
        ["python", "sql", "docker"],
        ["sql", "aws", "docker"],
        ["java", "aws"],
    ]

    all_frequent, stats = run_apriori(baskets, 0.3, verbose=False)

    # L1 count: 5
    assert len([k for k in all_frequent if len(k) == 1]) == 5

    # L2 count: 6
    assert len([k for k in all_frequent if len(k) == 2]) == 6

    # L3: check 3-itemsets occurring >= 3 times:
    assert len([k for k in all_frequent if len(k) == 3]) == 0

    # Ensure level stats are tracked
    assert 1 in stats
    assert 2 in stats
    assert stats[2]["candidates_generated"] == 10  # 5 choose 2 = 10
    assert stats[2]["survivors"] == 6


def test_edge_cases_apriori():
    # 1. Empty basket list
    empty_res, _ = run_apriori([], 0.1, verbose=False)
    assert len(empty_res) == 0

    # 2. Single basket
    single_res, _ = run_apriori([["python", "fastapi"]], 0.5, verbose=False)
    assert frozenset(["python"]) in single_res
    assert frozenset(["fastapi"]) in single_res
    assert frozenset(["python", "fastapi"]) in single_res

    # 3. Item present in every basket
    universal_baskets = [["python", "sql"], ["python", "docker"], ["python", "aws"]]
    univ_res, _ = run_apriori(universal_baskets, 1.0, verbose=False)
    assert frozenset(["python"]) in univ_res
    assert univ_res[frozenset(["python"])] == 3


def test_association_rules_and_lift():
    # Synthetic dataset with independent vs correlated items:
    # A (in 50/100), B (in 50/100), independent A & B co-occur in 25/100 -> Lift = 1.0
    # C and D strictly co-occur together in 40/100 -> Lift > 1.0
    baskets = []
    for i in range(100):
        b = []
        if i < 50:
            b.append("A")
        if i % 2 == 0:
            b.append("B")
        if i < 40:
            b.extend(["C", "D"])
        baskets.append(b)

    frequent_itemsets, _ = run_apriori(baskets, 0.2, verbose=False)
    rules_df = generate_rules(frequent_itemsets, total_baskets=100, min_confidence=0.1, min_lift=0.0)

    # Check rule A -> B
    rule_ab = rules_df[(rules_df["antecedent"].apply(lambda x: x == ["A"])) & (rules_df["consequent"].apply(lambda x: x == ["B"]))]
    assert not rule_ab.empty
    # Lift for independent events should be approximately 1.0
    assert abs(rule_ab.iloc[0]["lift"] - 1.0) < 0.05

    # Check rule C -> D (strongly correlated, lift >= 2.0)
    rule_cd = rules_df[(rules_df["antecedent"].apply(lambda x: x == ["C"])) & (rules_df["consequent"].apply(lambda x: x == ["D"]))]
    assert not rule_cd.empty
    assert rule_cd.iloc[0]["lift"] >= 2.0



def test_gap_ranking():
    # Test gap ranking for Backend role
    user_skills = ["python", "fastapi"]
    results = rank_gap(user_skills, desired_role="Backend", top_n=5)

    assert isinstance(results, list)
    assert len(results) <= 5
    for r in results:
        assert "skill" in r
        assert "coverage_pct" in r
        assert "readiness_gain" in r
        assert "learn_with" in r
        assert r["skill"].lower() not in user_skills

    # Cold case 1: unknown role
    with pytest.raises(ValueError, match="not found"):
        rank_gap(user_skills, desired_role="Nonexistent Role", top_n=5)

    # Cold case 2: user already has all skills in profile
    profile_top_skills = load_gap_artifacts()["role_profiles"]["Frontend"]["top_skills"]
    all_have = rank_gap(profile_top_skills, desired_role="Frontend", top_n=5)
    assert all_have == []


if __name__ == "__main__":
    test_apriori_l2()
    test_full_apriori_k()
    test_edge_cases_apriori()
    test_association_rules_and_lift()
    test_gap_ranking()
    print("All unit tests passed successfully!")
