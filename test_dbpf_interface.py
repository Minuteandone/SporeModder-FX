#!/usr/bin/env python3
"""
Test script for the DBPF Interface

This script demonstrates the basic functionality of the DBPF interface.
Run this to verify that the interface works correctly.
"""

from dbpf_interface import DBPFInterface, ResourceKey, parse_resource_key
import tempfile
import os
from pathlib import Path


def test_basic_functionality():
    """Test basic interface functionality."""
    print("Testing DBPF Interface...")

    # Test ResourceKey parsing
    print("\n1. Testing ResourceKey parsing:")
    try:
        key_str = "12345678!9ABCDEF0.11111111"
        key = parse_resource_key(key_str)
        print(f"✓ Parsed {key_str} -> {key}")
        assert key.group_id == 0x12345678
        assert key.instance_id == 0x9ABCDEF0
        assert key.type_id == 0x11111111
    except Exception as e:
        print(f"✗ ResourceKey parsing failed: {e}")
        return False

    # Test ResourceKey equivalence
    print("\n2. Testing ResourceKey equivalence:")
    try:
        key1 = ResourceKey(0x12345678, 0x9ABCDEF0, 0x11111111)
        key2 = ResourceKey(0x12345678, 0x9ABCDEF0, 0x11111111)
        key3 = ResourceKey(0x87654321, 0x9ABCDEF0, 0x11111111)

        assert key1.is_equivalent(key2)
        assert not key1.is_equivalent(key3)
        print("✓ ResourceKey equivalence works")
    except Exception as e:
        print(f"✗ ResourceKey equivalence failed: {e}")
        return False

    print("\n✓ All basic tests passed!")
    return True


def test_with_real_file():
    """Test with a real DBPF file if available."""
    print("\n3. Testing with real DBPF file:")

    # Look for any .package files in the current directory
    package_files = list(Path(".").glob("*.package"))
    if not package_files:
        print("No .package files found in current directory. Skipping real file test.")
        return True

    dbpf_file = package_files[0]
    print(f"Found DBPF file: {dbpf_file}")

    try:
        interface = DBPFInterface(str(dbpf_file))

        # Test loading
        interface.load()
        print("✓ Successfully loaded DBPF file")
        print(f"  Format: {'DBBF' if interface.dbpf.is_dbbf else 'DBPF'}")
        print(f"  Files: {interface.dbpf.index_count}")

        # Test listing (first 5 files)
        files = interface.list_files(limit=5)
        print(f"✓ Listed {len(files)} files")
        for file_info in files[:3]:  # Show first 3
            print(f"    {file_info}")

        # Test file info for first file
        if interface.dbpf.index.items:
            first_item = interface.dbpf.index.items[0]
            info = interface.get_file_info(first_item.name)
            if info:
                print("✓ Got file information")
                print(f"    Resource: {info['resource_key']}")
                print(f"    Size: {info['uncompressed_size']} bytes")
                print(f"    Compressed: {info['compressed']}")

        return True

    except Exception as e:
        print(f"✗ Real file test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("DBPF Interface Test Suite")
    print("=" * 40)

    success = True

    # Test basic functionality
    if not test_basic_functionality():
        success = False

    # Test with real file if available
    if not test_with_real_file():
        success = False

    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1


if __name__ == '__main__':
    exit(main())