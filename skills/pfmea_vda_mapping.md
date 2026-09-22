---
name: pfmea_vda_mapping
purpose: How to convert a legacy AIAG 4th Edition Process FMEA into an AIAG-VDA 1st Edition 7-Step PFMEA.
applies_when: converting an AIAG 4th Edition PFMEA workbook to the AIAG-VDA 7-Step standard
not_for: DFMEAs (use dfmea_vda_mapping); Control Plans (use control_plan_mapping)
---

# PFMEA: AIAG 4th Edition to AIAG-VDA 7-Step Conversion

Builds upon `source_preservation`, `vda_framework`, and `vda_four_m`.

## Deterministic Carry (15 Carried Concepts)
The core failure analysis is carried verbatim from source:
1. `Process Item` $\leftarrow$ `Production Item Name`
2. `Process Step` $\leftarrow$ `Operation Number & Operation Name`
3. `Product Characteristic` $\leftarrow$ `Product Characteristic`
4. `Process Characteristic` $\leftarrow$ `Process Characteristic`
5. `Failure Mode (FM)` $\leftarrow$ `Potential Failure Mode`
6. `Failure Effect (FE)` $\leftarrow$ `Potential Effects of Failure`
7. `Severity (S)` $\leftarrow$ `Severity Rating` (reordered before Failure Mode)
8. `Special Characteristic Class` $\leftarrow$ `Class` (CC/SC)
9. `Failure Cause (FC)` $\leftarrow$ `Potential Causes/Mechanisms of Failure`
10. `Current Prevention Control (PC)` $\leftarrow$ `Current Process Controls Prevention`
11. `Occurrence (O)` $\leftarrow$ `Occurrence Rating`
12. `Current Detection Control (DC)` $\leftarrow$ `Current Process Controls Detection`
13. `Detection (D)` $\leftarrow$ `Detection Rating`
14. Source optimization notes $\leftarrow$ Carried if populated; otherwise blank.

## Derived and Authored Columns (3 Authored Concepts)
1. **Work Element (4M):**
   - Derived from `Failure Cause` following the `vda_four_m` skill (`Machine`, `Method`, `Material`, `Man`).
2. **Process Item Function:**
   - Derived from `Operation Name` and `Characteristics`. Represents what the manufacturing step achieves.
   - Consistent across all rows of the same operation.
3. **Action Priority (AP):**
   - Calculated deterministically from $S \times O \times D$ using the AIAG-VDA priority logic (`H`, `M`, `L`). Replaces legacy RPN.

## Honest Abstention
- Optimization fields (`Responsible Person`, `Target Completion Date`, `Status`, post-action ratings) must remain empty unless explicitly present in source evidence.

## Validation Expectations
- Row count equals source row count exactly (1-to-1).
- Carried cells match source text byte-for-byte.
- 4M category is valid and non-empty.
- AP is valid (`H`, `M`, or `L`).
