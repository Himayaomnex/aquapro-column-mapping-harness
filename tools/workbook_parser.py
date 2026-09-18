"""
Workbook Parser Tool (Production Grade).
Extracts raw tabular data from real production PFMEA workbooks using openpyxl.
Handles multi-sheet workbooks (e.g. Header vs Body), forward-fills merged operation cells,
and preserves row traceability.
Deterministic, zero LLM calls.
"""

from typing import List, Dict, Any, Optional, Tuple
import os
import openpyxl


KEYWORD_WEIGHTS = {
    "operation number": 5,
    "operation description": 5,
    "potential failure mode": 5,
    "potential causes of failure": 4,
    "potential effects of failure": 4,
    "current process controls": 4,
    "preventive controls": 4,
    "detective controls": 4,
    "severity": 3,
    "occurrence": 3,
    "detection": 3,
    "characteristic": 3,
    "process function": 3,
    "product": 2,
    "process": 2,
}


def score_row_as_header(row_values: List[str]) -> int:
    """Scores a row based on PFMEA header keyword occurrences."""
    score = 0
    row_str = " | ".join(row_values).lower()
    for kw, weight in KEYWORD_WEIGHTS.items():
        if kw in row_str:
            score += weight
    return score


def find_best_sheet_and_header(wb: openpyxl.Workbook) -> Tuple[Optional[str], int]:
    """
    Finds the sheet that contains the actual PFMEA table (e.g. 'Body' or 'PFMEA')
    and locates its header row.
    """
    best_sheet_name = None
    best_header_row = 1
    highest_score = 0

    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        if sheet.max_row < 2:
            continue

        for r_idx in range(1, min(15, sheet.max_row + 1)):
            row_vals = [str(sheet.cell(r_idx, c).value or "").strip().lower() for c in range(1, min(50, sheet.max_column + 1))]
            score = score_row_as_header(row_vals)
            if score > highest_score:
                highest_score = score
                best_sheet_name = sheet_name
                best_header_row = r_idx

    # If no score found, fallback to active or first non-empty sheet
    if not best_sheet_name:
        best_sheet_name = wb.active.title if wb.active else wb.sheetnames[0]
        best_header_row = 1

    return best_sheet_name, best_header_row


def workbook_parser(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads a production PFMEA .xlsx file, identifies the primary PFMEA table,
    normalizes merged/hierarchical operation rows with forward filling,
    and returns raw rows as dicts.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Workbook not found at {file_path}")

    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet_name, header_row_idx = find_best_sheet_and_header(wb)
    sheet = wb[sheet_name]

    # Extract headers
    headers: List[str] = []
    op_col_indices: List[int] = []
    desc_col_indices: List[int] = []
    seg_col_indices: List[int] = []

    for col_idx in range(1, sheet.max_column + 1):
        val = sheet.cell(row=header_row_idx, column=col_idx).value
        h_str = str(val).strip() if val is not None else f"Column_{col_idx}"
        headers.append(h_str)

        h_lower = h_str.lower()
        if any(k in h_lower for k in ["operation number", "op number", "op no", "op #", "operation #"]):
            op_col_indices.append(col_idx - 1)
        elif any(k in h_lower for k in ["operation description", "operation name"]):
            desc_col_indices.append(col_idx - 1)
        elif any(k in h_lower for k in ["process function", "process segment"]):
            seg_col_indices.append(col_idx - 1)

    raw_rows: List[Dict[str, Any]] = []
    
    # State for forward-filling merged operation rows
    last_op_val = None
    last_desc_val = None
    last_seg_val = None

    for row_idx in range(header_row_idx + 1, sheet.max_row + 1):
        row_vals: List[Any] = [sheet.cell(row=row_idx, column=c).value for c in range(1, len(headers) + 1)]
        
        # Check if entire row is empty
        if not any(v is not None and str(v).strip() != "" for v in row_vals):
            continue

        # Check operation number for forward fill
        curr_op = None
        for op_i in op_col_indices:
            if op_i < len(row_vals) and row_vals[op_i] is not None and str(row_vals[op_i]).strip() != "":
                curr_op = str(row_vals[op_i]).strip()
                break

        curr_desc = None
        for desc_i in desc_col_indices:
            if desc_i < len(row_vals) and row_vals[desc_i] is not None and str(row_vals[desc_i]).strip() != "":
                curr_desc = str(row_vals[desc_i]).strip()
                break

        curr_seg = None
        for seg_i in seg_col_indices:
            if seg_i < len(row_vals) and row_vals[seg_i] is not None and str(row_vals[seg_i]).strip() != "":
                curr_seg = str(row_vals[seg_i]).strip()
                break

        # Update forward fill memory
        if curr_op:
            last_op_val = curr_op
            last_desc_val = curr_desc or last_desc_val
            last_seg_val = curr_seg or last_seg_val
        else:
            # Forward-fill if operation is missing on sub-row
            if last_op_val:
                for op_i in op_col_indices:
                    if op_i < len(row_vals) and (row_vals[op_i] is None or str(row_vals[op_i]).strip() == ""):
                        row_vals[op_i] = last_op_val
                if last_desc_val:
                    for desc_i in desc_col_indices:
                        if desc_i < len(row_vals) and (row_vals[desc_i] is None or str(row_vals[desc_i]).strip() == ""):
                            row_vals[desc_i] = last_desc_val
                if last_seg_val:
                    for seg_i in seg_col_indices:
                        if seg_i < len(row_vals) and (row_vals[seg_i] is None or str(row_vals[seg_i]).strip() == ""):
                            row_vals[seg_i] = last_seg_val

        # Construct row dict
        row_dict: Dict[str, Any] = {}
        has_content = False
        for h, val in zip(headers, row_vals):
            if val is not None and str(val).strip() != "":
                has_content = True
                row_dict[h] = val
            else:
                row_dict[h] = None

        if has_content:
            row_dict["_source_sheet"] = sheet_name
            row_dict["_source_row"] = row_idx
            raw_rows.append(row_dict)

    wb.close()
    return raw_rows
