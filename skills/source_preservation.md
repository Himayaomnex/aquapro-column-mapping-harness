---
name: source_preservation
purpose: The fundamental rule for handling customer source content in any automotive quality engineering document transformation.
applies_when: any task that produces an output document from a source document
not_for: pure greenfield generation with no source document
---

# Source Preservation

The uploaded workbook is the customer's authoritative engineering record. These rules apply without exception in every transformation:

## Rules

**1. Carried content is copied verbatim.**
Same text, same numbers, same abbreviations, same row order. Do not improve, rephrase, or correct customer content. A misspelling in the source ("Occurence") is carried as-is.

**2. The output has exactly as many rows as the source.**
One source row produces one output row. A row added is an invention. A row removed is data loss. The documented failure mode for this task was an agent turning a 35-row source into 106 rows — that is the defect this rule exists to prevent.

**3. Only author what the source cannot supply.**
Author only the columns that the target standard introduces and the source has no equivalent for. Every authored value must be grounded in that row's own carried content.

**4. Never overwrite customer data with a default.**
If the source already provides content for a column — including `Process Segment Name`, existing controls, or classifications — carry it. Do not replace it with a generated default.

**5. Unmapped source columns are reported, never dropped.**
Any source column with no target equivalent is listed as unmapped in the audit trail. It is never silently discarded or forced into an unrelated column.

## Validation
- Row count: output row count must equal source row count.
- Preservation: every carried cell must be byte-identical to its source cell.
- A single reworded carried cell is a validation failure.
