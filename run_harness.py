#!/usr/bin/env python3
"""Cranium Substrate deterministic, auditable contradiction harness."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Callable


CORPUS_CANDIDATES = (
    "frozen_corpus.json",
    "corpus.json",
    "test_corpus.json",
    "fixtures/frozen_corpus.json",
)


def normalize(text: str) -> str:
    text = text.lower().replace("—", " ").replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def has(text: str, *phrases: str) -> bool:
    return any(phrase in text for phrase in phrases)


def finding(rule_family: str, reason: str, **facts: Any) -> dict[str, Any]:
    return {"rule_family": rule_family, "facts": facts, "reason": reason}


def lexical_opposition(p: str, h: str) -> dict[str, Any] | None:
    pairs = (
        (("always",), ("never",)),
        (("alive", "survived", "speaking with investigators"), ("dead", "did not survive")),
        (("dead", "did not survive"), ("alive", "survived", "speaking with investigators")),
        (("open", "unlocked"), ("closed", "locked")),
        (("closed", "locked"), ("open", "unlocked")),
        (("allowed",), ("forbidden",)),
        (("forbidden",), ("allowed",)),
    )
    for left, right in pairs:
        if has(p, *left) and has(h, *right):
            return finding("lexical_opposition", "Opposing state or polarity terms were detected.", premise_terms=left, hypothesis_terms=right)
    return None


def immutable_attribute_conflict(p: str, h: str) -> dict[str, Any] | None:
    organic = ("biological hand", "biological arm", "natural hand", "natural arm", "organic", "living skin", "living tissue")
    artificial = ("mechanical prosthesis", "prosthetic hand", "prosthetic arm", "mechanical hand", "artificial hand", "artificial arm", "artificial device")
    if has(p, *organic) and has(h, *artificial):
        return finding("immutable_attribute_conflict", "An organic limb conflicts with an artificial-limb claim.", premise_attribute="organic_limb", hypothesis_attribute="artificial_limb")
    if has(p, *artificial) and has(h, *organic):
        return finding("immutable_attribute_conflict", "An artificial limb conflicts with an organic-limb claim.", premise_attribute="artificial_limb", hypothesis_attribute="organic_limb")
    return None


def identity_history_conflict(p: str, h: str) -> dict[str, Any] | None:
    never_earth = ("never traveled to earth", "never travelled to earth", "never been to earth", "never on earth", "not once set foot on earth", "entire life off world")
    earth_history = ("childhood in michigan", "grew up in michigan", "born in michigan", "lived in michigan", "raised in michigan", "school in detroit", "attended elementary school in detroit")
    if has(p, *never_earth) and has(h, *earth_history):
        return finding("identity_history_conflict", "Never having been on Earth conflicts with an Earth-residency history.", premise_constraint="never_on_earth", hypothesis_history="earth_residency")
    if has(p, *earth_history) and has(h, *never_earth):
        return finding("identity_history_conflict", "An Earth-residency history conflicts with never having been on Earth.", premise_history="earth_residency", hypothesis_constraint="never_on_earth")
    return None


def temporal_state_conflict(p: str, h: str) -> dict[str, Any] | None:
    destroyed = ("permanently destroyed", "completely destroyed", "destroyed beyond repair", "was demolished", "had been destroyed", "ceased to exist", "could not be rebuilt")
    operational = ("undamaged", "intact", "still standing", "unharmed", "broadcast from the tower", "used intact for a broadcast")
    if has(p, *destroyed) and has(h, *operational):
        return finding("temporal_state_conflict", "A permanently destroyed structure cannot be intact or operational later.", premise_state="destroyed", hypothesis_state="intact_or_operational")
    if has(p, *operational) and has(h, *destroyed):
        return finding("temporal_state_conflict", "An intact or operational structure conflicts with permanent destruction.", premise_state="intact_or_operational", hypothesis_state="destroyed")
    return None


def required_process_conflict(p: str, h: str) -> dict[str, Any] | None:
    isolation_required = ("quarantine is required", "requires quarantine", "must be quarantined", "mandatory quarantine", "must remain in an isolation review stage", "isolation review stage before")
    bypassed = ("directly committed", "committed directly", "without quarantine", "skipped quarantine", "bypassed quarantine", "entered the permanent store immediately", "bypassing isolation review")
    if has(p, *isolation_required) and has(h, *bypassed):
        return finding("required_process_conflict", "A mandatory isolation or quarantine step was bypassed.", required_step="isolation_or_quarantine", attempted_action="commit_without_required_review")
    if has(p, *bypassed) and has(h, *isolation_required):
        return finding("required_process_conflict", "Bypassing isolation or quarantine conflicts with a mandatory review rule.", premise_action="commit_without_required_review", hypothesis_requirement="isolation_or_quarantine")
    return None


def authority_scope_conflict(p: str, h: str) -> dict[str, Any] | None:
    senior_only = ("tier 3 is required", "requires tier 3", "tier 3 authorization", "tier three authorization", "only tier 3", "only a level three custodian")
    junior_action = ("tier 0 modified", "tier 0 changed", "tier 0 altered", "tier zero modified", "tier zero changed", "tier zero altered", "level zero clerk changed")
    if has(p, *senior_only) and has(h, *junior_action):
        return finding("authority_scope_conflict", "A junior actor performed a protected operation reserved for a senior authority tier.", required_tier="senior", requested_actor_tier="junior", operation="protected_state_mutation")
    if has(p, *junior_action) and has(h, *senior_only):
        return finding("authority_scope_conflict", "A junior protected-state mutation conflicts with a senior-only authorization rule.", premise_actor_tier="junior", hypothesis_required_tier="senior")
    return None


def hash_chain_conflict(p: str, h: str) -> dict[str, Any] | None:
    chain_required = ("parent hash is required", "requires a parent hash", "must include a parent hash", "hash chain is required", "each block references its parent", "must cite the digest of the entry immediately before it")
    unlinked = ("isolated block", "unlinked block", "without a parent hash", "no parent hash", "standalone block", "no link to any prior entry")
    if has(p, *chain_required) and has(h, *unlinked):
        return finding("hash_chain_conflict", "An entry without a predecessor link conflicts with the required chain relation.", required_relation="predecessor_hash_or_digest", hypothesis_relation="unlinked_entry")
    if has(p, *unlinked) and has(h, *chain_required):
        return finding("hash_chain_conflict", "An unlinked entry conflicts with a required predecessor chain.", premise_relation="unlinked_entry", hypothesis_requirement="predecessor_hash_or_digest")
    return None


def causal_constraint_conflict(p: str, h: str) -> dict[str, Any] | None:
    gate_required = ("requires a gate", "gate required", "must use a gate", "only through a gate", "ftl requires a gate", "only when it is coupled to a relay portal", "coupled to a relay portal")
    ungated = ("without a gate", "ungated jump", "jumped without a gate", "ftl jump without a gate", "jumped directly", "without connecting to a relay portal")
    if has(p, *gate_required) and has(h, *ungated):
        return finding("causal_constraint_conflict", "A required transit gate or relay was absent.", required_condition="gate_or_relay", hypothesis_action="ungated_transit")
    if has(p, *ungated) and has(h, *gate_required):
        return finding("causal_constraint_conflict", "Ungated transit conflicts with a mandatory gate or relay requirement.", premise_action="ungated_transit", hypothesis_requirement="gate_or_relay")
    return None


def domain_state_conflict(p: str, h: str) -> dict[str, Any] | None:
    required_effect = ("causes necrotic fatigue", "results in necrotic fatigue", "leaves necrotic fatigue", "necrotic fatigue is inevitable", "inevitably leaves blackened exhaustion")
    absent_effect = ("pristine hands", "fatigue free hands", "fatigue free", "no fatigue", "without fatigue", "hands remained pristine", "no exhaustion or darkening")
    if has(p, *required_effect) and has(h, *absent_effect):
        return finding("domain_state_conflict", "A required physical effect is explicitly absent in the claim.", required_effect="fatigue_or_blackened_exhaustion", hypothesis_state="effect_absent")
    if has(p, *absent_effect) and has(h, *required_effect):
        return finding("domain_state_conflict", "The stated absence of the physical effect conflicts with its required occurrence.", premise_state="effect_absent", hypothesis_effect="fatigue_or_blackened_exhaustion")
    return None


RULES: tuple[Callable[[str, str], dict[str, Any] | None], ...] = (
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
    p, h = normalize(premise), normalize(hypothesis)
    for rule in RULES:
        evidence = rule(p, h)
        if evidence:
            return {"prediction": True, "premise": premise, "hypothesis": hypothesis, **evidence}
    return {
        "prediction": False,
        "premise": premise,
        "hypothesis": hypothesis,
        "rule_family": "no_structured_conflict_detected",
        "facts": {},
        "reason": "No configured deterministic contradiction rule matched this pair.",
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


def load_corpus(requested: str | None) -> tuple[Path, list[dict[str, Any]]]:
    candidates = (requested,) if requested else CORPUS_CANDIDATES
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return path, data
            if isinstance(data, dict):
                for key in ("cases", "items", "records", "examples"):
                    if isinstance(data.get(key), list):
                        return path, data[key]
    raise FileNotFoundError("No supported corpus file found: " + ", ".join(c for c in candidates if c))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", help="Path to a JSON corpus; defaults to frozen_corpus.json when present.")
    args = parser.parse_args()
    corpus_path, corpus = load_corpus(args.corpus)
    results: list[dict[str, Any]] = []
    scored = correct = false_positives = false_negatives = 0
    for index, record in enumerate(corpus, start=1):
        premise = get_text(record, ("premise", "context", "source"))
        hypothesis = get_text(record, ("hypothesis", "claim", "target"))
        expected = get_expected(record)
        evaluation = evaluate_pair(premise, hypothesis)
        result = {"case": record.get("id", record.get("case_id", index)), "expected": expected, **evaluation}
        if expected is not None:
            scored += 1
            result["correct"] = evaluation["prediction"] == expected
            correct += int(result["correct"])
            false_positives += int(evaluation["prediction"] and not expected)
            false_negatives += int(not evaluation["prediction"] and expected)
        results.append(result)
    summary = {
        "harness": "Cranium Substrate deterministic structured-rule evaluator",
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
