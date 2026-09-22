# Control Plan from PFMEA

## Purpose
Produce an authentic, audit-ready AIAG Control Plan from a Process FMEA workbook.

The output answers one question: **For each process operation and characteristic in this PFMEA, what is the exact control plan — what must be preserved verbatim, what must be derived from process evidence, and what must remain blank?**

## Methodology Skills
- `source_preservation` — Governs verbatim carry and row-count fidelity.
- `control_plan_mapping` — Governs schema structure, derivation rules, and abstention policy.

## Output Contract

Every row in the output must conform to the following schema:

| Field | Type | Policy | Description |
|---|---|---|---|
| `production_item_name` | string | CARRY | Product or item identifier |
| `process_segment_name` | string | CARRY | Process segment or department; must never be dropped when present in source |
| `operation_number` | string | CARRY | Step or operation sequence number |
| `operation_name` | string | CARRY | Operation or process description |
| `product_characteristic` | string | CARRY | Product specification or feature |
| `process_characteristic` | string | CARRY / AUTHOR | Process parameter; CARRY if present, AUTHOR from cause if absent |
| `special_characteristic_class` | `CC` \| `SC` \| null | AUTHOR | Critical (`CC`) or Significant (`SC`) designation when S ≥ 8 or source flagged; otherwise null |
| `specification_tolerance` | string \| null | ABSTAIN | Engineering specification or tolerance |
| `evaluation_measurement_technique` | string \| null | AUTHOR | Measurement technique derived from source detection control |
| `tool_number` | string \| null | ABSTAIN | Tooling or fixture inventory number |
| `tool_name` | string \| null | ABSTAIN | Tooling or equipment name |
| `gage_number` | string \| null | ABSTAIN | Measurement gage identification |
| `control_method` | string \| null | AUTHOR | Operating control method derived from source prevention control |
| `sample_size` | string \| null | ABSTAIN | Inspection sample quantity |
| `sample_frequency` | string \| null | ABSTAIN | Inspection frequency |
| `reaction_plan` | string \| null | AUTHOR | Containment action derived only when an evaluation technique exists |

**ABSTAIN fields must remain blank.** A Control Plan with honest blanks is fully AIAG PPAP 4th Edition compliant. Fabricated tooling IDs, gage numbers, or sampling plans cause immediate OEM PPAP audit failure.

## Acceptance Criteria

| Rule | Enforcement | Requirement |
|---|---|---|
| V1 | reject_document | All defined schema fields present on every row |
| V2 | reject_document | Output row count equals source row count exactly (1-to-1) |
| V3 | reject_document | `process_segment_name` populated on every row where source provides it |
| V4 | reject_row | ABSTAIN fields contain no authored values |
| V5 | reject_row | `control_method` and `evaluation_measurement_technique` grounded in source PFMEA controls |
| V6 | reject_row | `reaction_plan` appears only when `evaluation_measurement_technique` is non-null |