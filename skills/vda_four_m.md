---
name: vda_four_m
purpose: How to assign the mandatory Four M (4M) work element category to each failure cause in an AIAG-VDA Process FMEA.
applies_when: authoring or validating the "Four M" / "Work Element" column of an AIAG-VDA PFMEA
not_for: Design FMEAs (DFMEA has no 4M column; DFMEAs classify physical and engineering design causes)
---

# Four M (4M) Classification in AIAG-VDA PFMEA

Every failure cause in an AIAG-VDA Process FMEA originates from a process work element. The AIAG-VDA standard categorizes work elements into exactly four distinct classes:

## The Permitted Vocabulary — Exactly Four Values

- **Machine:**
  - Machine wear, tooling degradation, fixture misalignment, press pressure drop, sensor drift, robot repeat error, equipment breakdown, improper machine calibration.
- **Method:**
  - Incorrect process parameter recipe, ambiguous work instruction, improper sequence of operations, faulty program logic, inadequate cooling cycle time, incomplete procedural guideline.
- **Material:**
  - Raw material variation, out-of-spec sheet thickness, contaminated oil/fluid, defective supplier subcomponent, wrong alloy grade, surface oxidation prior to assembly.
- **Man:**
  - Operator loading error, missed manual inspection step, lack of training/certification, fatigue, incorrect manual torque application, ergonomics-induced handling defect.

## The Negative Constraint — No Fifth Value

- **"Milieu" (Environment) is NOT permitted.** The AIAG-VDA standard incorporates environmental factors (temperature, humidity, dust) under `Machine` (facility controls) or `Method`. Any appearance of "Milieu" or arbitrary categories is an audit failure.

## Decision Procedure
1. Read the row's specific **Failure Cause (`FC`)** (not the failure mode or effect).
2. Determine the physical root cause mechanism.
3. Select the single dominant 4M category whose elimination prevents the cause.
4. If ambiguous between tooling and parameters, determine whether the physical tool (`Machine`) or the setup procedure (`Method`) was primary.

## Validation Expectations
- The cell must be exactly one of: `"Machine"`, `"Method"`, `"Material"`, `"Man"` (case-sensitive).
- Null or unclassified entries are not permitted in final PFMEA VDA rows.
