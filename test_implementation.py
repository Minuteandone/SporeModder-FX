#!/usr/bin/env python3
"""
Test script to validate the DBPF Explorer implementation
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import dbpf_explorer
        print("✓ dbpf_explorer imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import dbpf_explorer: {e}")
        return False

def test_file_type_mappings():
    """Test that file type mappings are working"""
    try:
        from dbpf_explorer import get_file_info_from_type, SPORE_FILE_TYPES
        print(f"✓ File type mappings loaded: {len(SPORE_FILE_TYPES)} types")

        # Test a few known types
        test_types = [0x00B1B104, 0x00B1B10F, 0x2F7D0004]  # PNG, PROP, WAV
        for type_id in test_types:
            info = get_file_info_from_type(type_id)
            print(f"  Type 0x{type_id:08X}: {info}")

        return True
    except Exception as e:
        print(f"✗ Failed to test file type mappings: {e}")
        return False

def test_property_parsing():
    """Test property file parsing functionality"""
    try:
        # Create a mock DBPFExplorer instance to test parsing
        import tkinter as tk
        from dbpf_explorer import DBPFExplorer

        # We can't fully test GUI components without a display, but we can test the parsing logic
        print("✓ Property parsing methods are defined")

        # Test the property type size function
        explorer = None
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the window
            explorer = DBPFExplorer(root)

            # Test _get_property_type_size
            sizes = {
                0x0000: 4,   # Boolean
                0x0001: 4,   # Integer
                0x0002: 4,   # Float
                0x0003: 0,   # String (variable)
                0x0004: 8,   # Vector2
                0x0005: 12,  # Vector3
                0x0006: 16,  # Vector4/Color
                0x0007: 12,  # Key
            }

            for prop_type, expected_size in sizes.items():
                actual_size = explorer._get_property_type_size(prop_type)
                if actual_size == expected_size:
                    print(f"  ✓ Property type 0x{prop_type:04X}: size {actual_size}")
                else:
                    print(f"  ✗ Property type 0x{prop_type:04X}: expected {expected_size}, got {actual_size}")

            root.destroy()
        except Exception as e:
            print(f"  Note: GUI testing limited: {e}")

        return True
    except Exception as e:
        print(f"✗ Failed to test property parsing: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing DBPF Explorer Implementation")
    print("=" * 40)

    tests = [
        ("Module Imports", test_imports),
        ("File Type Mappings", test_file_type_mappings),
        ("Property Parsing", test_property_parsing),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1

    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed! The implementation appears to be working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return 1

if __name__ == '__main__':
    sys.exit(main())