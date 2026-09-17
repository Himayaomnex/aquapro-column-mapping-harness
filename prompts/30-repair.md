# Repair Prompt (Rendered Only When `validator` Returns Violations)

## Repair Attempt
{{ repair_attempt }} of 2

After 2 failed repair attempts, the harness enters `degrade` mode.
Degrade ships only the rows with zero violations and logs the rest.
Do not try to fix every row at all costs -- a correctly-abstained row
is better than a fabricated one.

## Your Previous Draft
{{ previous_draft }}

## Violations Reported by `validator`

{% for v in violations %}
- Rule **{{ v.rule_id }}** ({{ v.on_fail }})
  Row: {{ v.row_identifier }}
  Issue: {{ v.detail }}
{% endfor %}

---

## Fix Instructions

Re-emit the FULL draft with ONLY the flagged rows/fields corrected.

**Do not touch rows that have no violations.**
Every unnecessary change to a passing row is a new opportunity to introduce
an error or lose a verbatim CARRY value.

### For each violation type:

**V1 (Missing key -- reject_document):**
A required column key is absent from a row. Add the missing key.
If you have no source evidence for that key's value, set it to `null`.

**V2 (Missing operation -- reject_document):**
An operation from the PFMEA source is absent from your output.
Find it in the mapped context and add a complete row for it.
If source data is incomplete for that operation, emit a row with null values
for AUTHOR fields -- do not omit the operation entirely.

**V3 (ABSTAIN column non-null -- reject_row):**
A column classified as ABSTAIN has a non-null value. Set it to `null`.
There is no version of this fix that keeps the non-null value. The rule
is unconditional.

**V4 (AUTHOR column not traceable -- reject_row):**
An authored value cannot be traced to its source PFMEA field.
Either correct the derivation to match what the source actually says,
or set the field to `null`. Do not invent a citation to make the check pass.

**V5 (Reaction Plan without Detective Control -- reject_row):**
A Reaction Plan value exists but `detective_control` is null in source.
Set `reaction_plan` to `null` on this row unconditionally.

---

Output valid JSON only. Same schema as the original compose output.
No prose. No explanation. Just the corrected full draft.
