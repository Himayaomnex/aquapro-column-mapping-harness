---
name: vda_four_m
purpose: Classification methodology for assigning 4M work element categories to process failure causes in AIAG-VDA Process FMEA.
applies_when: authoring the work element column in an AIAG-VDA PFMEA
not_for: Design FMEAs — DFMEA does not evaluate manufacturing work elements
---

# Four M Classification

In AIAG-VDA Process FMEA, every failure cause originates from a specific process work element. Each work element is classified into one of four standard categories.

## Permitted Categories

**Man**
- Root cause originates from human operation, cognitive load, or physical execution.
- Examples: operator part loading orientation, skipped manual verification, ergonomic strain, incorrect manual torque application.

**Machine**
- Root cause originates from machinery, tooling, sensors, or automated fixtures.
- Examples: cutting tool wear, fixture locator misalignment, pneumatic pressure loss, transducer drift, robotic motion repeatability.

**Material**
- Root cause originates from incoming raw materials, parts, or consumable fluids.
- Examples: raw material tensile variation, chemical contamination, supplier component flash, surface corrosion on incoming stock.

**Method**
- Root cause originates from process parameters, operational recipes, or work instructions.
- Examples: thermal profile recipe, incorrect tightening sequence, inadequate dwell time, ambiguous assembly instructions.

## Harmonization Rules

In AIAG-VDA 1st Edition harmonization, environmental influences (formerly termed "Milieu") are mapped into the controlling mechanism:
- Equipment-related environmental controls (ambient temperature control, ventilation) are classified under **Machine**.
- Environmental operating specifications and procedures are classified under **Method**.

## Assignment Methodology

1. Analyze the root **Cause** rather than the failure mode or effect.
2. Identify the primary physical or operational mechanism responsible for initiating the failure chain.
3. If multiple factors contribute, select the category corresponding to the primary containment or prevention point.
4. The classification field must never remain blank.

## Validation Principles
The category must strictly evaluate to one of: `Man`, `Machine`, `Material`, or `Method`. Any variation is rejected during schema validation.
