# Tool Registry

The complete action space available to the agent at every `plan` turn.
Each tool is an atomic, deterministic Python function with a typed signature.
No tool makes an LLM call internally. All reasoning lives in prompts.

---

## Core Active Tools

### workbook_parser

```
workbook_parser(file_path: str) -> list[dict]
```

Reads an uploaded Excel file (.xlsx) using openpyxl/pandas.
Identifies header rows, extracts all data rows as key-value dicts with
raw Excel header strings as keys.
Deterministic: no LLM calls. Header detection uses row-profiling heuristics.
Returns an empty list if the sheet has no data rows.

---

### column_mapper

```
column_mapper(raw_rows: list[dict]) -> MappedContext
```

Translates raw Excel headers into canonical concept keys using the synonym
table in `schemas/canonical_context.md`.
Groups rows by `operation_number`.
Classifies each populated canonical concept as CARRY or needs-AUTHOR per
the active capability contract.
Unrecognized headers are retained as `unmapped_fields` on the row — never dropped.
Deterministic: fixed lookup table. No LLM calls.

---

### excel_builder

```
excel_builder(mapped_context: MappedContext, draft_fields: dict = None, document_type: str = "control_plan_from_pfmea") -> list[Any]
```

The unified document builder supporting all APQP / FMEA document types:
- `control_plan_from_pfmea`: Assembles 16-column AIAG Control Plan rows (CARRY, AUTHOR, ABSTAIN).
- `pfmea_aiag_to_vda`: Assembles 7-Step AIAG-VDA PFMEA rows with Action Priority ($S \times O \times D \to H/M/L$) and 4M elements.
- `dfmea_aiag_to_vda`: Assembles AIAG-VDA DFMEA rows with Design Action Priority.
- `dfmea_to_pfmea`: Assembles DFMEA-to-PFMEA traceability matrix rows.
- Generic fallback for ad-hoc mappings.

---

### validator

```
validator(rows: list[Any], mapped_context: MappedContext = None, capability_id: str = "control_plan_from_pfmea") -> list[Violation]
```

Loads verification rules from `capabilities/{capability_id}.md` and checks
every rule mechanically against the built rows.
Returns `list[Violation]` — an empty list means 100% pass.
Never returns a boolean. Never raises exceptions.

Each `Violation` contains: `rule_id`, `on_fail` (reject_document | reject_row),
`row_identifier`, `statement`, `detail`.

Rules checked:
- V1: Format & schema completeness (all required keys present, correct types)
- V2: Operation set equality (source operations match output operations)
- V3: Mandatory Abstention (unsupported/unspecified columns must be null)
- V4: Evidence traceability (authored values match source evidence)
- V5: Quality interlocks (e.g. Reaction Plan requires Detective Control; Action Priority matches S/O/D)

---

### excel_exporter

```
excel_exporter(rows: list[Any], output_path: str, execution_log: ExecutionLog = None) -> str
```

Writes validated rows into an industry-compliant `.xlsx` file.
Supports both `ControlPlanRow` objects and generic dictionary row structures.
Also writes `execution_log.json` alongside the xlsx containing:
  - Per-row source traceability (source_sheet, source_row)
  - Unmapped header report
  - Violations found and whether repaired or degraded
  - Final status: COMPLETE | DEGRADED | FAILED

Returns the absolute path to the output `.xlsx` file.

---

### rag_retriever

```
rag_retriever(production_item_name: str, top_k: int = 20) -> MappedContext
```

Queries the PFMEA knowledge base / vector store by production item name.
Used in Scenario 2 when no file is uploaded.

---
