"""
Excel Exporter Tool (Industry Benchmark Grade).
Exports validated quality engineering documents into professional, industry-compliant
workbooks with Header, Body, and Footer sheets matching automotive OEM/Tier-1 APQP benchmarks:
  - CD6 Production Format (Header + Body + Footer, 18 columns)
  - CNC APQP Benchmark Format (Header + Body, 16 columns)
"""

from typing import List, Optional, Any, Dict
import os
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from .models import ControlPlanRow, ExecutionLog

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CD6_TEMPLATE = os.path.join(DATA_DIR, "CD6_Fr_Production_Item_Control_Plan.xlsx")
CNC_TEMPLATE = os.path.join(DATA_DIR, "CNC_Operation_Control_Plan_Benchmark.xlsx")


def _setup_cd6_headers(ws: openpyxl.worksheet.worksheet.Worksheet):
    """Sets up the authentic 18-column 2-row CD6 Control Plan Header if template not present."""
    body_widths = {
        "A": 4.0, "B": 5.0, "C": 24.0, "D": 14.0, "E": 12.0, "F": 12.0,
        "G": 14.0, "H": 18.0, "I": 6.0, "J": 8.0, "K": 34.0, "L": 20.0,
        "M": 10.0, "N": 20.0, "O": 16.0, "P": 12.0, "Q": 24.0, "R": 12.0
    }
    for col_l, w in body_widths.items():
        ws.column_dimensions[col_l].width = w

    fill_header = PatternFill(start_color="FFD3D3D3", end_color="FFD3D3D3", fill_type="solid")
    font_header = Font(name="Calibri", size=8, bold=True)
    thin_border = Border(
        left=Side(style="thin", color="FF808080"),
        right=Side(style="thin", color="FF808080"),
        top=Side(style="thin", color="FF808080"),
        bottom=Side(style="thin", color="FF808080")
    )
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for r in (1, 2):
        for c in range(1, 19):
            cell = ws.cell(r, c)
            cell.fill = fill_header
            cell.font = font_header
            cell.border = thin_border
            cell.alignment = align_center

    ws["A1"] = "Op. Grp. Sequence"
    ws["B1"] = "Op#"
    ws["C1"] = "Process Name / Operation Description"
    ws["D1"] = "Characteristics"
    ws["I1"] = "CCS"
    ws["J1"] = "Class"
    ws["K1"] = "Characteristics"
    ws["L1"] = "Sample"

    ws["D2"] = "Process Function"
    ws["E2"] = "num ,machine, device, jig, tools, for manufacturing"
    ws["F2"] = "No"
    ws["G2"] = "Process"
    ws["H2"] = "Product"
    ws["K2"] = "Product/Process Specification/ Tolerance"
    ws["L2"] = "Evaluation/ Measurement Technique"
    ws["M2"] = "Size"
    ws["N2"] = "Frequency"
    ws["O2"] = "Control Methods"
    ws["P2"] = "Responsibility to Control"
    ws["Q2"] = "Reaction Plan"
    ws["R2"] = "Operation Picture"

    merges = ["A1:A2", "B1:B2", "C1:C2", "D1:H1", "I1:I2", "J1:J2", "K1:K2", "L1:R1"]
    for m in merges:
        ws.merge_cells(m)


def _build_cd6_body(ws_b: openpyxl.worksheet.worksheet.Worksheet, rows: List[Any]):
    """Populates validated rows into CD6 18-column alternating specification & control sub-rows."""
    # Clean any previous merges in data rows
    for m in list(ws_b.merged_cells.ranges):
        if m.min_row > 2:
            ws_b.merged_cells.remove(m)
    if ws_b.max_row > 2:
        ws_b.delete_rows(3, ws_b.max_row - 2)

    font_data = Font(name="Calibri", size=8)
    thin_border = Border(
        left=Side(style="thin", color="FF808080"),
        right=Side(style="thin", color="FF808080"),
        top=Side(style="thin", color="FF808080"),
        bottom=Side(style="thin", color="FF808080")
    )
    align_center = Alignment(horizontal="center", vertical="top", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="top", wrap_text=True)

    current_row = 3
    op_blocks: List[Dict[str, Any]] = []
    current_op = None
    current_op_start = 3
    op_start_rows = set()

    for idx, row_item in enumerate(rows, start=1):
        r_dict = row_item.to_dict() if hasattr(row_item, "to_dict") else row_item
        op_num = str(r_dict.get("operation_number") or "").strip()
        op_name = str(r_dict.get("operation_name") or "").strip()
        seq = str(r_dict.get("process_segment_name") or "1").strip()
        is_first = op_num not in op_start_rows
        if is_first:
            op_start_rows.add(op_num)
            if current_op is not None and op_num != current_op:
                op_blocks.append({"op_num": current_op, "start": current_op_start, "end": current_row - 1})
                current_op_start = current_row
            current_op = op_num

        char_no = (
            r_dict.get("characteristic_id") or
            r_dict.get("tool_number") or
            r_dict.get("gage_number") or
            f"A_{op_num}_{idx}"
        )
        proc_func = r_dict.get("process_segment_name") or op_name
        tool = r_dict.get("tool_name") or r_dict.get("tool_number")
        proc_char = r_dict.get("process_characteristic")
        prod_char = r_dict.get("product_characteristic")
        ccs = r_dict.get("csr") or r_dict.get("ccs")
        char_class = r_dict.get("special_characteristic_class")
        spec_tol = r_dict.get("specification_tolerance")

        eval_tech = r_dict.get("evaluation_measurement_technique")
        sample_size = r_dict.get("sample_size")
        sample_freq = r_dict.get("sample_frequency")
        ctrl_method = r_dict.get("control_method")
        resp = r_dict.get("responsibility")
        reaction_plan = r_dict.get("reaction_plan")

        row_a = [
            seq if is_first else None,
            op_num if is_first else None,
            op_name if is_first else None,
            proc_func if is_first else None,
            tool,
            char_no,
            proc_char,
            prod_char,
            ccs,
            char_class,
            spec_tol,
            None, None, None, None, None, None, None
        ]

        row_b = [
            None, None, None, None, None, None, None, None, None, None, None,
            eval_tech,
            sample_size,
            sample_freq,
            ctrl_method,
            resp,
            reaction_plan,
            None
        ]

        r_a = current_row
        r_b = current_row + 1

        ws_b.row_dimensions[r_a].height = 24
        for c_idx, val in enumerate(row_a, start=1):
            cell = ws_b.cell(row=r_a, column=c_idx, value=val)
            cell.font = font_data
            cell.border = thin_border
            cell.alignment = align_center if c_idx in (1, 2, 6, 9, 10) else align_left

        ws_b.row_dimensions[r_b].height = 24
        for c_idx, val in enumerate(row_b, start=1):
            cell = ws_b.cell(row=r_b, column=c_idx, value=val)
            cell.font = font_data
            cell.border = thin_border
            cell.alignment = align_center if c_idx in (13, 14) else align_left

        # Merge Characteristic cells vertically across row_a and row_b (Cols F to K)
        for c_idx in range(6, 12):
            ws_b.merge_cells(start_row=r_a, start_column=c_idx, end_row=r_b, end_column=c_idx)
            c_align = align_center if c_idx in (6, 9, 10) else align_left
            ws_b.cell(row=r_a, column=c_idx).alignment = Alignment(
                horizontal=c_align.horizontal, vertical="center", wrap_text=True
            )

        current_row += 2

    # Close the last operation block
    if current_op is not None and current_row > current_op_start:
        op_blocks.append({"op_num": current_op, "start": current_op_start, "end": current_row - 1})

    # Merge Operation-level cells vertically across all rows in each operation (Cols A, B, C, D, R)
    for block in op_blocks:
        st = block["start"]
        en = block["end"]
        if en > st:
            for c_idx in (1, 2, 3, 4, 18):
                ws_b.merge_cells(start_row=st, start_column=c_idx, end_row=en, end_column=c_idx)
                c_align_h = "center" if c_idx in (1, 2) else "left"
                ws_b.cell(row=st, column=c_idx).alignment = Alignment(
                    horizontal=c_align_h, vertical="center", wrap_text=True
                )


def _export_cd6_format(rows: List[Any], output_path: str):
    """Exports to the exact CD6 Fr Production Item Control Plan format (Header + Body + Footer)."""
    if os.path.exists(CD6_TEMPLATE):
        wb = openpyxl.load_workbook(CD6_TEMPLATE)
        # Clean up microscopic columns in Footer sheet so it doesn't look squished
        if "Footer" in wb.sheetnames:
            ws_f = wb["Footer"]
            for col_letter in list(ws_f.column_dimensions.keys()):
                if len(col_letter) > 1 or col_letter > "K":
                    del ws_f.column_dimensions[col_letter]

        if "Control Plan" in wb.sheetnames:
            wb.remove(wb["Control Plan"])

        ws_b = wb["Body"]
        _build_cd6_body(ws_b, rows)
    else:
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        ws_b = wb.create_sheet(title="Body")
        _setup_cd6_headers(ws_b)
        _build_cd6_body(ws_b, rows)

    try:
        wb.save(output_path)
    except PermissionError:
        base, ext = os.path.splitext(output_path)
        alt_path = f"{base}_new{ext}"
        print(f"[Excel Exporter Warning] '{output_path}' is open in Excel. Saved to '{alt_path}' instead.")
        wb.save(alt_path)
    wb.close()


def _export_cnc_format(rows: List[Any], output_path: str, part_name: str = "CNC Operation"):
    """Exports to the exact CNC APQP Benchmark format (Header + Body, 16 columns)."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # 1. Header Sheet
    ws_h = wb.create_sheet(title="Header")
    _build_cnc_header(ws_h, part_name=part_name)

    # 2. Body Sheet (Single authoritative 16-column body sheet)
    ws_b = wb.create_sheet(title="Body")
    _build_cnc_body(ws_b, rows)

    try:
        wb.save(output_path)
    except PermissionError:
        base, ext = os.path.splitext(output_path)
        alt_path = f"{base}_new{ext}"
        print(f"[Excel Exporter Warning] '{output_path}' is open in Excel. Saved to '{alt_path}' instead.")
        wb.save(alt_path)
    wb.close()


def _build_cnc_header(ws: openpyxl.worksheet.worksheet.Worksheet, part_name: str):
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

    h_widths = {
        "A": 28.0, "B": 8.0, "C": 2.0, "D": 10.0, "E": 10.0,
        "F": 2.0, "G": 14.0, "H": 18.0, "I": 4.0, "J": 18.0,
        "K": 2.0, "L": 24.0, "M": 24.0
    }
    for col_l, w in h_widths.items():
        ws.column_dimensions[col_l].width = w

    ws["H1"] = "CONTROL PLAN"
    ws["H1"].font = f_title
    ws["H1"].alignment = align_center

    merges = [
        "A3:E3", "A4:E4", "G3:I3", "G4:I4",
        "A6:B6", "A7:B7", "C6:E6", "C7:E7", "G6:J6", "G7:J7", "L6:M6", "L7:M7",
        "A9:B9", "A10:B10", "C9:E9", "C10:E10", "G9:J9", "G10:J10", "L9:M9", "L10:M10",
        "A12:C12", "A13:C13", "D12:E12", "D13:E13", "G12:J12", "G13:J13", "L12:M12", "L13:M13"
    ]
    for m in merges:
        ws.merge_cells(m)

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

    ws["A6"] = "Part Number"
    ws["A6"].font = f_label
    ws["C6"] = "Latest Change Level/Date"
    ws["C6"].font = f_label
    ws["G6"] = "Core Team"
    ws["G6"].font = f_label
    ws["L6"] = "Customer Engineering Approval/Date (If Req\'d.)"
    ws["L6"].font = f_label

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

    ws["A12"] = "Supplier/Plant"
    ws["A12"].font = f_label
    ws["D12"] = "Supplier Code"
    ws["D12"].font = f_label
    ws["G12"] = "Other Approval/Date (If Req\'d.)"
    ws["G12"].font = f_label
    ws["L12"] = "Other Approval/Date (If Req\'d.)"
    ws["L12"].font = f_label

    for r in [3, 4, 6, 7, 9, 10, 12, 13]:
        for c in range(1, 14):
            ws.cell(r, c).border = thin_border


def _build_cnc_body(ws: openpyxl.worksheet.worksheet.Worksheet, rows: List[Any]):
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

    body_widths = {
        "A": 5.0, "B": 5.0, "C": 22.0, "D": 11.0, "E": 20.0, "F": 6.0,
        "G": 16.0, "H": 22.0, "I": 14.0, "J": 18.0, "K": 22.0, "L": 11.0,
        "M": 16.0, "N": 11.0, "O": 11.0, "P": 22.0
    }
    for col_l, w in body_widths.items():
        ws.column_dimensions[col_l].width = w

    ws.row_dimensions[1].height = 22
    ws.row_dimensions[2].height = 22
    ws.row_dimensions[3].height = 18

    for r in range(1, 4):
        for c in range(1, 17):
            cell = ws.cell(r, c)
            cell.fill = fill_header
            cell.font = font_header
            cell.border = thin_border
            cell.alignment = align_center

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

    ws["D2"] = "No"
    ws["E2"] = "Name"
    ws["F2"] = "S.No"
    ws["G2"] = "Process"
    ws["H2"] = "Product"
    ws["J2"] = "Product/Process Specification/ Tolerance"
    ws["K2"] = "Control Method"
    ws["M2"] = "Evaluation/ Measurement Technique"
    ws["N2"] = "Sample"

    ws["N3"] = "Size"
    ws["O3"] = "Frequency"

    merges = [
        "A1:A3", "B1:B3", "C1:C3",
        "D1:E1", "F1:H1", "I1:I3", "J1:K1", "L1:L3", "M1:O1", "P1:P3",
        "D2:D3", "E2:E3", "F2:F3", "G2:G3", "H2:H3", "J2:J3", "K2:K3", "M2:M3", "N2:O2"
    ]
    for m in merges:
        ws.merge_cells(m)

    start_row = 4
    current_row = start_row
    op_start_rows = {}

    for idx, row_item in enumerate(rows, start=1):
        r_dict = row_item.to_dict() if hasattr(row_item, "to_dict") else row_item
        op_num = str(r_dict.get("operation_number") or "").strip()
        op_name = str(r_dict.get("operation_name") or "").strip()
        seq = str(r_dict.get("process_segment_name") or "1").strip()

        is_first_of_op = op_num not in op_start_rows
        if is_first_of_op:
            op_start_rows[op_num] = current_row

        row_vals = [
            seq if is_first_of_op else None,
            op_num if is_first_of_op else None,
            op_name if is_first_of_op else None,
            r_dict.get("tool_number"),
            r_dict.get("tool_name"),
            r_dict.get("characteristic_id") or (str(idx) if is_first_of_op else None),
            r_dict.get("process_characteristic"),
            r_dict.get("product_characteristic"),
            r_dict.get("special_characteristic_class"),
            r_dict.get("specification_tolerance"),
            r_dict.get("control_method"),
            r_dict.get("gage_number"),
            r_dict.get("evaluation_measurement_technique"),
            r_dict.get("sample_size"),
            r_dict.get("sample_frequency"),
            r_dict.get("reaction_plan")
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
    Detects dataset type (CD6 Production vs CNC Benchmark) and applies the authentic template.
    """
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    if not rows:
        print("[Excel Exporter] Warning: No rows to export.")
        return output_path

    abs_output_path = os.path.abspath(output_path)
    sample_item = rows[0]
    sample_dict = sample_item.to_dict() if hasattr(sample_item, "to_dict") else sample_item

    is_control_plan = isinstance(sample_item, ControlPlanRow) or (
        isinstance(sample_dict, dict) and "reaction_plan" in sample_dict and "special_characteristic_class" in sample_dict
    )

    # Detect dataset / template match
    has_cd6_ops = any(
        str(getattr(r, "operation_number", "") if hasattr(r, "operation_number") else r.get("operation_number", ""))
        in ("819", "820", "840", "845", "855", "955")
        for r in rows[:10]
    )
    is_cd6 = "cd6" in abs_output_path.lower() or any(
        "cd6" in str(getattr(r, "production_item_name", "")).lower() or
        "cd6" in str(getattr(r, "operation_name", "")).lower() for r in rows[:10]
    ) or has_cd6_ops

    try:
        if is_control_plan:
            if is_cd6 and os.path.exists(CD6_TEMPLATE):
                print("[Excel Exporter] Applying CD6 Production Benchmark Format (Header + Body + Footer)...")
                _export_cd6_format(rows, abs_output_path)
            else:
                part_name = "Production Item"
                base_file = os.path.basename(abs_output_path).replace("_Control_Plan.xlsx", "").replace("_Control_Plan", "").replace(".xlsx", "").replace("_", " ").strip()
                if isinstance(sample_item, ControlPlanRow) and sample_item.production_item_name and sample_item.production_item_name != "Production Item":
                    part_name = sample_item.production_item_name
                elif isinstance(sample_dict, dict) and sample_dict.get("production_item_name") and sample_dict.get("production_item_name") != "Production Item":
                    part_name = str(sample_dict.get("production_item_name"))
                elif base_file and base_file.lower() not in ("control plan", "output", "test output"):
                    part_name = base_file
                _export_cnc_format(rows, abs_output_path, part_name=part_name)
        else:
            # Multi-capability professional VDA 7-Step & DFMEA format
            wb = openpyxl.Workbook()
            wb.remove(wb.active)

            is_dfmea = "higher_level_element" in sample_dict or "focus_element" in sample_dict
            is_pfmea_vda = "process_step" in sample_dict or "process_item" in sample_dict

            if is_dfmea:
                sheet_title = "DFMEA"
                col_defs = [
                    ("higher_level_element", "Higher Level (System)"),
                    ("focus_element", "Focus Element (Subsystem)"),
                    ("lower_level_element", "Lower Level (Component)"),
                    ("system_function", "System Function"),
                    ("focus_function", "Focus Function / Requirement"),
                    ("design_characteristic", "Design Characteristic"),
                    ("failure_effect_fe", "Failure Effect (FE)"),
                    ("severity_rating", "Severity (S)"),
                    ("failure_mode_fm", "Failure Mode (FM)"),
                    ("special_characteristic_class", "Special Char Class"),
                    ("design_cause_fc", "Design Cause (FC)"),
                    ("current_prevention_control", "Current Prevention Control (PC)"),
                    ("occurrence_rating", "Occurrence (O)"),
                    ("current_detection_control", "Current Detection Control (DC)"),
                    ("detection_rating", "Detection (D)"),
                    ("action_priority_ap", "Action Priority (AP)"),
                    ("recommended_design_action", "Recommended Design Action"),
                    ("responsible_engineer", "Responsible Engineer"),
                    ("target_date", "Target Date"),
                    ("action_status", "Status"),
                ]
                section_defs = [
                    ("Structure Analysis", 1, 3, "FF4472C4", "FFFFFFFF"),
                    ("Functional Analysis", 4, 6, "FFFFC000", "FF000000"),
                    ("Failure Analysis", 7, 11, "FFF4B183", "FF000000"),
                    ("Risk Analysis", 12, 16, "FFFF0000", "FFFFFFFF"),
                    ("Optimization", 17, 20, "FF5B9BD5", "FFFFFFFF"),
                ]
            elif is_pfmea_vda:
                sheet_title = "PFMEA"
                col_defs = [
                    ("process_item", "Process Item (System)"),
                    ("process_step", "Process Step (Operation)"),
                    ("work_element_4m", "Work Element (4M)"),
                    ("process_function", "Process Function"),
                    ("product_characteristic", "Product Characteristic"),
                    ("process_characteristic", "Process Characteristic"),
                    ("failure_effect_fe", "Failure Effect (FE)"),
                    ("severity_rating", "Severity (S)"),
                    ("failure_mode_fm", "Failure Mode (FM)"),
                    ("special_characteristic_class", "Special Char Class"),
                    ("failure_cause_fc", "Failure Cause (FC)"),
                    ("current_prevention_control", "Current Prevention Control (PC)"),
                    ("occurrence_rating", "Occurrence (O)"),
                    ("current_detection_control", "Current Detection Control (DC)"),
                    ("detection_rating", "Detection (D)"),
                    ("action_priority_ap", "Action Priority (AP)"),
                    ("prevention_action", "Prevention Action"),
                    ("detection_action", "Detection Action"),
                    ("responsible_person", "Responsible Person"),
                    ("target_date", "Target Date"),
                    ("status", "Status"),
                ]
                section_defs = [
                    ("Structure Analysis", 1, 3, "FF4472C4", "FFFFFFFF"),
                    ("Functional Analysis", 4, 6, "FFFFC000", "FF000000"),
                    ("Failure Analysis", 7, 11, "FFF4B183", "FF000000"),
                    ("Risk Analysis", 12, 16, "FFFF0000", "FFFFFFFF"),
                    ("Optimization", 17, 21, "FF5B9BD5", "FFFFFFFF"),
                ]
            else:
                sheet_title = "Body"
                col_defs = [(k, k.replace("_", " ").title()) for k in sample_dict.keys()]
                section_defs = []

            ws = wb.create_sheet(title=sheet_title)

            # Soft Blue Header Fill (#ADD8E6) matching industry DFMEA/PFMEA benchmark
            fill_header = PatternFill(start_color="FFADD8E6", end_color="FFADD8E6", fill_type="solid")
            font_header = Font(name="Calibri", size=10, bold=True, color="FF000000")
            thin_border = Border(
                left=Side(style="thin", color="FF808080"),
                right=Side(style="thin", color="FF808080"),
                top=Side(style="thin", color="FF808080"),
                bottom=Side(style="thin", color="FF808080")
            )
            align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
            align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

            if section_defs:
                header_row_idx = 2
                data_start_row = 3
                ws.row_dimensions[1].height = 24
                for s_label, s_start, s_end, s_color, s_font_color in section_defs:
                    if s_start < s_end:
                        ws.merge_cells(start_row=1, start_column=s_start, end_row=1, end_column=s_end)
                    fill_sec = PatternFill(start_color=s_color, end_color=s_color, fill_type="solid")
                    font_sec = Font(name="Calibri", size=10, bold=True, color=s_font_color)
                    for c_idx in range(s_start, s_end + 1):
                        c = ws.cell(row=1, column=c_idx)
                        c.fill = fill_sec
                        c.border = thin_border
                        c.alignment = align_center
                    ws.cell(row=1, column=s_start, value=s_label).font = font_sec
            else:
                header_row_idx = 1
                data_start_row = 2

            ws.row_dimensions[header_row_idx].height = 28
            for col_idx, (_, d_name) in enumerate(col_defs, start=1):
                cell = ws.cell(header_row_idx, col_idx, d_name)
                cell.fill = fill_header
                cell.font = font_header
                cell.alignment = align_center
                cell.border = thin_border
                ws.column_dimensions[get_column_letter(col_idx)].width = max(len(d_name) + 4, 16)

            font_data = Font(name="Calibri", size=9)
            font_bold_red = Font(name="Calibri", size=9, bold=True, color="FF9C0006")
            font_bold_yellow = Font(name="Calibri", size=9, bold=True, color="FF9C6500")
            font_bold_green = Font(name="Calibri", size=9, bold=True, color="FF006100")
            fill_ap_h = PatternFill(start_color="FFFFC7CE", end_color="FFFFC7CE", fill_type="solid")
            fill_ap_m = PatternFill(start_color="FFFFEB9C", end_color="FFFFEB9C", fill_type="solid")
            fill_ap_l = PatternFill(start_color="FFC6EFCE", end_color="FFC6EFCE", fill_type="solid")

            for r_idx, r_item in enumerate(rows, start=data_start_row):
                ws.row_dimensions[r_idx].height = 22
                r_d = r_item.to_dict() if hasattr(r_item, "to_dict") else r_item
                for c_idx, (k, _) in enumerate(col_defs, start=1):
                    val = r_d.get(k)
                    cell = ws.cell(r_idx, c_idx, val)
                    cell.font = font_data
                    cell.border = thin_border
                    
                    # Centered ratings
                    if k in ("severity_rating", "occurrence_rating", "detection_rating", "special_characteristic_class", "action_priority_ap"):
                        cell.alignment = align_center
                    else:
                        cell.alignment = align_left

                    # AP conditional formatting
                    if k == "action_priority_ap":
                        if val == "H":
                            cell.fill = fill_ap_h
                            cell.font = font_bold_red
                        elif val == "M":
                            cell.fill = fill_ap_m
                            cell.font = font_bold_yellow
                        elif val == "L":
                            cell.fill = fill_ap_l
                            cell.font = font_bold_green

            wb.save(abs_output_path)
            wb.close()
    except PermissionError:
        base, ext = os.path.splitext(abs_output_path)
        alt_path = f"{base}_new{ext}"
        print(f"[Excel Exporter Warning] '{abs_output_path}' is open in Excel. Saved to '{alt_path}' instead.")
        abs_output_path = alt_path

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
