# Capability Contract — Template

Every file under `capabilities/` fills in exactly these seven sections.
This is the template referenced by the harness design's "Adding a New
Capability" panel (item 1: *Create a capability .md*). If a capability
file has a section this template doesn't define, delete the section — it
belongs in a skill or a schema instead.

```yaml
capability_id: string              # e.g. control_plan_from_pfmea
consumer: string                   # who reads this output and why
trigger_description: string        # one paragraph, for the model's own
                                    # capability-declaration decision —
                                    # NOT a regex, NOT a router rule
input_contract:
  requires_file: bool
  accepted_file_types: [string]
  no_file_fallback: string | null  # name of the tool/skill used instead
output_contract:
  format: json_schema               # always JSON — the verifier must parse it
  schema_ref: string                 # path to the schema
verification_rules:                 # V1..Vn — see rule below
  - id: string
    statement: string
    checked_by: string              # exact function/check in `verify`
    on_fail: reject_row | reject_document | warn
degrade_policy: string              # what `degrade` ships if repair fails
non_goals: [string]                 # explicit — what this capability does NOT do
```

## The rule that governs this template

**Every line in `verification_rules` must name the exact check that
enforces it in code.** If you cannot name the check, the rule is prose,
not a rule — move it to the skill file as guidance, or delete it. The
harness design's Enforceability Rule (§5.2) applies here word for word:
*every rule in a prompt must be enforceable by the verifier in code, or be
deleted.*

## `on_fail` semantics

- `reject_row`: this row is dropped from the composed output and reported
  in `execution_log.json`; the rest of the document ships. Used for rules
  that are local to one operation/characteristic.
- `reject_document`: the whole draft fails verification and goes to
  `repair`; if repair is exhausted, the whole document goes to `degrade`.
  Used for rules that are structural (e.g. "all 16 columns present").
- `warn`: logged, does not block delivery. Used sparingly — a rule that
  never blocks anything is close to decoration and should be justified.
