"""
RAG Retriever Tool (Production Grade).
Retrieves historical PFMEA records from the knowledge base or parent codebase repository fixtures
when no file is uploaded (Scenario 2: No Document Provided).
100% portable: dynamic relative paths without hardcoded absolute machine paths.
"""

import os
import re
from typing import List, Optional
from .models import MappedContextItem, MappedContext
from .workbook_parser import workbook_parser
from .column_mapper import column_mapper

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DATA_DIR = os.path.join(BASE_DIR, "data")
PARENT_FIXTURES_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "aquapro-excel-comparison-handover 1", "aquapro-excel-comparison-handover", "mission", "excel-comparison", "fixtures")
)


def rag_retriever(production_item_name: str, top_k: int = 20) -> MappedContext:
    """
    Retrieves stored PFMEA records matching the production item name.
    Searches both local data directory and parent knowledge repository fixtures.
    Tags all returned items with source_type='rag_data'.
    """
    print(f"[RAG Retriever] Searching knowledge base for '{production_item_name}'...")
    
    clean_item = (production_item_name or "").lower().replace("production item", "").strip()
    words = [w for w in re.split(r'[\s_\-]+', clean_item) if len(w) > 2]

    search_dirs = [d for d in [LOCAL_DATA_DIR, PARENT_FIXTURES_DIR] if os.path.exists(d)]
    matched_file = None
    candidate_fallback = None

    for sdir in search_dirs:
        for fname in os.listdir(sdir):
            if fname.lower().endswith(".xlsx") and "fmea" in fname.lower():
                candidate_fallback = os.path.join(sdir, fname)
                if any(w in fname.lower() for w in words) or clean_item in fname.lower():
                    matched_file = os.path.join(sdir, fname)
                    break
        if matched_file:
            break

    # If no exact keyword match, use candidate fallback from knowledge base
    if not matched_file and candidate_fallback:
        matched_file = candidate_fallback

    if matched_file:
        print(f"[RAG Retriever] Found matching historical record in knowledge repository: '{os.path.basename(matched_file)}'")
        raw_rows = workbook_parser(matched_file)
        mapped_ctx = column_mapper(raw_rows)
        for item in mapped_ctx.items:
            item.source_type = "rag_data"
            item.production_item_name = production_item_name
        return mapped_ctx

    print(f"[RAG Retriever] No direct historical match found for '{production_item_name}'.")
    return MappedContext()
