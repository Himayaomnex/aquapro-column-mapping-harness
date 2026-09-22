---
name: source_preservation
purpose: The fundamental rule for handling customer source content in any automotive quality engineering document transformation.
applies_when: any task that produces an output document from a source document
not_for: pure greenfield generation with no source document
---

# Source Preservation

The customer workbook represents the authoritative engineering baseline. These principles apply without exception in every document transformation:

## Core Principles

**1. Verbatim Transfer**
Carried content must be transferred verbatim: exact terminology, numeric values, abbreviations, and engineering phrasing. Do not rephrase, standardize, or attempt to correct customer terminology. Retain original spelling and designations as recorded.

**2. Strict Row-to-Row Fidelity**
Every source failure analysis or process operation corresponds strictly to one row in the output document. Row inflation distorts risk metrics, while row consolidation results in loss of engineering traceability.

**3. Minimal Authoring Boundary**
Author only the specific fields introduced by the target standard that have no direct counterpart in the source record. Every authored value must be directly traceable to evidence within that specific row.

**4. Preservation of Existing Classifications & Segments**
If the source workbook provides classifications, process segments, or control designations, retain them. Never overwrite customer-defined classifications with system defaults.

**5. Transparent Tracking of Unmapped Data**
Source columns that do not map to the target standard must be captured in the execution audit log rather than discarded silently or forced into incompatible fields.

## Validation Principles
- Total output rows must match source input rows exactly.
- All transferred content must maintain byte-for-byte fidelity with the source workbook.
