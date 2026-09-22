# DFMEA: AIAG 4th Edition to AIAG-VDA 7-Step

## Purpose
Convert a legacy AIAG 4th Edition Design FMEA into a fully compliant AIAG-VDA 1st Edition 7-Step DFMEA.

The output answers one question: **For every failure analysis row in this DFMEA, how is it correctly restructured into the 7-step layout — establishing the 3-level design structure hierarchy, preserving the failure chain verbatim, and computing Action Priority?**

## Methodology Skills
- `source_preservation` — Governs verbatim carry and row-count fidelity.
- `vda_framework` — Governs the 7-step structure, reordered failure chain, and section bands.
- `dfmea_vda_mapping` — Governs the 3-level hierarchy authoring and the full column mapping contract.

## Output Contract

Every row in the output must conform to the following 20-column schema:

| # | Field | Type | Policy |
|---|---|---|---|
| 1 | `higher_level_element` | string | AUTHOR — system-level item; constant across all rows |
| 2 | `focus_element` | string | AUTHOR — subsystem or interface being analysed; constant per function group |
| 3 | `lower_level_element` | string | AUTHOR — component or material interface responsible for the cause |
| 4 | `system_function` | string | AUTHOR — what the system must achieve |
| 5 | `focus_function` | string | AUTHOR — what the focus element does; may carry source requirement text |
| 6 | `design_characteristic` | string | CARRY — from source Requirement or Function |
| 7 | `failure_effect_fe` | string | CARRY — reordered before Failure Mode |
| 8 | `severity_rating` | integer | CARRY — reordered before Failure Mode |
| 9 | `failure_mode_fm` | string | CARRY |
| 10 | `special_characteristic_class` | `CC` \| `SC` \| null | CARRY |
| 11 | `design_cause_fc` | string | CARRY |
| 12 | `current_prevention_control` | string \| null | CARRY |
| 13 | `occurrence_rating` | integer | CARRY |
| 14 | `current_detection_control` | string \| null | CARRY |
| 15 | `detection_rating` | integer | CARRY |
| 16 | `action_priority_ap` | `H` \| `M` \| `L` | AUTHOR — computed from S × O × D per AIAG-VDA table |
| 17 | `recommended_design_action` | string \| null | ABSTAIN unless source specifies |
| 18 | `responsible_engineer` | string \| null | ABSTAIN |
| 19 | `target_date` | string \| null | ABSTAIN |
| 20 | `action_status` | string \| null | ABSTAIN |

## Acceptance Criteria

| Rule | Enforcement | Requirement |
|---|---|---|
| V1 | reject_document | All 20 fields present on every row |
| V2 | reject_document | Output row count equals source row count exactly (1-to-1) |
| V3 | reject_document | `higher_level_element` is identical on every row |
| V4 | reject_document | `focus_element` is identical across all rows sharing the same Function Group |
| V5 | reject_row | `action_priority_ap` is exactly one of: H, M, L — computed per AIAG-VDA rubric |
| V6 | reject_row | All CARRY fields are byte-identical to their source cells |
| V7 | reject_row | ABSTAIN fields contain no authored values |