import json
from pathlib import Path

from run_harness import evaluate_pair, load_corpus


def test_frozen_corpus_is_complete_and_scored():
    path, corpus = load_corpus()
    assert path.name == "frozen_corpus.json"
    assert len(corpus) == 15
    assert all("isContradiction" in item for item in corpus)


def test_frozen_corpus_accuracy_is_reproducible():
    _, corpus = load_corpus()
    correct = sum(
        evaluate_pair(item["premise"], item["hypothesis"])["prediction"]
        == item["isContradiction"]
        for item in corpus
    )
    assert correct == 15


def test_positive_results_are_auditable():
    _, corpus = load_corpus()
    for item in corpus:
        result = evaluate_pair(item["premise"], item["hypothesis"])
        if result["prediction"]:
            assert result["rule_family"] != "no_structured_conflict_detected"
            assert result["reason"]
            assert isinstance(result["facts"], dict)
