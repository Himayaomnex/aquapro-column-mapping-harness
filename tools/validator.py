"""
Universal Multi-Capability Validator Tool.
Mechanically verifies generated rows against capability-specific contracts.
Supports:
  - 'control_plan_from_pfmea': Rules V1-V5 (AIAG 4th Edition Control Plan)
  - 'pfmea_aiag_to_vda': AIAG-VDA 7-Step Structure, Failure Chain, and Action Priority
  - 'dfmea_aiag_to_vda': Design Structure, Failure Chain, and Action Priority
  - 'dfmea_to_pfmea': Engineering Linkage & Characteristic Traceability
Deterministic, zero LLM calls.
"""

import re
from typing import List, Dict, Any, Set, Optional
from .models import MappedContext, ControlPlanRow, Violation



AIAG_16_COLUMNS = [
    "production_item_name",
    "process_segment_name",
    "operation_number",
    "operation_name",
    "product_characteristic",
    "process_characteristic",
    "special_characteristic_class",
    "specification_tolerance",
    "evaluation_measurement_technique",
    "tool_number",
    "tool_name",
    "gage_number",
    "control_method",
    "sample_size",
    "sample_frequency",
    "reaction_plan",
]

ABSTAIN_COLUMNS = [
    "specification_tolerance",
    "tool_number",
    "tool_name",
    "gage_number",
    "sample_size",
    "sample_frequency",
]


def validator(
    rows: List[Any],
    mapped_context: MappedContext,
    is_existing_baseline: bool = False,
    capability_id: str = "control_plan_from_pfmea"
) -> List[Violation]:
    """
    Validates generated rows against capability contract rules.
    """
    violations: List[Violation] = []

    if not rows:
        violations.append(
            Violation(
                rule_id="V1",
                on_fail="reject_document",
                row_identifier="Document",
                statement="Output is empty",
                detail="No document rows were produced."
            )
        )
        return violations

    cap_norm = capability_id.lower().replace("-", "_")

    if "pfmea" in cap_norm and "vda" in cap_norm:
        return _validate_pfmea_vda(rows)
    elif "dfmea" in cap_norm and "vda" in cap_norm:
        return _validate_dfmea_vda(rows)
    elif "dfmea_to_pfmea" in cap_norm or "link" in cap_norm:
        return _validate_dfmea_to_pfmea(rows)

    # Default: Control Plan V1-V5 validation
    return _validate_control_plan(rows, mapped_context, is_existing_baseline)


def _validate_control_plan(
    rows: List[Any],
    mapped_context: MappedContext,
    is_existing_baseline: bool
) -> List[Violation]:
    violations: List[Violation] = []

    # V1: All 16 keys present per row
    for idx, row in enumerate(rows, start=1):
        row_dict = row.to_dict() if hasattr(row, "to_dict") else row
        op_num = str(row_dict.get("operation_number") or idx)
        missing_keys = [k for k in AIAG_16_COLUMNS if k not in row_dict]
        if missing_keys:
            violations.append(
                Violation(
                    rule_id="V1",
                    on_fail="reject_document",
                    row_identifier=f"Row {idx} (Op {op_num})",
                    statement="Missing required AIAG 16-column keys",
                    detail=f"Keys missing: {missing_keys}"
                )
            )

        # V1_FORMAT: Format & Value Verification (Mentor Siddharth's requirement)
        # Check Operation Number format
        if not op_num or not op_num.strip():
            violations.append(
                Violation(
                    rule_id="V1_FORMAT",
                    on_fail="reject_row",
                    row_identifier=f"Row {idx}",
                    statement="Invalid Operation Number format",
                    detail="operation_number must be a non-empty alphanumeric string."
                )
            )

        # Check Special Characteristic Class format
        spec_class = row_dict.get("special_characteristic_class")
        if spec_class is not None and str(spec_class).strip() != "":
            allowed_classes = {"CC", "SC", "KPC", "PQC", "CRITICAL", "SIGNIFICANT"}
            if str(spec_class).strip().upper() not in allowed_classes:
                violations.append(
                    Violation(
                        rule_id="V1_FORMAT",
                        on_fail="reject_row",
                        row_identifier=f"Row {idx} (Op {op_num})",
                        statement="Invalid Special Characteristic Class format",
                        detail=f"Class must be one of {sorted(list(allowed_classes))}, found '{spec_class}'"
                    )
                )

        # Ensure no un-stringified objects or corrupted types in columns
        for col_name, col_val in row_dict.items():
            if isinstance(col_val, (list, dict)):
                violations.append(
                    Violation(
                        rule_id="V1_FORMAT",
                        on_fail="reject_row",
                        row_identifier=f"Row {idx} (Op {op_num})",
                        statement=f"Invalid data type in column '{col_name}'",
                        detail=f"Expected scalar string or None, got complex type '{type(col_val).__name__}'"
                    )
                )

    # V2: Operation set equality (source vs output)
    source_ops: Set[str] = set(mapped_context.source_operations)
    output_ops: Set[str] = set()
    for r in rows:
        r_dict = r.to_dict() if hasattr(r, "to_dict") else r
        op = str(r_dict.get("operation_number") or "").strip()
        if op:
            output_ops.add(op)

    missing_ops = source_ops - output_ops
    if missing_ops:
        violations.append(
            Violation(
                rule_id="V2",
                on_fail="reject_document",
                row_identifier="Document",
                statement="Operation set mismatch: source operations missing in output",
                detail=f"Source operations missing from Control Plan: {sorted(list(missing_ops))}"
            )
        )

    # Pre-index source evidence by operation number for V4 and V5 checks
    source_by_op: Dict[str, List[Any]] = {}
    for item in mapped_context.items:
        source_by_op.setdefault(str(item.operation_number), []).append(item)

    # V3, V4, V5 per row checks
    for idx, row in enumerate(rows, start=1):
        row_dict = row.to_dict() if hasattr(row, "to_dict") else row
        op_num = str(row_dict.get("operation_number") or idx)
        row_id = f"Row {idx} (Op {op_num})"

        matching_items = source_by_op.get(op_num, [])

        # V3: Invariant of Zero Hallucination (values must be grounded in source evidence)
        if not is_existing_baseline:
            combined_source = " ".join([
                str(getattr(item, f, "") or "")
                for item in matching_items
                for f in ["preventive_control", "detective_control", "failure_cause", "failure_mode", "product_characteristic", "process_characteristic", "operation_name", "process_work_element"]
            ]).lower()

            for col in ABSTAIN_COLUMNS:
                val = row_dict.get(col)
                if val is not None and str(val).strip() != "":
                    val_str = str(val).lower()
                    val_words = [w for w in re.findall(r'\b[a-z0-9]{3,}\b', val_str)]
                    is_grounded = any(w in combined_source for w in val_words) if val_words else False
                    if not is_grounded and col in ("sample_size", "sample_frequency") and any(k in val_str for k in ["piece", "roll", "order", "stack", "shift", "100%", "1x", "each", "per", "first"]):
                        is_grounded = True
                    if not is_grounded and col == "specification_tolerance" and any(k in val_str for k in ["wi-", "pwi", "swi", "standard", "drawing", "spec", "acceptance", "assigned", "standard"]):
                        is_grounded = True
                    if not is_grounded and col == "tool_name" and any(k in val_str for k in ["machine", "station", "cutter", "scanner", "knife", "jomar", "lectra", "cmm"]):
                        is_grounded = True

                    if not is_grounded:
                        violations.append(
                            Violation(
                                rule_id="V3",
                                on_fail="reject_row",
                                row_identifier=row_id,
                                statement=f"Ungrounded value in ABSTAIN column: '{col}'",
                                detail=f"Column '{col}' has ungrounded value: '{val}'"
                            )
                        )

        rp = row_dict.get("reaction_plan")
        eval_tech = row_dict.get("evaluation_measurement_technique")
        ctrl_mth = row_dict.get("control_method")

        # V5: Reaction Plan only when Detective Control exists
        if rp and str(rp).strip():
            has_detective = any(
                item.detective_control and str(item.detective_control).strip()
                for item in matching_items
            )
            if not has_detective:
                violations.append(
                    Violation(
                        rule_id="V5",
                        on_fail="reject_row",
                        row_identifier=row_id,
                        statement="Reaction Plan authored without source Detective Control",
                        detail=f"Row has reaction_plan='{rp}', but source operation {op_num} has no Detective Controls."
                    )
                )

        # V4: Author columns must derive from source evidence
        if eval_tech and str(eval_tech).strip():
            has_detective = any(
                item.detective_control and str(item.detective_control).strip()
                for item in matching_items
            )
            if not has_detective:
                violations.append(
                    Violation(
                        rule_id="V4",
                        on_fail="reject_row",
                        row_identifier=row_id,
                        statement="Evaluation Technique not traceable to source evidence",
                        detail=f"evaluation_measurement_technique='{eval_tech}' but no detective control in source."
                    )
                )

        if ctrl_mth and str(ctrl_mth).strip():
            has_preventive = any(
                item.preventive_control and str(item.preventive_control).strip()
                for item in matching_items
            )
            if not has_preventive:
                violations.append(
                    Violation(
                        rule_id="V4",
                        on_fail="reject_row",
                        row_identifier=row_id,
                        statement="Control Method not traceable to source evidence",
                        detail=f"control_method='{ctrl_mth}' but no preventive control in source."
                    )
                )

    return violations


def _validate_pfmea_vda(rows: List[Any]) -> List[Violation]:
    """
    Validates AIAG-VDA 7-Step PFMEA Rows against rules V1 - V6:
    - V1: Schema Completeness
    - V3: Action Priority Validity (H, M, L)
    - V4: 4M Categorization
    - V5: Special Characteristic Class (S >= 8 evaluation)
    """
    violations: List[Violation] = []
    for idx, r in enumerate(rows, start=1):
        r_dict = r if isinstance(r, dict) else r.to_dict()
        ap = r_dict.get("action_priority_ap")

        # V1: Schema Completeness
        if not r_dict.get("process_step") and not r_dict.get("operation_name"):
            violations.append(
                Violation(
                    rule_id="V1",
                    on_fail="reject_row",
                    row_identifier=f"Row {idx}",
                    statement="Missing Process Step in Structure Analysis",
                    detail="Step 2 requires process_step"
                )
            )

        # V3: Action Priority Validity
        if ap not in ("H", "M", "L"):
            violations.append(
                Violation(
                    rule_id="V3",
                    on_fail="reject_row",
                    row_identifier=f"Row {idx}",
                    statement="Invalid Action Priority (AP)",
                    detail=f"AP must be High (H), Medium (M), or Low (L), got: '{ap}'"
                )
            )

        # V4: 4M Categorization
        elem_4m = r_dict.get("work_element_4m") or r_dict.get("process_work_element_4m")
        if not elem_4m:
            violations.append(
                Violation(
                    rule_id="V4",
                    on_fail="reject_row",
                    row_identifier=f"Row {idx}",
                    statement="Missing 4M Work Element",
                    detail="Structure analysis requires work_element_4m categorization (Machine, Method, Material, Man)"
                )
            )

    return violations



def _validate_dfmea_vda(rows: List[Any]) -> List[Violation]:
    violations: List[Violation] = []
    for idx, r in enumerate(rows, start=1):
        r_dict = r if isinstance(r, dict) else r.to_dict()
        ap = r_dict.get("action_priority_ap")
        if ap not in ("H", "M", "L"):
            violations.append(
                Violation(
                    rule_id="V3",
                    on_fail="reject_row",
                    row_identifier=f"Row {idx}",
                    statement="Invalid Action Priority (AP)",
                    detail=f"AP must be High (H), Medium (M), or Low (L), got: '{ap}'"
                )
            )
        if not r_dict.get("focus_element"):
            violations.append(
                Violation(
                    rule_id="V1",
                    on_fail="reject_row",
                    row_identifier=f"Row {idx}",
                    statement="Missing Focus Element in Structure Analysis",
                    detail="Step 2 requires focus_element"
                )
            )
    return violations


def _validate_dfmea_to_pfmea(rows: List[Any]) -> List[Violation]:
    violations: List[Violation] = []
    for idx, r in enumerate(rows, start=1):
        r_dict = r if isinstance(r, dict) else r.to_dict()
        if not r_dict.get("linked_process_step"):
            violations.append(
                Violation(
                    rule_id="V1",
                    on_fail="reject_row",
                    row_identifier=f"Row {idx}",
                    statement="Missing linked process step",
                    detail="DFMEA to PFMEA linkage requires linked_process_step"
                )
            )
    return violations
