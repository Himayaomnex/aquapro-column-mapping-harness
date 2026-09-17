"""
Data models for the Router-Free Unified Harness.
Implements the schemas defined in schemas/canonical_context.md and capabilities/control_plan_from_pfmea.md.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MappedContextItem(BaseModel):
    """
    Standardized internal data model for one (operation x PFMEA field) observation.
    """
    # Identity (always required)
    operation_number: str
    operation_name: str
    production_item_name: str

    # Hierarchy (CARRY fields for document spine)
    process_segment_name: Optional[str] = None

    # Characteristics (CARRY fields)
    product_characteristic: Optional[str] = None
    process_characteristic: Optional[str] = None

    # PFMEA analysis (AUTHOR source fields)
    failure_mode: Optional[str] = None
    failure_effect: Optional[str] = None
    failure_cause: Optional[str] = None
    severity_rating: Optional[int] = None
    occurrence_rating: Optional[int] = None
    preventive_control: Optional[str] = None
    detective_control: Optional[str] = None
    detection_rating: Optional[int] = None

    # Source traceability
    source_sheet: str = "Sheet1"
    source_row: int = 0
    source_type: str = "file"  # file | rag_data | ai_suggestion | existing_document
    unmapped_fields: List[str] = Field(default_factory=list)


class MappedContext(BaseModel):
    """
    Collection of mapped context items with summary traceability.
    """
    items: List[MappedContextItem] = Field(default_factory=list)
    unmapped_headers: List[str] = Field(default_factory=list)
    raw_row_count: int = 0
    source_operations: List[str] = Field(default_factory=list)


class ControlPlanRow(BaseModel):
    """
    Exact 16-column AIAG 4th Edition Control Plan row.
    Every key must exist on every row (V1).
    Columns 8, 10, 11, 12, 14, 15 are subject to the Invariant of Zero Hallucination (V3).
    """
    # 1. Production Item Name (CARRY)
    production_item_name: str
    # 2. Process Segment Name (CARRY)
    process_segment_name: Optional[str] = None
    # 3. Operation Number (CARRY)
    operation_number: str
    # 4. Operation Name (CARRY)
    operation_name: str
    # 5. Product Characteristic (CARRY)
    product_characteristic: Optional[str] = None
    # 6. Process Characteristic (AUTHOR)
    process_characteristic: Optional[str] = None
    # 7. Special Characteristic Classification (AUTHOR: CC | SC | null)
    special_characteristic_class: Optional[str] = None
    # 8. Specification / Tolerance (ABSTAIN / null on new, preserved on baseline)
    specification_tolerance: Optional[str] = None
    # 9. Evaluation / Measurement Technique (AUTHOR)
    evaluation_measurement_technique: Optional[str] = None
    # 10. Tool Number (ABSTAIN / null on new, preserved on baseline)
    tool_number: Optional[str] = None
    # 11. Tool Name (ABSTAIN / null on new, preserved on baseline)
    tool_name: Optional[str] = None
    # 12. Gage Number (ABSTAIN / null on new, preserved on baseline)
    gage_number: Optional[str] = None
    # 13. Control Method (AUTHOR)
    control_method: Optional[str] = None
    # 14. Sample Size (ABSTAIN / null on new, preserved on baseline)
    sample_size: Optional[str] = None
    # 15. Sample Frequency (ABSTAIN / null on new, preserved on baseline)
    sample_frequency: Optional[str] = None
    # 16. Reaction Plan (AUTHOR)
    reaction_plan: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict with exact 16 AIAG keys."""
        return {
            "production_item_name": self.production_item_name,
            "process_segment_name": self.process_segment_name,
            "operation_number": self.operation_number,
            "operation_name": self.operation_name,
            "product_characteristic": self.product_characteristic,
            "process_characteristic": self.process_characteristic,
            "special_characteristic_class": self.special_characteristic_class,
            "specification_tolerance": self.specification_tolerance,
            "evaluation_measurement_technique": self.evaluation_measurement_technique,
            "tool_number": self.tool_number,
            "tool_name": self.tool_name,
            "gage_number": self.gage_number,
            "control_method": self.control_method,
            "sample_size": self.sample_size,
            "sample_frequency": self.sample_frequency,
            "reaction_plan": self.reaction_plan,
        }


class Violation(BaseModel):
    """
    Specific contract violation reported by the validator.
    """
    rule_id: str  # V1, V2, V3, V4, V5
    on_fail: str  # reject_document | reject_row | warn
    row_identifier: str  # e.g., 'Op 10 - Char 1' or 'Document'
    statement: str
    detail: str


class ExecutionLog(BaseModel):
    """
    Traceability and audit log written alongside Control_Plan.xlsx.
    """
    capability_id: str
    status: str  # COMPLETE | DEGRADED | FAILED
    source_type: str
    source_identifier: str
    total_source_operations: int
    output_rows_count: int
    unmapped_headers: List[str] = Field(default_factory=list)
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    repair_attempts: int = 0
    output_file: Optional[str] = None
