# PFMEA: AIAG 4th Edition to AIAG-VDA 7-Step

## Purpose
Convert a legacy AIAG 4th Edition Process FMEA into a fully compliant AIAG-VDA 1st Edition 7-Step PFMEA.

The output answers one question: **For every failure analysis row in this PFMEA, how is it correctly restructured into the 7-step harmonised layout — preserving all source content verbatim, classifying each work element into its 4M category, and replacing the obsolete RPN with Action Priority?**

## Methodology Skills
- `source_preservation` — Governs verbatim carry and row-count fidelity.
- `vda_framework` — Governs the 7-step structure, reordered failure chain, and section bands.
- `vda_four_m` — Governs the strict 4M work element classification.
- `pfmea_vda_mapping` — Governs the full column-by-column mapping contract.

## Output Contract

Every row in the output must conform to the following 20-column schema:

| # | Field | Type | Policy |
|---|---|---|---|
| 1 | `process_item` | string | CARRY — from Production Item Name |
| 2 | `process_step` | string | CARRY — from Operation Number + Operation Name |
| 3 | `work_element_4m` | `Machine` \| `Method` \| `Material` \| `Man` | AUTHOR — classified from Failure Cause |
| 4 | `process_function` | string | AUTHOR — what the process step achieves; constant per operation |
| 5 | `product_characteristic` | string \| null | CARRY |
| 6 | `process_characteristic` | string \| null | CARRY |
| 7 | `failure_effect_fe` | string | CARRY — reordered before Failure Mode |
| 8 | `severity_rating` | integer | CARRY — reordered before Failure Mode |
| 9 | `failure_mode_fm` | string | CARRY |
| 10 | `special_characteristic_class` | `CC` \| `SC` \| null | CARRY |
| 11 | `failure_cause_fc` | string | CARRY |
| 12 | `current_prevention_control` | string \| null | CARRY |
| 13 | `occurrence_rating` | integer | CARRY |
| 14 | `current_detection_control` | string \| null | CARRY |
| 15 | `detection_rating` | integer | CARRY |
| 16 | `action_priority_ap` | `H` \| `M` \| `L` | AUTHOR — computed from S × O × D per AIAG-VDA table |
| 17 | `prevention_action` | string \| null | ABSTAIN unless source specifies |
| 18 | `detection_action` | string \| null | ABSTAIN unless source specifies |
| 19 | `responsible_person` | string \| null | ABSTAIN |
| 20 | `target_completion_date` | string \| null | ABSTAIN |

## Acceptance Criteria

| Rule | Enforcement | Requirement |
|---|---|---|
| V1 | reject_document | All 20 fields present on every row |
| V2 | reject_document | Output row count equals source row count exactly (1-to-1) |
| V3 | reject_row | `work_element_4m` is exactly one of: Machine, Method, Material, Man |
| V4 | reject_row | `action_priority_ap` is exactly one of: H, M, L — computed per AIAG-VDA rubric |
| V5 | reject_row | All CARRY fields are byte-identical to their source cells |
| V6 | reject_row | ABSTAIN fields contain no authored values |