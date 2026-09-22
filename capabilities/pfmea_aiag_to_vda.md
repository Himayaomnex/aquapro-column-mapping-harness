# PFMEA: AIAG 4th Edition to AIAG-VDA 7-Step

## Purpose
Convert a legacy AIAG 4th Edition Process FMEA into a fully compliant AIAG-VDA 1st Edition 7-Step PFMEA.

The output answers one question: **For every failure analysis row in this PFMEA, how is it correctly restructured into the 7-step harmonised layout — preserving all source content verbatim, classifying each work element into its 4M category, and replacing the obsolete RPN with Action Priority?**

## Methodology Skills
- `source_preservation` — Governs verbatim carry and row-count fidelity.
- `vda_framework` — Governs the 7-step structure, reordered failure chain, and section bands.
- `vda_four_m` — Governs the strict 4M work element classification.
- `pfmea_vda_mapping` — Governs transformation methodology and mapping rules.

## Output Contract

Every row in the output must conform to the following schema:

| Field | Type | Policy | Description |
|---|---|---|---|
| `process_item` | string | CARRY | System, sub-system, or item name |
| `process_step` | string | CARRY | Operation sequence number and operation name |
| `work_element_4m` | `Machine` \| `Method` \| `Material` \| `Man` | AUTHOR | Work element classified from failure cause |
| `process_function` | string | AUTHOR | Function of the process step; consistent per operation |
| `product_characteristic` | string \| null | CARRY | Product specification or feature |
| `process_characteristic` | string \| null | CARRY | Process parameter |
| `failure_effect_fe` | string | CARRY | Potential effect of failure; reordered before failure mode |
| `severity_rating` | integer | CARRY | Severity score (1-10); reordered before failure mode |
| `failure_mode_fm` | string | CARRY | Potential failure mode |
| `special_characteristic_class` | `CC` \| `SC` \| null | CARRY | Special characteristic classification |
| `failure_cause_fc` | string | CARRY | Potential cause or mechanism of failure |
| `current_prevention_control` | string \| null | CARRY | Existing prevention controls |
| `occurrence_rating` | integer | CARRY | Occurrence score (1-10) |
| `current_detection_control` | string \| null | CARRY | Existing detection controls |
| `detection_rating` | integer | CARRY | Detection score (1-10) |
| `action_priority_ap` | `H` \| `M` \| `L` | AUTHOR | Action Priority evaluated from S × O × D per AIAG-VDA standard |
| `prevention_action` | string \| null | ABSTAIN | Recommended prevention action (retained if present in source) |
| `detection_action` | string \| null | ABSTAIN | Recommended detection action (retained if present in source) |
| `responsible_person` | string \| null | ABSTAIN | Responsible person / role |
| `target_completion_date` | string \| null | ABSTAIN | Target completion date |

## Acceptance Criteria

| Rule | Enforcement | Requirement |
|---|---|---|
| V1 | reject_document | All defined schema fields present on every row |
| V2 | reject_document | Output row count equals source row count exactly (1-to-1) |
| V3 | reject_row | `work_element_4m` is exactly one of: Machine, Method, Material, Man |
| V4 | reject_row | `action_priority_ap` is exactly one of: H, M, L — computed per AIAG-VDA rubric |
| V5 | reject_row | All CARRY fields are byte-identical to their source cells |
| V6 | reject_row | ABSTAIN fields contain no authored values unless source provides them |