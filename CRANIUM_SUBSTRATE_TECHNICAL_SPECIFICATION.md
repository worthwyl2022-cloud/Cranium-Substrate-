# Cranium Substrate Technical Specification v1.0

**Cranium Substrate™**
© 2026 Wyl Mathes. All Rights Reserved.

---

## Authorship Notice

Dated technical specification describing the architecture, terminology, and
implementation concepts of the Cranium Substrate Engine, authored by Wyl Mathes.
Published as evidence of authorship, design evolution, and ownership.

---

## System Overview

Cranium Substrate is a cognitive infrastructure architecture implemented in
Kotlin, organized around protected semantic channels (Canon Lanes), immutable
epistemic units (Cognitive Atoms), contradiction detection, deliberative
convergence, and a prompt-stream immune defense layer.

---

## Core Architectural Concepts

### Canon Lanes
Priority-bound semantic channels. Lane hierarchy: System Axioms, Enterprise
Policy, Factual Knowledge, User Preferences, Working Memory, Hypothetical/Sandbox.

### Cognitive Atoms
Basic epistemic unit. Stores: proposition, lane, provenance, confidence score,
timestamp, metadata, optional embedding. Temporal decay reduces confidence on
non-axiomatic atoms.

### Contradiction Engine
Pairwise semantic conflict detection via lexical polarity and negation heuristics.
Generates conflict reports. Resolution strategies: lock protected lanes, supersede
lower-confidence atoms.

### Deliberation Engine
Iterates over working atom pool, audits contradictions, applies resolution matrix,
computes consensus confidence until convergence or iteration limit.

### Epistemic Immune Layer
Scans prompt streams for jailbreak patterns, override attempts, axiom-negation
vectors. Responses: allow, purge, isolate, or lock depending on threat severity.

### Output Evaluator
Checks generated output against protected lanes before release. Flags policy
violations and contradiction with protected axioms.

---

## Repository Modules

| Module | Purpose |
|---|---|
| substrate/ | Core semantic and deliberative runtime |
| immune/ | Prompt-stream defense and quarantine logic |
| judge/ | Contradiction audit and benchmark evaluation |
| product/ | Workspace and project-store layer |
| benchmark/ | Corpus, methodology, harnesses, receipts, audit reports |
| docs/ | Executive and acquisition-facing materials |

---

## Named System Elements (Terminology Record as of 2026-08-29)

- Cranium Substrate
- Canon Lanes
- Cognitive Atoms
- Epistemic Immune Layer
- Deliberation Engine
- Contradiction Engine
- Resonance Field
- Output Evaluator
- Substrate Core
- Cranium Judge

---

## Trade Secret Guidance

Recommended for trade-secret treatment (do not fully disclose publicly):
- Contradiction scoring and weighting logic
- Deliberation convergence tuning values
- Lane prioritization heuristics and thresholds
- Governance and override mechanisms
- Future causal reasoning methods

---

## Ownership

Cranium Substrate™
© 2026 Wyl Mathes. All Rights Reserved.
WorthWyl Media · Las Vegas, NV
First version: 2026-08-29
