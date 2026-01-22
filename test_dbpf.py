#!/usr/bin/env python3
"""
Test script for DBPF explorer functionality
"""

import sys
import os
sys.path.insert(0, '/workspaces/SporeModder-FX')

try:
    from dbpf_interface import DBPFInterface, parse_resource_key, ResourceKey
    from dbpf_unpacker import DBPFUnpacker
    print("✓ DBPF modules imported successfully")

    # Test file type mappings
    from dbpf_explorer import SPORE_FILE_TYPES, get_file_info_from_type
    print(f"✓ File type mappings loaded: {len(SPORE_FILE_TYPES)} types")

    # Test a few file type lookups
    test_types = [0x00B1B104, 0x00E6BCE5, 0x2F4E681C]
    for type_id in test_types:
        ext, cat, desc = get_file_info_from_type(type_id)
        print(f"✓ Type 0x{type_id:08X}: {ext} ({cat}) - {desc}")

    print("\n✓ All basic functionality tests passed!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()