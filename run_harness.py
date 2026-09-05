#!/usr/bin/env python3
"""
Cranium Substrate — structured contradiction harness.

This is a deterministic rule evaluator. It is not a general-purpose NLI model.
Every positive verdict records the rule family that produced it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


CORPUS_CANDIDATES = (
    "frozen_corpus.json",
    "corpus.json",
    "test_corpus.json",
    "fixtures/frozen_corpus.json",
)


def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("—", " ").replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def lexical_opposition(premise: str, hypothesis: str) -> dict[str, Any] | None:
    oppositions = (
        ("always", "never"),
        ("never", "always"),
        ("alive", "dead"),
        ("dead", "alive"),
        ("open", "closed"),
        ("closed", "open"),
        ("true", "false"),
        ("false", "true"),
        ("allowed", "forbidden"),
        ("forbidden", "allowed"),
    )

    for left, right in oppositions:
        if left in premise and right in hypothesis:
            return {
                "rule_family": "lexical_opposition",
                "facts": {"premise_term": left, "hypothesis_term": right},
                "reason": f"'{left}' conflicts with '{right}'.",
            }
    return None


def immutable_attribute_conflict(
    premise: str, hypothesis: str
) -> dict[str, Any] | None:
    biological_terms = (
        "biological hand",
        "biological arm",
        "natural hand",
        "natural arm",
        "flesh and blood hand",
    )
    prosthetic_terms = (
        "mechanical prosthesis",
        "prosthetic hand",
        "prosthetic arm",
        "mechanical hand",
        "artificial hand",
        "artificial arm",
    )

    if contains_any(premise, biological_terms) and contains_any(hypothesis, prosthetic_terms):
        return {
            "rule_family": "immutable_attribute_conflict",
            "facts": {
                "premise_attribute": "biological_limb",
                "hypothesis_attribute": "permanent_prosthetic_limb",
            },
            "reason": "A biological limb conflicts with a permanent mechanical prosthesis.",
        }

    if contains_any(premise, prosthetic_terms) and contains_any(hypothesis, biological_terms):
        return {
            "rule_family": "immutable_attribute_conflict",
            "facts": {
                "premise_attribute": "permanent_prosthetic_limb",
                "hypothesis_attribute": "biological_limb",
            },
            "reason": "A permanent mechanical prosthesis conflicts with a biological limb.",
        }

    return None


def identity_history_conflict(premise: str, hypothesis: str) -> dict[str, Any] | None:
    never_earth = (
        "never traveled to earth",
        "never travelled to earth",
        "never been to earth",
        "has never been to earth",
    )
    earth_history = (
        "childhood in michigan",
        "grew up in michigan",
        "born in michigan",
        "lived in michigan",
        "raised in michigan",
    )

    if contains_any(premise, never_earth) and contains_any(hypothesis, earth_history):
        return {
            "rule_family": "identity_history_conflict",
            "facts": {
                "premise_constraint": "never_on_earth",
                "hypothesis_history": "earth_residency",
            },
            "reason": "A person who was never on Earth cannot have a childhood in Michigan.",
        }

    if contains_any(premise, earth_history) and contains_any(hypothesis, never_earth):
        return {
            "rule_family": "identity_history_conflict",
            "facts": {
                "premise_history": "earth_residency",
                "hypothesis_constraint": "never_on_earth",
            },
            "reason": "Earth residency conflicts with never having been on Earth.",
        }

    return None


def temporal_state_conflict(premise: str, hypothesis: str) -> dict[str, Any] | None:
    destroyed_terms = (
        "permanently destroyed",
        "completely destroyed",
        "destroyed beyond repair",
        "was demolished",
        "had been destroyed",
    )
    intact_terms = (
        "undamaged",
        "intact",
        "still standing",
        "unharmed",
        "broadcast from the tower",
    )

    if contains_any(premise, destroyed_terms) and contains_any(hypothesis, intact_terms):
        return {
            "rule_family": "temporal_state_conflict",
            "facts": {
                "premise_state": "permanently_destroyed",
                "hypothesis_state": "intact_or_operational",
            },
            "reason": "A permanently destroyed structure cannot later be intact or operational.",
        }

    if contains_any(premise, intact_terms) and contains_any(hypothesis, destroyed_terms):
        return {
            "rule_family": "temporal_state_conflict",
            "facts": {
                "premise_state": "intact_or_operational",
                "hypothesis_state": "permanently_destroyed",
            },
            "reason": "An intact or operational structure conflicts with permanent destruction.",
        }

    return None


def required_process_conflict(premise: str, hypothesis: str) -> dict[str, Any] | None:
    quarantine_required = (
        "quarantine is required",
        "requires quarantine",
        "must be quarantined",
        "mandatory quarantine",
    )
    bypass_quarantine = (
        "directly committed",
        "committed directly",
        "without quarantine",
        "skipped quarantine",
        "bypassed quarantine",
    )

    if contains_any(premise, quarantine_required) and contains_any(hypothesis, bypass_quarantine):
        return {
            "rule_family": "required_process_conflict",
            "facts": {
                "required_step": "quarantine",
                "attempted_action": "direct_commit_without_quarantine",
            },
            "reason": "A direct commitment conflicts with a mandatory quarantine step.",
        }

    if contains_any(premise, bypass_quarantine) and contains_any(hypothesis, quarantine_required):
        return {
            "rule_family": "required_process_conflict",
            "facts": {
                "premise_action": "direct_commit_without_quarantine",
                "hypothesis_requirement": "quarantine",
            },
            "reason": "Bypassing quarantine conflicts with a mandatory quarantine rule.",
        }

    return None


def authority_scope_conflict(premise: str, hypothesis: str) -> dict[str, Any] | None:
    tier_three_required = (
        "tier 3 is required",
        "requires tier 3",
        "tier 3 authorization",
        "tier three authorization",
        "only tier 3",
    )
    tier_zero_action = (
        "tier 0 modified",
        "tier 0 operator modified",
        "tier 0 changed",
        "tier 0 altered",
        "tier zero modified",
        "tier zero changed",
        "tier zero altered",
    )

    if contains_any(premise, tier_three_required) and contains_any(hypothesis, tier_zero_action):
        return {
            "rule_family": "authority_scope_conflict",
            "facts": {
                "required_tier": 3,
                "requested_actor_tier": 0,
                "operation": "protected_state_mutation",
            },
            "reason": "Tier 0 cannot authorize a Tier 3 protected-state mutation.",
        }

    if contains_any(premise, tier_zero_action) and contains_any(hypothesis, tier_three_required):
        return {
            "rule_family": "authority_scope_conflict",
            "facts": {
                "premise_actor_tier": 0,
                "hypothesis_required_tier": 3,
                "operation": "protected_state_mutation",
            },
            "reason": "A Tier 0 mutation conflicts with a Tier 3 authorization requirement.",
        }

    return None


def hash_chain_conflict(premise: str, hypothesis: str) -> dict[str, Any] | None:
    chain_required = (
        "parent hash is required",
        "requires a parent hash",
        "must include a parent hash",
        "hash chain is required",
        "each block references its parent",
    )
    unlinked_block = (
        "isolated block",
        "unlinked block",
        "without a parent hash",
        "no parent hash",
        "standalone block",
    )

    if contains_any(premise, chain_required) and contains_any(hypothesis, unlinked_block):
        return {
            "rule_family": "hash_chain_conflict",
            "facts": {
                "required_relation": "parent_hash_chain",
                "hypothesis_relation": "isolated_or_unlinked_block",
            },
            "reason": "An isolated block conflicts with a required parent-hash chain.",
        }

    if contains_any(premise, unlinked_block) and contains_any(hypothesis, chain_required):
        return {
            "rule_family": "hash_chain_conflict",
            "facts": {
                "premise_relation": "isolated_or_unlinked_block",
                "hypothesis_requirement": "parent_hash_chain",
            },
            "reason": "A block without a parent hash conflicts with a required hash chain.",
        }

    return None


def causal_constraint_conflict(premise: str, hypothesis: str) -> dict[str, Any] | None:
    gate_required = (
        "requires a gate",
        "gate required",
        "must use a gate",
        "only through a gate",
        "ftl requires a gate",
    )
    ungated_jump = (
        "without a gate",
        "ungated jump",
        "jumped without a gate",
        "ftl jump without a gate",
        "jumped directly",
    )

    if contains_any(premise, gate_required) and contains_any(hypothesis, ungated_jump):
        return {
            "rule_family": "causal_constraint_conflict",
            "facts": {
                "required_condition": "gate",
                "hypothesis_action": "ungated_jump",
            },
            "reason": "An ungated jump conflicts with a gate-required travel rule.",
        }

    if contains_any(premise, ungated_jump) and contains_any(hypothesis, gate_required):
        return {
            "rule_family": "causal_constraint_conflict",
            "facts": {
                "premise_action": "ungated_jump",
                "hypothesis_requirement": "gate",
            },
            "reason": "An ungated jump conflicts with a mandatory gate requirement.",
        }

    return None


def domain_state_conflict(premise: str, hypothesis: str) -> dict[str, Any] | None:
    fatigue_required = (
        "causes necrotic fatigue",
        "results in necrotic fatigue",
        "leaves necrotic fatigue",
        "necrotic fatigue is inevitable",
    )
    fatigue_absent = (
        "pristine hands",
        "fatigue free hands",
        "fatigue-free hands",
        "no fatigue",
        "without fatigue",
        "hands remained pristine",
    )

    if contains_any(premise, fatigue_required) and contains_any(hypothesis, fatigue_absent):
        return {
            "rule_family": "domain_state_conflict",
            "facts": {
                "required_effect": "necrotic_fatigue",
                "hypothesis_state": "pristine_or_fatigue_free",
            },
            "reason": "A required necrotic-fatigue effect conflicts with pristine, fatigue-free hands.",
        }

    if contains_any(premise, fatigue_absent) and contains_any(hypothesis, fatigue_required):
        return {
            "rule_family": "domain_state_conflict",
            "facts": {
                "premise_state": "pristine_or_fatigue_free",
                "hypothesis_effect": "necrotic_fatigue",
            },
            "reason": "Pristine, fatigue-free hands conflict with a required necrotic-fatigue effect.",
        }

    return None


RULES = (
    lexical_opposition,
    immutable_attribute_conflict,
    identity_history_conflict,
    temporal_state_conflict,
    required_process_conflict,
    authority_scope_conflict,
    hash_chain_conflict,
    causal_constraint_conflict,
    domain_state_conflict,
)


def evaluate_pair(premise: str, hypothesis: str) -> dict[str, Any]:
    normalized_premise = normalize(premise)
    normalized_hypothesis = normalize(hypothesis)

    for rule in RULES:
        evidence = rule(normalized_premise, normalized_hypothesis)
        if evidence:
            return {
                "prediction": True,
                "premise": premise,
                "hypothesis": hypothesis,
                **evidence,
            }

    return {
        "prediction": False,
        "premise": premise,
        "hypothesis": hypothesis,
        "rule_family": "no_structured_conflict_detected",
        "facts": {},
        "reason": "No configured contradiction rule matched this pair.",
    }


def get_text(record: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str):
            return value
    return ""


def get_expected(record: dict[str, Any]) -> bool | None:
    for key in ("isContradiction", "is_contradiction", "contradiction", "label"):
        value = record.get(key)

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            value = value.strip().lower()
            if value in {"true", "contradiction", "contradict", "1", "yes"}:
                return True
            if value in {"false", "noncontradiction", "non_contradiction", "0", "no"}:
                return False

        if isinstance(value, int) and value in {0, 1}:
            return bool(value)

    return None


def load_corpus() -> tuple[Path, list[dict[str, Any]]]:
    for candidate in CORPUS_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return path, data
            if isinstance(data, dict):
                for key in ("cases", "items", "records", "examples"):
                    if isinstance(data.get(key), list):
                        return path, data[key]

    raise FileNotFoundError(
        "No supported corpus file found. Expected one of: "
        + ", ".join(CORPUS_CANDIDATES)
    )


def main() -> None:
    corpus_path, corpus = load_corpus()

    results: list[dict[str, Any]] = []
    scored = 0
    correct = 0
    false_positives = 0
    false_negatives = 0

    for index, record in enumerate(corpus, start=1):
        premise = get_text(record, ("premise", "context", "source"))
        hypothesis = get_text(record, ("hypothesis", "claim", "target"))
        expected = get_expected(record)
        evaluation = evaluate_pair(premise, hypothesis)

        result = {
            "case": record.get("id", record.get("case_id", index)),
            "expected": expected,
            **evaluation,
        }

        if expected is not None:
            scored += 1
            result["correct"] = evaluation["prediction"] == expected
            correct += int(result["correct"])

            if evaluation["prediction"] and not expected:
                false_positives += 1
            elif not evaluation["prediction"] and expected:
                false_negatives += 1

        results.append(result)

    summary = {
        "harness": "Cranium Substrate structured contradiction evaluator",
        "corpus": str(corpus_path),
        "cases": len(results),
        "scored_cases": scored,
        "correct": correct,
        "accuracy_percent": round((correct / scored) * 100, 2) if scored else None,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "results": results,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
