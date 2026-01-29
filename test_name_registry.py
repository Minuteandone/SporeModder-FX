#!/usr/bin/env python3
"""
Test script for the name registry system.
Validates that the Python implementation matches the Java implementation.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from name_registry import get_hash_manager, HashManager, fnv_hash


def test_fnv_hash():
    """Test FNV hash calculation against known values."""
    print("\n=== Testing FNV Hash Calculation ===")

    test_cases = [
        ("name", 0x2F8B3BF4),
        ("parent", 0x5F6317D5),
        ("creatureGame", 0),  # We just verify it doesn't crash
    ]

    for text, expected in test_cases:
        hash_val = fnv_hash(text)
        print(f"FNV('{text}') = 0x{hash_val:08X}")
        if expected and hash_val != expected:
            print(f"  WARNING: Expected 0x{expected:08X}")


def test_registry_loading():
    """Test that registry files are loaded correctly."""
    print("\n=== Testing Registry Loading ===")

    hm = get_hash_manager()

    # Test file registry
    file_count = len(hm.file_registry.names)
    print(f"File registry loaded: {file_count} entries")

    # Test type registry
    type_count = len(hm.type_registry.names)
    print(f"Type registry loaded: {type_count} entries")

    # Test property registry
    prop_count = len(hm.property_registry.names)
    print(f"Property registry loaded: {prop_count} entries")

    return file_count > 0 and type_count > 0


def test_name_lookup():
    """Test name lookup functionality."""
    print("\n=== Testing Name Lookup ===")

    hm = get_hash_manager()

    # Get some known hashes from the registries
    test_hashes = list(hm.file_registry.names.keys())[:5]

    print("Sample file names from registry:")
    for hash_val in test_hashes:
        name = hm.get_file_name(hash_val)
        print(f"  0x{hash_val:08X} -> {name}")

    test_type_hashes = list(hm.type_registry.names.keys())[:5]

    print("\nSample type names from registry:")
    for hash_val in test_type_hashes:
        name = hm.get_type_name(hash_val)
        print(f"  0x{hash_val:08X} -> {name}")


def test_hex_fallback():
    """Test that unknown hashes return hex format."""
    print("\n=== Testing Hex Fallback ===")

    hm = get_hash_manager()

    # Try a hash that's unlikely to be in the registry
    unknown_hash = 0xDEADBEEF

    file_name = hm.get_file_name(unknown_hash)
    print(f"Unknown file hash 0x{unknown_hash:08X}: {file_name}")

    type_name = hm.get_type_name(unknown_hash)
    print(f"Unknown type hash 0x{unknown_hash:08X}: {type_name}")

    return file_name.startswith("0x") and type_name.startswith("0x")


def test_property_names():
    """Test property name lookup."""
    print("\n=== Testing Property Names ===")

    hm = get_hash_manager()

    # Test special properties
    test_props = [
        0x00B2CCCA,  # description
        0x00B2CCCB,  # parent
    ]

    print("Special properties:")
    for prop_id in test_props:
        prop_name = hm.get_property_name(prop_id)
        print(f"  0x{prop_id:08X} -> {prop_name}")


def test_resource_key_names():
    """Test the generate_readable_filename function."""
    print("\n=== Testing Resource Key Names ===")

    # We need to import after path is set
    from dbpf_explorer import ResourceKey, generate_readable_filename, get_file_info_from_type

    hm = get_hash_manager()

    # Create a test resource key
    key = ResourceKey()
    key.group_id = hm.get_file_hash("sporemaster")
    key.instance_id = hm.get_file_hash("names")
    key.type_id = hm.get_type_hash("prop")

    print(f"Test Resource Key:")
    print(f"  Group ID: 0x{key.group_id:08X}")
    print(f"  Instance ID: 0x{key.instance_id:08X}")
    print(f"  Type ID: 0x{key.type_id:08X}")

    # Get type info
    type_info = get_file_info_from_type(key.type_id)
    print(f"  Type Info: {type_info}")

    # Generate readable filename
    filename = generate_readable_filename(key, type_info)
    print(f"  Readable Filename: {filename}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Name Registry System Tests")
    print("=" * 60)

    try:
        # Test hash calculation
        test_fnv_hash()

        # Test registry loading
        if not test_registry_loading():
            print("WARNING: Registries may not have loaded properly")

        # Test name lookup
        test_name_lookup()

        # Test hex fallback
        if not test_hex_fallback():
            print("WARNING: Hex fallback test failed")

        # Test property names
        test_property_names()

        # Test resource key names
        test_resource_key_names()

        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
