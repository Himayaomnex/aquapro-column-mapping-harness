"""
Excel Exporter Tool (Industry Benchmark Grade).
Exports validated quality engineering documents into professional, industry-compliant
workbooks with Header and Body sheets matching automotive OEM/Tier-1 APQP benchmarks.
"""

from typing import List, Optional, Any, Dict
import os
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from .models import ControlPlanRow, ExecutionLog


# Body Column Widths matching Benchmark
BENCHMARK_BODY_WIDTHS = {
    "A": 5.0,    # Op. Grp. Sequence
    "B": 5.0,    # Op#
    "C": 22.0,   # Op Name
    "D": 11.0,   # Machine No
    "E": 20.0,   # Machine Name
    "F": 6.0,    # S.No
    "G": 16.0,   # Process Char
    "H": 22.0,   # Product Char
    "I": 14.0,   # Special Char Class
    "J": 18.0,   # Spec / Tolerance
    "K": 22.0,   # Control Method
    "L": 11.0,   # Gage Number
    "M": 16.0,   # Evaluation Technique
    "N": 11.0,   # Sample Size
    "O": 11.0,   # Sample Frequency
    "P": 22.0,   # Reaction Plan
}


def _build_benchmark_header_sheet(wb: openpyxl.Workbook, part_name: str = "CNC Operation"):
    """Constructs the official AIAG APQP Control Plan Header sheet."""
    ws = wb.create_sheet(title="Header", index=0)

    # Styles
    f_title = Font(name="Calibri", size=12, bold=True)
    f_label = Font(name="Calibri", size=8, bold=False, color="505050")
    f_val = Font(name="Calibri", size=9, bold=True)
    thin_border = Border(
        left=Side(style="thin", color="B0B0B0"),
        right=Side(style="thin", color="B0B0B0"),
        top=Side(style="thin", color="B0B0B0"),
        bottom=Side(style="thin", color="B0B0B0")
    )
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")

    # Column widths for Header
    h_widths = {
        "A": 28.0, "B": 8.0, "C": 2.0, "D": 10.0, "E": 10.0,
        "F": 2.0, "G": 14.0, "H": 18.0, "I": 4.0, "J": 18.0,
        "K": 2.0, "L": 24.0, "M": 24.0
    }
    for col_l, w in h_widths.items():
        ws.column_dimensions[col_l].width = w

    # Row 1: Title
    ws["H1"] = "CONTROL PLAN"
    ws["H1"].font = f_title
    ws["H1"].alignment = align_center

    # Merged ranges
    merges = [
        "A3:E3", "A4:E4", "G3:I3", "G4:I4",
        "A6:B6", "A7:B7", "C6:E6", "C7:E7", "G6:J6", "G7:J7", "L6:M6", "L7:M7",
        "A9:B9", "A10:B10", "C9:E9", "C10:E10", "G9:J9", "G10:J10", "L9:M9", "L10:M10",
        "A12:C12", "A13:C13", "D12:E12", "D13:E13", "G12:J12", "G13:J13", "L12:M12", "L13:M13"
    ]
    for m in merges:
        ws.merge_cells(m)

    # Row 3 & 4
    ws["A3"] = "Control Plan Number"
    ws["A3"].font = f_label
    ws["G3"] = "Key Contact"
    ws["G3"].font = f_label
    ws["J3"] = "Phone"
    ws["J3"].font = f_label
    ws["L3"] = "Date (Orig.)"
    ws["L3"].font = f_label
    ws["M3"] = "Date (Rev.)"
    ws["M3"].font = f_label

    # Row 6 & 7
    ws["A6"] = "Part Number"
    ws["A6"].font = f_label
    ws["C6"] = "Latest Change Level/Date"
    ws["C6"].font = f_label
    ws["G6"] = "Core Team"
    ws["G6"].font = f_label
    ws["L6"] = "Customer Engineering Approval/Date (If Req\'d.)"
    ws["L6"].font = f_label

    # Row 9 & 10
    ws["A9"] = "Part Name"
    ws["A9"].font = f_label
    ws["A10"] = part_name
    ws["A10"].font = f_val
    ws["C9"] = "Description"
    ws["C9"].font = f_label
    ws["G9"] = "Supplier/Plant Approval/Date"
    ws["G9"].font = f_label
    ws["L9"] = "Customer Quality Approval/Date (If Req\'d.)"
    ws["L9"].font = f_label

    # Row 12 & 13
    ws["A12"] = "Supplier/Plant"
    ws["A12"].font = f_label
    ws["D12"] = "Supplier Code"
    ws["D12"].font = f_label
    ws["G12"] = "Other Approval/Date (If Req\'d.)"
    ws["G12"].font = f_label
    ws["L12"] = "Other Approval/Date (If Req\'d.)"
    ws["L12"].font = f_label

    # Add borders to header fields
    for r in [3, 4, 6, 7, 9, 10, 12, 13]:
        for c in range(1, 14):
            ws.cell(r, c).border = thin_border


def _build_benchmark_body_sheet(ws: openpyxl.worksheet.worksheet.Worksheet, rows: List[Any]):
    """Constructs the official 3-row hierarchical AIAG Control Plan Body sheet."""
    # Styling
    fill_header = PatternFill(start_color="FFD3D3D3", end_color="FFD3D3D3", fill_type="solid")
    font_header = Font(name="Calibri", size=8, bold=False)
    font_data = Font(name="Calibri", size=8)
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin", color="A0A0A0"),
        right=Side(style="thin", color="A0A0A0"),
        top=Side(style="thin", color="A0A0A0"),
        bottom=Side(style="thin", color="A0A0A0")
    )

    # Set Column Widths
    for col_l, w in BENCHMARK_BODY_WIDTHS.items():
        ws.column_dimensions[col_l].width = w

    # Row Heights
    ws.row_dimensions[1].height = 22
    ws.row_dimensions[2].height = 22
    ws.row_dimensions[3].height = 18

    # Apply fills, fonts, and borders to all header cells (1..3, 1..16)
    for r in range(1, 4):
        for c in range(1, 17):
            cell = ws.cell(r, c)
            cell.fill = fill_header
            cell.font = font_header
            cell.border = thin_border
            cell.alignment = align_center

    # Row 1 Labels
    ws["A1"] = "Op. Grp. Sequence"
    ws["B1"] = "Op#"
    ws["C1"] = "Op Name"
    ws["D1"] = "num ,machine, device, jig, tools, for manufacturing"
    ws["F1"] = "Characteristics"
    ws["I1"] = "Special Characteristic Class"
    ws["J1"] = "Methods"
    ws["L1"] = "Gage Number"
    ws["M1"] = "Methods"
    ws["P1"] = "Reaction Plan"

    # Row 2 Labels
    ws["D2"] = "No"
    ws["E2"] = "Name"
    ws["F2"] = "S.No"
    ws["G2"] = "Process"
    ws["H2"] = "Product"
    ws["J2"] = "Product/Process Specification/ Tolerance"
    ws["K2"] = "Control Method"
    ws["M2"] = "Evaluation/ Measurement Technique"
    ws["N2"] = "Sample"

    # Row 3 Labels
    ws["N3"] = "Size"
    ws["O3"] = "Frequency"

    # Merged Header Cells
    header_merges = [
        "A1:A3", "B1:B3", "C1:C3",
        "D1:E1", "F1:H1", "I1:I3", "J1:K1", "L1:L3", "M1:O1", "P1:P3",
        "D2:D3", "E2:E3", "F2:F3", "G2:G3", "H2:H3", "J2:J3", "K2:K3", "M2:M3", "N2:O2"
    ]
    for m in header_merges:
        ws.merge_cells(m)

    # Populate Data Rows starting at Row 4
    start_row = 4
    current_row = start_row
    op_start_rows = {}

    for idx, row_item in enumerate(rows, start=1):
        r_dict = row_item.to_dict() if hasattr(row_item, "to_dict") else row_item
        op_num = str(r_dict.get("operation_number") or "").strip()
        op_name = str(r_dict.get("operation_name") or "").strip()
        seq = str(r_dict.get("process_segment_name") or "1").strip()

        # Track operations for vertical merging
        if op_num not in op_start_rows:
            op_start_rows[op_num] = current_row
            is_first_of_op = True
        else:
            is_first_of_op = False

        row_vals = [
            seq if is_first_of_op else None,                                         # Col 1: Op. Grp. Sequence
            op_num if is_first_of_op else None,                                      # Col 2: Op#
            op_name if is_first_of_op else None,                                     # Col 3: Op Name
            r_dict.get("tool_number"),                                               # Col 4: No
            r_dict.get("tool_name"),                                                 # Col 5: Name
            None,                                                                    # Col 6: S.No
            r_dict.get("process_characteristic"),                                    # Col 7: Process
            r_dict.get("product_characteristic"),                                    # Col 8: Product
            r_dict.get("special_characteristic_class"),                              # Col 9: Special Char Class
            r_dict.get("specification_tolerance"),                                   # Col 10: Spec / Tolerance
            r_dict.get("control_method"),                                            # Col 11: Control Method
            r_dict.get("gage_number"),                                               # Col 12: Gage Number
            r_dict.get("evaluation_measurement_technique"),                          # Col 13: Eval Technique
            r_dict.get("sample_size"),                                               # Col 14: Sample Size
            r_dict.get("sample_frequency"),                                          # Col 15: Sample Freq
            r_dict.get("reaction_plan")                                              # Col 16: Reaction Plan
        ]

        ws.row_dimensions[current_row].height = 24
        for col_idx, val in enumerate(row_vals, start=1):
            cell = ws.cell(row=current_row, column=col_idx, value=val)
            cell.font = font_data
            cell.border = thin_border
            if col_idx in (1, 2, 4, 6, 9, 12, 14, 15):
                cell.alignment = align_center
            else:
                cell.alignment = align_left

        current_row += 1


def excel_exporter(
    rows: List[Any],
    output_path: str,
    execution_log: Optional[ExecutionLog] = None,
    document_title: str = "Quality Engineering Document"
) -> str:
    """
    Exports rows to professional Excel file matching official APQP benchmarks.
    Creates Header and Body sheets for Control Plans, with backward-compatible aliases.
    """
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    if not rows:
        print("[Excel Exporter] Warning: No rows to export.")
        return output_path

    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Remove default blank sheet

    sample_item = rows[0]
    sample_dict = sample_item.to_dict() if hasattr(sample_item, "to_dict") else sample_item

    is_control_plan = isinstance(sample_item, ControlPlanRow) or (
        isinstance(sample_dict, dict) and "reaction_plan" in sample_dict and "special_characteristic_class" in sample_dict
    )

    if is_control_plan:
        part_name = "CNC Operation"
        if isinstance(sample_item, ControlPlanRow) and sample_item.production_item_name:
            part_name = sample_item.production_item_name
        elif isinstance(sample_dict, dict) and sample_dict.get("production_item_name"):
            part_name = sample_dict["production_item_name"]

        # 1. Header Sheet
        _build_benchmark_header_sheet(wb, part_name=part_name)

        # 2. Body Sheet (The official 3-row hierarchical benchmark)
        ws_body = wb.create_sheet(title="Body")
        _build_benchmark_body_sheet(ws_body, rows)

        # 3. Control Plan Sheet (Alias for backward compatibility with unit tests)
        ws_cp = wb.create_sheet(title="Control Plan")
        _build_benchmark_body_sheet(ws_cp, rows)
    else:
        # Standard Generic Sheet for DFMEA / PFMEA 7-Step
        ws = wb.create_sheet(title="Body")
        headers = [(k, k.replace("_", " ").title()) for k in sample_dict.keys()]
        
        # Light gray header styling
        fill_header = PatternFill(start_color="FFD3D3D3", end_color="FFD3D3D3", fill_type="solid")
        font_header = Font(name="Calibri", size=9, bold=True)
        thin_border = Border(
            left=Side(style="thin", color="A0A0A0"),
            right=Side(style="thin", color="A0A0A0"),
            top=Side(style="thin", color="A0A0A0"),
            bottom=Side(style="thin", color="A0A0A0")
        )

        # Header Row
        ws.row_dimensions[1].height = 25
        for col_idx, (_, d_name) in enumerate(headers, start=1):
            cell = ws.cell(1, col_idx, d_name)
            cell.fill = fill_header
            cell.font = font_header
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border
            ws.column_dimensions[get_column_letter(col_idx)].width = max(len(d_name) + 4, 14)

        # Data Rows
        font_data = Font(name="Calibri", size=8)
        for r_idx, r_item in enumerate(rows, start=2):
            ws.row_dimensions[r_idx].height = 22
            r_d = r_item.to_dict() if hasattr(r_item, "to_dict") else r_item
            for c_idx, (k, _) in enumerate(headers, start=1):
                val = r_d.get(k)
                cell = ws.cell(r_idx, c_idx, val)
                cell.font = font_data
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

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
