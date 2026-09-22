# Capability Contract: pfmea_aiag_to_vda

## Consumer
Manufacturing Process Quality Engineers, APQP Program Managers, and Automotive Tier-1 Suppliers transitioning legacy AIAG 4th Edition PFMEAs to the harmonized AIAG-VDA 1st Edition standard.

## Purpose
Convert a legacy AIAG 4th Edition PFMEA into a fully compliant AIAG-VDA 1st Edition 7-Step PFMEA document.
Core question answered: **Given this legacy PFMEA, how is it correctly restructured into the 7-step harmonized standard — reordering the failure chain, classifying work elements into 4M, and replacing obsolete RPN with Action Priority (AP)?**

## Applicable Methodology Skills
- `skills/source_preservation.md` — Invariant of verbatim carry, 1-to-1 row preservation, and zero hallucination.
- `skills/vda_framework.md` — 7-Step harmonized structure, reordered failure chain, and section banding.
- `skills/vda_four_m.md` — Strict 4-value vocabulary (`Machine`, `Method`, `Material`, `Man`) derived from failure cause.
- `skills/pfmea_vda_mapping.md` — AIAG 4th Edition PFMEA to AIAG-VDA 7-Step mapping rules.

## The 7-Step AIAG-VDA Structure
1. **Step 1: Planning & Preparation** (Scope definition, process boundaries).
2. **Step 2: Structure Analysis** (Process Item $\to$ Process Step $\to$ Process Work Element [4M]).
3. **Step 3: Function Analysis** (Functions of the item, process step, and work element).
4. **Step 4: Failure Analysis** (Failure Effect [FE] $\to$ Failure Mode [FM] $\to$ Failure Cause [FC]).
5. **Step 5: Risk Analysis** (Current Prevention & Detection Controls, S, O, D ratings, and Action Priority [AP]).
6. **Step 6: Optimization** (Recommended preventive/detective actions, ownership, target date, and status).
7. **Step 7: Results Documentation** (Audit traceability and executive risk reporting).

## 20-Column Canonical Output Schema

```json
[
  {
    "process_item":                      "string",
    "process_step":                      "string",
    "work_element_4m":                   "Machine | Method | Material | Man",
    "process_function":                  "string",
    "product_characteristic":            "string | null",
    "process_characteristic":            "string | null",
    "failure_effect_fe":                 "string",
    "severity_rating":                   "integer",
    "failure_mode_fm":                   "string",
    "special_characteristic_class":      "CC | SC | null",
    "failure_cause_fc":                  "string",
    "current_prevention_control":        "string | null",
    "occurrence_rating":                 "integer",
    "current_detection_control":         "string | null",
    "detection_rating":                  "integer",
    "action_priority_ap":                "H | M | L",
    "prevention_action":                 "string | null",
    "detection_action":                  "string | null",
    "responsible_person":                "string | null",
    "target_completion_date":            "string | null",
    "status":                            "string | null"
  }
]
```

## Field Derivation & Preservation Policy

1. **CARRY (Source Preservation):**
   - Core failure chain: `Failure Effect (FE)`, `Severity Rating (S)`, `Failure Mode (FM)`, `Failure Cause (FC)`, `Prevention Control`, `Occurrence Rating (O)`, `Detection Control`, `Detection Rating (D)` are copied verbatim.
   - Reordering rule: `Failure Effect` and `Severity` precede `Failure Mode`.
   - `product_characteristic` and `process_characteristic` are carried directly.

2. **AUTHOR (Grounded Quality Engineering Fields):**
   - `work_element_4m`: Categorized strictly into `Machine`, `Method`, `Material`, or `Man` based on the root cause mechanism. "Milieu" is strictly forbidden.
   - `process_function`: Derived from operation name and characteristics, consistent across all rows of the operation.
   - `action_priority_ap`: Computed deterministically from $S \times O \times D$ using the AIAG-VDA Action Priority table (`H`, `M`, `L`).

3. **ABSTAIN (Honest Blanks):**
   - Optimization fields (`responsible_person`, `target_completion_date`, `status`, post-action ratings) remain blank unless physical test data or signoff exists in source.

## Verification & Acceptance Criteria

| # | Rule | Enforcement | Description |
|---|---|---|---|
| V1 | Schema Completeness | reject_document | Every row contains all 20 canonical AIAG-VDA keys |
| V2 | Exact Row Count Equality | reject_document | 100% row preservation: exactly 1 source row $\to$ 1 output row |
| V3 | Action Priority Validity | reject_row | Action Priority must strictly be 'H', 'M', or 'L' based on AIAG-VDA rubric |
| V4 | Strict 4M Vocabulary | reject_row | `work_element_4m` must be exactly one of: Machine, Method, Material, Man |
| V5 | Special Characteristic Class | reject_row | Rows with $S \ge 8$ must be evaluated for 'CC' or 'SC' classification |
| V6 | Honest Abstention | reject_row | No fabricated engineer names, completion dates, or post-action ratings |