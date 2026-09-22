# Capability Contract: dfmea_aiag_to_vda

## Consumer
Product Design Engineers, Systems Engineering Leads, and Functional Safety Auditors harmonizing Design FMEAs to the AIAG-VDA 1st Edition standard.

## Purpose
Convert a legacy AIAG 4th Edition DFMEA into a fully compliant AIAG-VDA 1st Edition 7-Step DFMEA document.
Core question answered: **Given this legacy DFMEA, how is it correctly restructured into the 3-level design structure hierarchy (System, System Element, Component Element), with reordered failure net, and Action Priority (AP)?**

## Applicable Methodology Skills
- `skills/source_preservation.md` — Invariant of verbatim carry, 1-to-1 row preservation, and zero hallucination.
- `skills/vda_framework.md` — 7-Step harmonized structure, reordered failure chain, and section banding.
- `skills/dfmea_vda_mapping.md` — AIAG 4th Edition DFMEA to AIAG-VDA 7-Step mapping rules.

## The 3-Level Design Structure Hierarchy
1. **Higher Level Element (1. System):** Top-level system or vehicle item (e.g. `"Electrical Power Distribution"`). Constant across all rows of the system.
2. **Focus Element (2. System Element / Interface):** Subsystem or assembly under evaluation (e.g. `"Bus Bar"`).
3. **Lower Level Element (3. Component Element):** Component part or material interface responsible for the failure cause.

## 20-Column Canonical Output Schema

```json
[
  {
    "higher_level_element":              "string",
    "focus_element":                     "string",
    "lower_level_element":               "string",
    "system_function":                   "string",
    "focus_function":                    "string",
    "design_characteristic":             "string",
    "failure_effect_fe":                 "string",
    "severity_rating":                   "integer",
    "failure_mode_fm":                   "string",
    "special_characteristic_class":      "CC | SC | null",
    "design_cause_fc":                   "string",
    "current_prevention_control":        "string | null",
    "occurrence_rating":                 "integer",
    "current_detection_control":         "string | null",
    "detection_rating":                  "integer",
    "action_priority_ap":                "H | M | L",
    "recommended_design_action":         "string | null",
    "responsible_engineer":              "string | null",
    "target_date":                       "string | null",
    "action_status":                     "string | null"
  }
]
```

## Field Derivation & Preservation Policy

1. **CARRY (Source Preservation):**
   - Core failure chain: `Failure Effect (FE)`, `Severity Rating (S)`, `Failure Mode (FM)`, `Design Cause (FC)`, `Prevention Control`, `Occurrence Rating (O)`, `Detection Control`, `Detection Rating (D)` are copied verbatim.
   - Reordering rule: `Failure Effect` and `Severity` precede `Failure Mode`.
   - Focus function / requirement is carried directly from source.

2. **AUTHOR (Grounded Quality Engineering Fields):**
   - 3-level structure elements (`higher_level_element`, `focus_element`, `lower_level_element`) and their corresponding functions/characteristics are grounded in the source function groups and engineering specifications.
   - `action_priority_ap`: Computed deterministically from $S \times O \times D$ using the AIAG-VDA Action Priority table (`H`, `M`, `L`). Replaces legacy RPN.

3. **ABSTAIN (Honest Blanks):**
   - Design optimization fields (`responsible_engineer`, `target_date`, `action_status`, post-action ratings) remain blank unless verified test results or engineering signoffs exist in source.
   - CAD/CAE model IDs and drawing numbers remain honest blanks unless provided.

## Verification & Acceptance Criteria

| # | Rule | Enforcement | Description |
|---|---|---|---|
| V1 | Schema Completeness | reject_document | Every row contains all 20 canonical AIAG-VDA Design keys |
| V2 | Exact Row Count Equality | reject_document | Exactly 1-to-1 row count matching source failure modes (e.g. 35 rows in $\to$ 35 rows out) |
| V3 | 3-Level Hierarchy Consistency | reject_document | Higher Level (System) must remain constant; Focus Element must be populated and consistent |
| V4 | Action Priority Validity | reject_row | Action Priority must strictly be 'H', 'M', or 'L' based on AIAG-VDA rubric |
| V5 | Special Characteristic Class | reject_row | Characteristics with $S \ge 8$ must be evaluated for 'CC' or 'SC' classification |
| V6 | Honest Abstention | reject_row | No fabricated engineer names, test completion dates, or speculative post-action ratings |