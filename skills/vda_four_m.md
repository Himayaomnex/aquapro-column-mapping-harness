---
name: vda_four_m
purpose: How to classify the work element category for each failure cause in an AIAG-VDA Process FMEA.
applies_when: authoring the work element column in an AIAG-VDA PFMEA
not_for: Design FMEAs — DFMEA has no 4M column
---

# Four M Classification

In the AIAG-VDA Process FMEA, every failure cause originates from a process work element. That work element is classified into exactly one of four categories.

## The four permitted values

**Man** — The cause originates from human action or inaction.
Examples: operator loading error, missed inspection step, insufficient training, fatigue, incorrect manual torque.

**Machine** — The cause originates from equipment, tooling, or fixturing.
Examples: tool wear, fixture misalignment, sensor drift, press pressure drop, calibration failure, robot positioning error.

**Material** — The cause originates from incoming material or components.
Examples: out-of-specification sheet thickness, contaminated fluid, wrong alloy grade, defective supplier subcomponent, surface oxidation.

**Method** — The cause originates from the process design or work instructions.
Examples: incorrect parameter recipe, ambiguous work instruction, wrong operation sequence, missing cooling cycle, inadequate procedure.

## What is not permitted

"Milieu" (environment) is not a valid category. Environmental factors belong under Machine (facility/equipment controls) or Method (process design). A documented defect occurred when a paraphrased copy of this vocabulary introduced "Milieu" into a delivered customer document — this rule exists to prevent that.

## How to assign the category

1. Read the failure **Cause** — not the mode, not the effect. The category describes where the cause comes from.
2. Identify the dominant mechanism: is it the operator, the equipment, the incoming material, or the process design?
3. If more than one category could apply, select the one whose elimination would most directly remove the cause.
4. The cell must never be empty. If the cause text is ambiguous, classify from the failure mode's mechanism.

## Validation
The permitted values are: `Man`, `Machine`, `Material`, `Method` — case-sensitive, exactly as written. Any other value is a validation failure.
