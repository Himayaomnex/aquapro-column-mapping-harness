# DFMEA: AIAG 4th Edition to AIAG-VDA 7-Step

## Purpose
Convert a legacy AIAG 4th Edition Design FMEA into a fully compliant AIAG-VDA 1st Edition 7-Step DFMEA.

The output answers one question: **For every failure analysis row in this DFMEA, how is it correctly restructured into the 7-step layout — establishing the 3-level design structure hierarchy, preserving the failure chain verbatim, and computing Action Priority?**

## Methodology Skills
- `source_preservation` — Governs verbatim carry and row-count fidelity.
- `vda_framework` — Governs the 7-step structure, reordered failure chain, and section bands.
- `dfmea_vda_mapping` — Governs the 3-level hierarchy authoring and alignment rules.

## Output Contract

Every row in the output must conform to the following schema:

| Field | Type | Policy | Description |
|---|---|---|---|
| `higher_level_element` | string | AUTHOR | System-level item; constant across all rows |
| `focus_element` | string | AUTHOR | Subsystem or interface being analysed; consistent per function group |
| `lower_level_element` | string | AUTHOR | Component or material interface responsible for the cause |
| `system_function` | string | AUTHOR | Intended function of the overall system |
| `focus_function` | string | AUTHOR | Function of the focus element; may reflect source requirement text |
| `design_characteristic` | string | CARRY | Product design requirement or functional characteristic |
| `failure_effect_fe` | string | CARRY | Potential effect of failure; reordered before failure mode |
| `severity_rating` | integer | CARRY | Severity score (1-10); reordered before failure mode |
| `failure_mode_fm` | string | CARRY | Potential failure mode |
| `special_characteristic_class` | `CC` \| `SC` \| null | CARRY | Special characteristic designation |
| `design_cause_fc` | string | CARRY | Design mechanism or failure cause |
| `current_prevention_control` | string \| null | CARRY | Existing design prevention controls |
| `occurrence_rating` | integer | CARRY | Occurrence score (1-10) |
| `current_detection_control` | string \| null | CARRY | Existing design detection controls |
| `detection_rating` | integer | CARRY | Detection score (1-10) |
| `action_priority_ap` | `H` \| `M` \| `L` | AUTHOR | Action Priority evaluated from S × O × D per AIAG-VDA standard |
| `recommended_design_action` | string \| null | ABSTAIN | Recommended mitigation action (retained if present in source) |
| `responsible_engineer` | string \| null | ABSTAIN | Responsible engineer / owner |
| `target_date` | string \| null | ABSTAIN | Target completion date |
| `action_status` | string \| null | ABSTAIN | Status of the design action |

## Acceptance Criteria

| Rule | Enforcement | Requirement |
|---|---|---|
| V1 | reject_document | All defined schema fields present on every row |
| V2 | reject_document | Output row count equals source row count exactly (1-to-1) |
| V3 | reject_document | `higher_level_element` is identical on every row |
| V4 | reject_document | `focus_element` is identical across all rows sharing the same Function Group |
| V5 | reject_row | `action_priority_ap` is exactly one of: H, M, L — computed per AIAG-VDA rubric |
| V6 | reject_row | All CARRY fields are byte-identical to their source cells |
| V7 | reject_row | ABSTAIN fields contain no authored values unless source provides them |