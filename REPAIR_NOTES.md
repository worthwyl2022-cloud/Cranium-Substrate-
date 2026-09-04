# Structured Contradiction Taxonomy Repair

## Purpose

Replace the current narrow lexical contradiction detector with a structured,
auditable rule taxonomy. The target is semantic conflict detection, not
case-ID or phrase matching.

## Current baseline

- Frozen corpus size: 15 cases
- Contradictions: 11
- Non-contradictions: 4
- Previous contradiction detection: 7/15
- Previous overall accuracy: 46.67%
- Specificity on the 4 non-contradictions: 100%

The original corpus and the 46.67% receipt must remain frozen as pre-repair
evidence. Do not overwrite, relabel, or remove it.

## Required rule families

The evaluator must test relations rather than benchmark-specific phrases.

1. Immutable attribute conflict
   - Example: a biological hand conflicts with a permanent mechanical prosthesis.

2. Identity and biography conflict
   - Example: “never traveled to Earth” conflicts with a childhood in Michigan.

3. Temporal state conflict
   - Example: a permanently destroyed tower conflicts with a later undamaged broadcast.

4. Required process conflict
   - Example: required quarantine conflicts with direct commitment without quarantine.

5. Authority and scope conflict
   - Example: a Tier 0 actor cannot perform a Tier 3 protected-state mutation.

6. Cryptographic chain conflict
   - Example: a required parent-hash chain conflicts with isolated or unlinked blocks.

7. Causal or technology constraint conflict
   - Example: gate-required FTL travel conflicts with a jump that uses no gate.

8. Required domain-state conflict
   - Example: necrotic fatigue as a required result conflicts with pristine, fatigue-free hands.

9. Existing lexical opposition support
   - Retain the current generic antonym/opposition handling only as one rule family.

## Evaluator contract

The top-level evaluator should return a verdict and an auditable explanation.

```python
{
    "prediction": True,
    "rule_family": "authority_scope_conflict",
    "facts": {
        "requested_actor_tier": 0,
        "required_tier": 3,
        "requested_operation": "modify_authoritative_state",
    },
    "reason": "Tier 0 cannot authorize a Tier 3 protected-state mutation.",
}
