#!/usr/bin/env python3
"""
Example usage of the DBPF Unpacker and Interface

This file demonstrates both the low-level DBPF unpacker API
and the high-level DBPF interface.
"""

from dbpf_unpacker import DBPFUnpacker, ResourceKey, DBPFItem
from dbpf_interface import DBPFInterface, parse_resource_key
import os
import sys

def example_usage():
    """Demonstrate basic usage of the DBPF tools."""

    print("DBPF Tools Examples")
    print("=" * 50)

    # Example 1: Basic unpacking with DBPFUnpacker
    print("\n1. Basic DBPF unpacking with DBPFUnpacker")
    print("   python3 dbpf_unpacker.py path/to/file.package output/directory")
    print()

    # Example 2: Using the high-level interface
    print("2. Using the DBPF Interface (recommended)")
    print("   python3 dbpf_interface.py file.package list")
    print("   python3 dbpf_interface.py file.package extract GROUP!INSTANCE.TYPE output.dat")
    print("   python3 dbpf_interface.py file.package unpack output_dir")
    print("   python3 dbpf_interface.py file.package info GROUP!INSTANCE.TYPE")
    print()

    # Example 3: Programmatic usage
    print("3. Programmatic usage with DBPFInterface")

    # Create a ResourceKey
    key = ResourceKey()
    key.group_id = 0x12345678
    key.instance_id = 0x9ABCDEF0
    key.type_id = 0x11111111

    print(f"Resource Key: {key}")
    print(f"Group ID: 0x{key.group_id:08X}")
    print(f"Instance ID: 0x{key.instance_id:08X}")
    print(f"Type ID: 0x{key.type_id:08X}")
    print()

    # Parse resource key from string
    try:
        parsed_key = parse_resource_key("12345678!9ABCDEF0.11111111")
        print(f"Parsed key: {parsed_key}")
        print(f"Equivalent: {key.is_equivalent(parsed_key)}")
    except Exception as e:
        print(f"Parse error: {e}")
    print()

    print("4. What the unpacker does")
    print("   - Reads DBPF header (magic: DBPF or DBBF)")
    print("   - Reads index containing file metadata")
    print("   - For each file:")
    print("     * Reads compressed/uncompressed data")
    print("     * Decompresses if needed (RefPack)")
    print("     * Saves to output directory structure")
    print()

    print("5. Output structure:")
    print("   output_dir/")
    print("   ├── GROUPID1/")
    print("   │   ├── INSTANCEID1.TYPEID1")
    print("   │   └── INSTANCEID2.TYPEID2")
    print("   └── GROUPID2/")
    print("       └── ...")

    print("\n6. Available tools:")
    print("   - dbpf_unpacker.py: Low-level unpacking")
    print("   - dbpf_interface.py: High-level interface")
    print("   - test_dbpf_interface.py: Test the interface")
    print("   - README_DBPF_INTERFACE.md: Documentation")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Run the test
        from dbpf_unpacker import test_decompression
        test_decompression()
    else:
        example_usage()