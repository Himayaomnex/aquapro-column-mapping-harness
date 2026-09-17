"""
Excel Exporter Tool (Universal Multi-Document).
Writes validated document rows into professional .xlsx workbooks.
Supports:
  - AIAG 4th Edition Control Plan
  - AIAG-VDA 1st Edition PFMEA / DFMEA
  - Generic Tabular Document rows (dict or Pydantic)
Writes companion execution_log.json for audit and traceability.
Deterministic, zero LLM calls.
"""

from typing import List, Optional, Any, Dict
import os
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from .models import ControlPlanRow, ExecutionLog


AIAG_CONTROL_PLAN_HEADERS = [
    ("production_item_name", "Part / Process Description"),
    ("process_segment_name", "Process Segment"),
    ("operation_number", "Op #"),
    ("operation_name", "Operation Description"),
    ("product_characteristic", "Product Characteristics"),
    ("process_characteristic", "Process Characteristics"),
    ("special_characteristic_class", "Special Char Class"),
    ("specification_tolerance", "Specification / Tolerance"),
    ("evaluation_measurement_technique", "Evaluation / Measurement Technique"),
    ("tool_number", "Tool #"),
    ("tool_name", "Tool Description"),
    ("gage_number", "Gage #"),
    ("control_method", "Control Method"),
    ("sample_size", "Sample Size"),
    ("sample_frequency", "Sample Freq"),
    ("reaction_plan", "Reaction Plan"),
]


def excel_exporter(
    rows: List[Any],
    output_path: str,
    execution_log: Optional[ExecutionLog] = None,
    document_title: str = "Quality Engineering Document"
) -> str:
    """
    Exports rows to professional Excel file and writes companion execution_log.json.
    Supports both ControlPlanRow objects and generic dictionary rows.
    """
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    if not rows:
        print("[Excel Exporter] Warning: No rows to export.")
        return output_path

    # Determine headers
    sample_item = rows[0]
    sample_dict = sample_item.to_dict() if hasattr(sample_item, "to_dict") else sample_item

    # Check if AIAG Control Plan
    if isinstance(sample_item, ControlPlanRow) or (
        isinstance(sample_dict, dict) and "reaction_plan" in sample_dict and "special_characteristic_class" in sample_dict
    ):
        headers = AIAG_CONTROL_PLAN_HEADERS
        sheet_title = "Control Plan"
        banner_title = "AIAG 4th Edition — CONTROL PLAN"
    else:
        # Dynamic headers from dictionary keys
        headers = [(k, k.replace("_", " ").title()) for k in sample_dict.keys()]
        sheet_title = "Engineering Document"
        banner_title = document_title.upper()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title

    # Styling
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)

    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    # Title Banner (Row 1)
    end_col_letter = get_column_letter(len(headers))
    ws.merge_cells(f"A1:{end_col_letter}1")
    title_cell = ws["A1"]
    title_cell.value = banner_title
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="1F4E79")
    title_cell.alignment = Alignment(horizontal="left", vertical="center")

    # Column Headers (Row 3)
    header_row_idx = 3
    for col_idx, (_, display_name) in enumerate(headers, start=1):
        cell = ws.cell(row=header_row_idx, column=col_idx, value=display_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border
    ws.row_dimensions[header_row_idx].height = 32

    # Data Rows (Row 4+)
    data_font = Font(name="Calibri", size=10)
    for row_offset, row_item in enumerate(rows, start=header_row_idx + 1):
        r_dict = row_item.to_dict() if hasattr(row_item, "to_dict") else row_item
        for col_idx, (key, _) in enumerate(headers, start=1):
            val = r_dict.get(key)
            cell = ws.cell(row=row_offset, column=col_idx, value=val)
            cell.font = data_font
            cell.border = thin_border
            if key in ("operation_number", "special_characteristic_class", "severity_s", "occurrence_o", "detection_d", "action_priority_ap"):
                cell.alignment = center_align
            else:
                cell.alignment = left_align
        ws.row_dimensions[row_offset].height = 24

    # Adjust Column Widths
    for col_idx, (_, display_name) in enumerate(headers, start=1):
        col_letter = get_column_letter(col_idx)
        max_len = len(display_name)
        for r_idx in range(header_row_idx + 1, header_row_idx + 1 + min(len(rows), 50)):
            c_val = str(ws.cell(row=r_idx, column=col_idx).value or "")
            if len(c_val) > max_len:
                max_len = min(len(c_val), 40)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    abs_output_path = os.path.abspath(output_path)
    try:
        wb.save(abs_output_path)
    except PermissionError:
        base, ext = os.path.splitext(abs_output_path)
        alt_path = f"{base}_new{ext}"
        print(f"[Excel Exporter Warning] '{abs_output_path}' is currently open in Microsoft Excel. Saved to '{alt_path}' instead.")
        abs_output_path = alt_path
        wb.save(abs_output_path)
    wb.close()

    # Companion execution log
    log_path = os.path.splitext(abs_output_path)[0] + "_execution_log.json"
    log_data = (
        execution_log.model_dump()
        if execution_log
        else {
            "status": "COMPLETE",
            "output_file": abs_output_path,
            "output_rows_count": len(rows),
        }
    )
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)

    print(f"[Excel Exporter] Successfully exported {len(rows)} rows to '{abs_output_path}'")
    return abs_output_path
