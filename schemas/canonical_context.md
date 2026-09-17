# Canonical Context -- Schema

Shared vocabulary for the entire harness. `column_mapper` translates raw source
Excel headers from any uploaded PFMEA workbook into these canonical concept keys.
Nothing downstream (compose, validator, excel_exporter) ever sees a raw header string.

---

## 1. MappedContextItem (Internal Data Model)

One item per (operation x PFMEA field) pair after `column_mapper` runs.

```python
class MappedContextItem(BaseModel):
    # Identity (always required)
    operation_number: str                       # e.g. "10", "20", "030"
    operation_name: str                         # e.g. "CNC Rough Milling"
    production_item_name: str                   # e.g. "Bracket Assembly LH"

    # Hierarchy (CARRY fields for the document spine)
    process_segment_name: Optional[str] = None  # e.g. "Machining" (L1 spine node)

    # Characteristics (CARRY fields)
    product_characteristic: Optional[str] = None
    process_characteristic: Optional[str] = None

    # PFMEA analysis (AUTHOR source fields)
    failure_mode: Optional[str] = None
    failure_effect: Optional[str] = None
    failure_cause: Optional[str] = None
    severity_rating: Optional[int] = None       # 1-10, AIAG standard scale
    occurrence_rating: Optional[int] = None     # 1-10, AIAG standard scale
    preventive_control: Optional[str] = None
    detective_control: Optional[str] = None
    detection_rating: Optional[int] = None      # 1-10, AIAG standard scale

    # Source traceability
    source_sheet: str                           # Sheet name in the workbook
    source_row: int                             # Row number in the workbook
    unmapped_fields: list[str] = []             # Headers seen but not recognized
```

---

## 2. Canonical Concepts -- PFMEA Source Side

`column_mapper` matches incoming Excel headers against these known aliases.
The right column shows all currently known header variations from `EXCEL_FORMATS["pfmea"]`.

| Canonical Concept          | Known Source Headers (PFMEA)                         |
|----------------------------|------------------------------------------------------|
| `production_item_name`     | "Production Item Name"                               |
| `process_segment_name`     | "Process Segment Name"                               |
| `operation_number`         | "Operation Number"                                   |
| `operation_name`           | "Operation Name"                                     |
| `product_characteristic`   | "Product Characteristics"                            |
| `process_characteristic`   | "Process Characteristics"                            |
| `failure_mode`             | "Potential Failure Mode"                             |
| `failure_effect`           | "Potential Effects of Failure"                       |
| `severity_rating`          | "Severity Rating: Failure Mode Effect"               |
| `failure_cause`            | "Potential Causes of Failure"                        |
| `occurrence_rating`        | "Cause: Occurence Rating"                            |
| `preventive_control`       | "Preventive Controls"                                |
| `preventive_control_rating`| "Preventive Controls: Occurence Rating"              |
| `detective_control`        | "Detective Controls"                                 |
| `detection_rating`         | "Detective Controls: Rating"                         |

**Unmapped header rule:**
Any header not in this table is NOT dropped silently.
It is retained as `unmapped_fields` on the row and reported in `execution_log.json`.
This makes column mapping gaps visible rather than swallowed.

---

## 3. Canonical Concepts -- Control Plan Output Side

The 16 AIAG 4th Edition columns that `control_plan_builder` must populate.
Column numbers here match the CARRY/AUTHOR/ABSTAIN table in `capabilities/control_plan_from_pfmea.md`.

| # | Canonical Key                       | Type           |
|---|-------------------------------------|----------------|
| 1 | `production_item_name`              | str            |
| 2 | `process_segment_name`              | Optional[str]  |
| 3 | `operation_number`                  | str            |
| 4 | `operation_name`                    | str            |
| 5 | `product_characteristic`            | Optional[str]  |
| 6 | `process_characteristic`            | Optional[str]  |
| 7 | `special_characteristic_class`      | Optional[str]  |
| 8 | `specification_tolerance`           | None (ABSTAIN) |
| 9 | `evaluation_measurement_technique`  | Optional[str]  |
|10 | `tool_number`                       | None (ABSTAIN) |
|11 | `tool_name`                         | None (ABSTAIN) |
|12 | `gage_number`                       | None (ABSTAIN) |
|13 | `control_method`                    | Optional[str]  |
|14 | `sample_size`                       | None (ABSTAIN) |
|15 | `sample_frequency`                  | None (ABSTAIN) |
|16 | `reaction_plan`                     | Optional[str]  |
