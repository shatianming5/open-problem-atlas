# Attempt Policy

## What Is an Attempt?

An attempt is a recorded effort — by an AI system, a human, or a hybrid — to make progress on a verified open problem. Attempts live in the Lab layer and never pollute the Atlas truth layer.

## Required Fields

Every attempt must include:

| Field | Description |
|-------|-------------|
| `problem_id` | References a verified problem in the Atlas |
| `actor` | Who/what made the attempt |
| `actor_type` | `human`, `ai`, or `hybrid` |
| `model` | Model name and version (for AI attempts) |
| `date` | When the attempt was made |
| `method_summary` | What approach was used |
| `tools` | Software, libraries, hardware used |
| `outcome` | What was the result |
| `verification_status` | `verified` or `unverified` |
| `limitations` | Known limitations of the attempt |

## Default Labels

All new attempts are tagged with:
- `unverified` — until independently confirmed
- `machine-generated` or `hybrid` — if AI was involved
- `not canonical` — attempt results are not canonical facts

## What Counts as an Attempt

- LLM literature review or problem decomposition
- Computational search (brute force, SAT, symbolic)
- Lean/Coq formalization attempt
- Counterexample search
- Proof sketch or partial proof
- Reproducible notebook with analysis

## What Does NOT Count

- Vague "I think this might work" without any execution
- A single LLM prompt with no analysis of the output
- Marketing claims ("GPT-5 solved this!") without evidence

## Verification

An attempt can be upgraded from `unverified` to `verified` when:
1. The methodology is reproducible
2. An independent reviewer confirms the outcome
3. For proof claims: a domain expert or formal verification confirms

## Display Rules

When showing attempts alongside problems:
- Always show: actor, model, version, date, tools, verification status
- Always show limitations
- Never present unverified AI output as fact
- Sort by: date (newest first), then verification status

## Cost Management for AI Attempts

- Use small models for initial triage
- Reserve large models for shortlisted problems
- Cache all outputs
- Record prompt versions and model IDs
- Ensure all machine-generated fields are traceable
