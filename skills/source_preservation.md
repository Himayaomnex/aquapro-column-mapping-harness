---
name: source_preservation
purpose: The fundamental rule for handling customer source content in any automotive quality engineering document transformation.
applies_when: any task that produces an output document from an uploaded or referenced source document (PFMEA, DFMEA, Control Plan)
not_for: pure greenfield generation where no source document exists
---

# Source Preservation Invariant

The uploaded workbook is the customer's authoritative legal and engineering record. In any transformation or conversion:

1. **Carried Content is Copied Verbatim:**
   - Same text, same numbers, same terminology, same abbreviations, same row order.
   - You do NOT "improve", paraphrase, summarize, or reword carried customer text.
   - Misspellings in source headers or text (e.g., "Occurence") are preserved as-is.

2. **Exact 1-to-1 Row-Count Equality:**
   - One source row = exactly one output row.
   - A row added is an invention (hallucination).
   - A row removed is data loss (critical non-conformance).
   - Turning a 35-row source into 106 rows is a catastrophic failure mode.

3. **Only Author What the Source Cannot Supply:**
   - Only author columns that the target standard (e.g., AIAG-VDA 7-Step or AIAG Control Plan) introduces and the source lacks.
   - Authored values must be strictly grounded in the row's own carried context, never in generic part knowledge.

4. **Preserve Customer Content Over Authoring Defaults:**
   - When the customer file already carries content (e.g., `Process Segment Name`, `Product Characteristics`, or existing controls), carry it directly.
   - Never overwrite customer data with default templates or blank fields.

5. **Unmapped Source Columns are Explicitly Reported:**
   - Any source column that has no target equivalent must be noted in unmapped fields for audit traceability.
   - Never silently drop customer data or force it into an unrelated column.

## Validation Expectations
- `row_count`: Source row count == Output row count.
- `preservation`: Every carried cell is byte-identical to its source cell.
- A single reworded or missing carried cell fails validation.
