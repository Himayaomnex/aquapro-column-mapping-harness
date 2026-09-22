---
name: vda_framework
purpose: The AIAG-VDA 1st Edition Harmonized FMEA Framework — explaining what the 7-step layout introduces over the legacy AIAG 4th Edition layout.
applies_when: any task that reads, writes, converts to, or validates an AIAG-VDA layout FMEA (Process or Design)
not_for: Control Plans and Process Flows (no VDA layout exists for Control Plans; Control Plans follow AIAG APQP)
---

# The AIAG-VDA Harmonized 7-Step Framework

The AIAG-VDA standard unifies American (AIAG) and German (VDA) automotive engineering standards into a 7-Step method:

- **Step 1: Planning and Preparation** (Project identification, boundaries, scope).
- **Step 2: Structure Analysis** (3-level structural hierarchy: Higher Level System / Process Item $\to$ Focus Element / Process Step $\to$ Lower Level Component / Work Element).
- **Step 3: Function Analysis** (Functional description and requirements for each structure level).
- **Step 4: Failure Analysis** (3-level failure net: Failure Effect [FE] $\to$ Failure Mode [FM] $\to$ Failure Cause [FC]).
- **Step 5: Risk Analysis** (Current Prevention & Detection Controls, Severity [S], Occurrence [O], Detection [D], and Action Priority [AP]).
- **Step 6: Optimization** (Mitigation actions, responsible party, target date, action status, and re-assessed risk).
- **Step 7: Results Documentation** (Risk reporting, executive audit summary, and customer communication).

## Key Structural Shifts from AIAG 4th Edition

1. **Reordering of the Failure Chain:**
   - In legacy 4th Edition: `Failure Mode` $\to$ `Failure Effect` $\to$ `Failure Cause`.
   - In AIAG-VDA 7-Step: Effects (and their Severity $S$) are placed BEFORE the Failure Mode (`Failure Effect [FE]` $\to$ `Severity` $\to$ `Failure Mode [FM]` $\to$ `Failure Cause [FC]`).

2. **Action Priority (AP) Replaces RPN:**
   - Risk Priority Number ($RPN = S \times O \times D$) is completely obsolete.
   - Action Priority evaluates $S, O, D$ logic combinations into three discrete priorities:
     - **High (H):** Mandatory action required; system/process change needed.
     - **Medium (M):** Action recommended; review controls.
     - **Low (L):** Action optional; controls are effective.

3. **Section Bands (Hierarchical Grouping):**
   - Columns are grouped into clear section bands: Structure Analysis, Function Analysis, Failure Analysis, Risk Analysis, and Optimization.

## Validation Expectations
- Section bands and 20-column canonical ordering are preserved.
- Ratings ($S, O, D$) are integers from 1 to 10.
- Action Priority ($AP$) must strictly match the AIAG-VDA evaluation logic table (`H`, `M`, `L`).
