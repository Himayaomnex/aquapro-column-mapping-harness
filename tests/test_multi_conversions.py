"""
Unit & Integration Tests for Multi-Conversion Architecture.
Tests:
- Action Priority (AP) calculation
- PFMEA to AIAG-VDA 7-Step conversion
- DFMEA to AIAG-VDA 7-Step conversion
- DFMEA to PFMEA linkage
- End-to-end multi-conversion execution through UnifiedHarness
"""

import os
import unittest
from tools import (
    workbook_parser,
    column_mapper,
    excel_builder,
    excel_exporter,
    MappedContext,
    MappedContextItem
)
from tools.excel_builder import calculate_action_priority
from harness import UnifiedHarness


class TestMultiConversions(unittest.TestCase):

    def setUp(self):
        self.sample_items = [
            MappedContextItem(
                production_item_name="CD6 Front Axle Knuckle",
                process_segment_name="Machining",
                operation_number="10",
                operation_name="CNC Bore Milling",
                product_characteristic="Bore Diameter",
                process_characteristic="Spindle RPM & Feed",
                failure_mode="Bore oversized",
                failure_effect="Loose bearing fit causing vibration",
                failure_cause="Tool insert worn",
                severity_rating=9,
                occurrence_rating=6,
                detection_rating=5,
                preventive_control="Tool life counter alarm",
                detective_control="Air gage 100% check",
                source_sheet="Sheet1",
                source_row=2
            ),
            MappedContextItem(
                production_item_name="CD6 Front Axle Knuckle",
                process_segment_name="Machining",
                operation_number="20",
                operation_name="Induction Hardening",
                product_characteristic="Case Depth",
                process_characteristic="Coil Frequency",
                failure_mode="Insufficient depth",
                failure_effect="Premature fatigue failure",
                failure_cause="Power drop during cycle",
                severity_rating=8,
                occurrence_rating=3,
                detection_rating=2,
                preventive_control="Power regulator monitor",
                detective_control="Destructive cut check 1/shift",
                source_sheet="Sheet1",
                source_row=3
            ),
            MappedContextItem(
                production_item_name="CD6 Front Axle Knuckle",
                process_segment_name="Machining",
                operation_number="30",
                operation_name="Deburring",
                product_characteristic="Edge Chamfer",
                process_characteristic="Brush Pressure",
                failure_mode="Burrs remaining",
                failure_effect="Minor assembly interference",
                failure_cause="Brush bristles worn",
                severity_rating=4,
                occurrence_rating=3,
                detection_rating=3,
                preventive_control="Daily brush inspection",
                detective_control="Visual inspection",
                source_sheet="Sheet1",
                source_row=4
            )
        ]
        self.context = MappedContext(
            items=self.sample_items,
            source_operations=["10", "20", "30"]
        )

    def test_01_action_priority_calculation(self):
        # S=9, O=6, D=5 -> High (Safety critical + moderate occurrence)
        self.assertEqual(calculate_action_priority(9, 6, 5), "H")
        # S=8, O=3, D=2 -> Low (Good detection and low occurrence)
        self.assertEqual(calculate_action_priority(8, 3, 2), "L")
        # S=4, O=3, D=3 -> Low (Low severity)
        self.assertEqual(calculate_action_priority(4, 3, 3), "L")
        # S=8, O=8, D=8 -> High
        self.assertEqual(calculate_action_priority(8, 8, 8), "H")

    def test_02_pfmea_aiag_to_vda_builder(self):
        rows = excel_builder(
            mapped_context=self.context,
            document_type="pfmea_aiag_to_vda"
        )
        self.assertEqual(len(rows), 3)
        # Check Step 2 Structure
        self.assertIn("process_item_system", rows[0])
        self.assertIn("process_step", rows[0])
        self.assertIn("process_work_element_4m", rows[0])
        # Check Step 5 Risk & Action Priority
        self.assertEqual(rows[0]["action_priority_ap"], "H")
        self.assertEqual(rows[0]["special_characteristic"], "CC")
        self.assertEqual(rows[1]["special_characteristic"], "SC")

    def test_03_dfmea_aiag_to_vda_builder(self):
        rows = excel_builder(
            mapped_context=self.context,
            document_type="dfmea_aiag_to_vda"
        )
        self.assertEqual(len(rows), 3)
        # Check Focus Element and Failure Mode
        self.assertEqual(rows[0]["focus_element"], "CD6 Front Axle Knuckle")
        self.assertIn("design_prevention_control", rows[0])
        self.assertIn("action_priority_ap", rows[0])

    def test_04_dfmea_to_pfmea_builder(self):
        rows = excel_builder(
            mapped_context=self.context,
            document_type="dfmea_to_pfmea"
        )
        self.assertEqual(len(rows), 3)
        # Verify engineering linkage fields
        self.assertIn("source_dfmea_item", rows[0])
        self.assertIn("linked_process_step", rows[0])
        self.assertIn("linked_process_failure_mode", rows[0])
        self.assertIn("recommended_process_control", rows[0])
        # Severity >= 8 triggers error-proofing recommendation
        self.assertIn("Poka-Yoke", rows[0]["recommended_process_control"])

    def test_05_export_multi_conversions_to_excel(self):
        vda_rows = excel_builder(self.context, document_type="pfmea_aiag_to_vda")
        out_path = "tests/data/test_PFMEA_AIAG_VDA.xlsx"
        exported_file = excel_exporter(vda_rows, out_path, document_title="AIAG-VDA 1st Edition — PFMEA")
        self.assertTrue(os.path.exists(exported_file))
        self.assertGreater(os.path.getsize(exported_file), 1000)

    def test_06_e2e_pfmea_aiag_to_vda_harness_run(self):
        data_file = "data/CNC_Operation_Process_FMEA.xlsx"
        if not os.path.exists(data_file):
            self.skipTest("Source data file not found")
        harness = UnifiedHarness()
        final_state = harness.run(
            task="Convert PFMEA to AIAG-VDA format",
            file_path=data_file,
            capability="pfmea_aiag_to_vda"
        )
        self.assertIsNotNone(final_state)
        self.assertEqual(final_state.get("capability_id"), "pfmea_aiag_to_vda")
        self.assertGreater(len(final_state.get("built_rows", [])), 0)
        out_file = final_state.get("exported_file_path")
        self.assertTrue(out_file and os.path.exists(out_file))

    def test_07_e2e_dfmea_to_pfmea_harness_run(self):
        data_file = "data/CNC_Operation_Process_FMEA.xlsx"
        if not os.path.exists(data_file):
            self.skipTest("Source data file not found")
        harness = UnifiedHarness()
        final_state = harness.run(
            task="Generate PFMEA linkage from DFMEA",
            file_path=data_file,
            capability="dfmea_to_pfmea"
        )
        self.assertIsNotNone(final_state)
        self.assertEqual(final_state.get("capability_id"), "dfmea_to_pfmea")
        self.assertGreater(len(final_state.get("built_rows", [])), 0)
        out_file = final_state.get("exported_file_path")
        self.assertTrue(out_file and os.path.exists(out_file))


if __name__ == "__main__":
    unittest.main()

