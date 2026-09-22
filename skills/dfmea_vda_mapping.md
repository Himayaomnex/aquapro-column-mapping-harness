---
name: dfmea_vda_mapping
purpose: How to convert a legacy AIAG 4th Edition Design FMEA into an AIAG-VDA 1st Edition 7-Step DFMEA.
applies_when: converting an AIAG 4th Edition DFMEA workbook to the AIAG-VDA 7-Step standard
not_for: PFMEAs (use pfmea_vda_mapping); Control Plans (use control_plan_mapping)
---

# DFMEA: AIAG 4th Edition to AIAG-VDA 7-Step Conversion

Builds upon `source_preservation` and `vda_framework`.

## The Structural Difference in DFMEA
In AIAG 4th Edition DFMEAs, the design structure is represented flatly (Function Group, Function, Requirement, Failure Chain). In the AIAG-VDA 7-Step format, Design Structure Analysis requires a strict **3-Level Physical & Functional Hierarchy**:

1. **Higher Level Element (1. System):**
   - The top-level product assembly or vehicle system.
   - Grounded in `Production Item` or `Function Group` (e.g., `"Electrical Power Distribution"`).
   - Must remain constant across all rows within the system.

2. **Focus Element (2. Subsystem / System Element / Interface):**
   - The subsystem, assembly, or interface under evaluation.
   - Grounded in the source item or component name (e.g., `"Bus Bar"`).
   - Consistent across all rows for that subsystem.

3. **Lower Level Element (3. Component Element):**
   - The specific component, material interface, or feature being designed.
   - Derived from the component design requirement or physical part.

## Functional Breakdown (3 Levels of Functions & Requirements)
- **Higher Level Function:** What the overall system must achieve for the vehicle/customer.
- **Focus Function:** What the focus element does to fulfill the system function.
- **Design Characteristic / Lower Level Function:** Specific engineering specification, tolerance, or material property (e.g., `"Conduct Required Current without Excessive Temperature Rise"`).

## Carried Failure Chain
The failure analysis chain is carried verbatim from source:
- `Failure Effect (FE)` $\leftarrow$ `Potential Effects of Failure`
- `Severity (S)` $\leftarrow$ `Severity Rating` (reordered before Failure Mode)
- `Failure Mode (FM)` $\leftarrow$ `Potential Failure Mode`
- `Special Characteristic Class` $\leftarrow$ `Class` (CC/SC)
- `Design Cause (FC)` $\leftarrow$ `Potential Causes/Mechanisms of Failure`
- `Prevention Control (PC)` $\leftarrow$ `Current Design Controls Prevention`
- `Occurrence (O)` $\leftarrow$ `Occurrence Rating`
- `Detection Control (DC)` $\leftarrow$ `Current Design Controls Detection`
- `Detection (D)` $\leftarrow$ `Detection Rating`
- `Action Priority (AP)` $\leftarrow$ Calculated using AIAG-VDA $S \times O \times D$ logic (`H`, `M`, `L`).

## There is NO Four M in DFMEA
Design FMEAs analyze physical design mechanisms (wear, fatigue, yield, thermal expansion). Four M is exclusively a process/manufacturing tool.

## Validation Expectations
- Row count matches source row count exactly (e.g., 35 rows in $\to$ 35 rows out).
- System, Focus, and Lower Level elements are populated and consistent.
- AP is computed accurately.
- No fabricated engineer names or signoff dates.
