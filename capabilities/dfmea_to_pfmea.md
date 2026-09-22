# Capability Contract: dfmea_to_pfmea

## Consumer
Simultaneous Engineering teams, Manufacturing Launch Engineers, and APQP Quality Leads bridging Product Design FMEA outputs into manufacturing Process FMEA risk analysis (APQP Phase 2 to Phase 3 handoff).

## Purpose
Establish formal engineering linkage between Design and Process FMEA:
- **Inherit Special Characteristics:** Carry Critical and Special Characteristics (`CC`/`SC`) identified in DFMEA directly into the PFMEA process spine.
- **Translate Design Causes into Process Failure Modes:** Map design failure mechanisms into assembly line process failure modes.
- **Mandate Error-Proofing (Poka-Yoke):** Enforce automated containment or error-proofing whenever design severity $S \ge 8$.

## Applicable Methodology Skills
- `skills/source_preservation.md` — Invariant of verbatim carry and zero hallucination.
- `skills/dfmea_to_pfmea_linking.md` — Rules for cascading design risk into manufacturing operations.

## Output Schema

```json
[
  {
    "dfmea_part_name":                   "string",
    "design_characteristic":             "string",
    "dfmea_severity_rating":             "integer",
    "special_characteristic_class":      "CC | SC | null",
    "dfmea_failure_effect":              "string",
    "dfmea_design_cause":                "string",
    "pfmea_operation_number":            "string",
    "pfmea_operation_name":              "string",
    "pfmea_process_failure_mode":        "string",
    "pfmea_process_failure_cause":       "string",
    "error_proofing_poka_yoke":          "string | null",
    "recommended_process_control":       "string | null",
    "recommended_detection_method":      "string | null"
  }
]
```

## Field Derivation & Preservation Policy
1. **CARRY:** DFMEA part name, design characteristic, severity rating, and failure effects are carried verbatim.
2. **AUTHOR:**
   - Linkage to manufacturing operations (e.g. torque station, press fit).
   - If $S \ge 8$, error-proofing / Poka-Yoke requirement must be specified.
3. **ABSTAIN:** Shop-floor machine serial numbers, specific fixture IDs, or unverified tooling parameters remain blank.

## Verification & Acceptance Criteria

| # | Rule | Enforcement | Description |
|---|---|---|---|
| V1 | Traceability Coverage | reject_document | Every critical DFMEA characteristic must link to at least one PFMEA operation |
| V2 | Mandatory Error-Proofing | reject_row | For design severity $S \ge 8$, `error_proofing_poka_yoke` must be flagged |
| V3 | Special Characteristic Preservation | reject_row | Special characteristics (CC/SC) from DFMEA must be preserved; severity cannot be downgraded |
| V4 | Causal Traceability | reject_row | Process failure mode must logically prevent or detect the design root cause |
| V5 | Zero Hallucination | reject_row | No invented tooling IDs or machine model numbers |