#!/usr/bin/env python3
"""
Test script for the standalone DBPF Explorer GUI

This script tests that the DBPF Explorer can be imported and
basic functionality works without errors.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        # Test main GUI import
        import dbpf_explorer
        print("✓ dbpf_explorer module imported")

        # Test DBPF functionality
        from dbpf_interface import DBPFInterface, parse_resource_key, ResourceKey
        print("✓ DBPF interface modules imported")

        from dbpf_unpacker import DBPFUnpacker, DatabasePackedFile
        print("✓ DBPF unpacker modules imported")

        # Test tkinter availability
        import tkinter as tk
        from tkinter import ttk
        print("✓ tkinter available")

        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_basic_functionality():
    """Test basic DBPF functionality."""
    print("\nTesting basic functionality...")

    try:
        from dbpf_interface import ResourceKey, parse_resource_key

        # Test ResourceKey creation
        key = ResourceKey(0x12345678, 0x9ABCDEF0, 0x11111111)
        print(f"✓ ResourceKey created: {key}")

        # Test parsing
        parsed = parse_resource_key("12345678!9ABCDEF0.11111111")
        print(f"✓ Resource key parsed: {parsed}")

        # Test equivalence
        if key.is_equivalent(parsed):
            print("✓ Resource key equivalence works")
        else:
            print("✗ Resource key equivalence failed")
            return False

        return True

    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        return False


def test_gui_classes():
    """Test that GUI classes can be instantiated."""
    print("\nTesting GUI classes...")

    try:
        import dbpf_explorer

        # Test that main classes exist
        if hasattr(dbpf_explorer, 'DBPFExplorer'):
            print("✓ DBPFExplorer class available")
        else:
            print("✗ DBPFExplorer class not found")
            return False

        if hasattr(dbpf_explorer, 'BatchExtractDialog'):
            print("✓ BatchExtractDialog class available")
        else:
            print("✗ BatchExtractDialog class not found")
            return False

        return True

    except Exception as e:
        print(f"✗ GUI class test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("DBPF Explorer Test Suite")
    print("=" * 50)
    print("Testing the standalone DBPF Explorer GUI application")
    print("=" * 50)

    success = True

    if not test_imports():
        success = False

    if not test_basic_functionality():
        success = False

    if not test_gui_classes():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed!")
        print("\nThe DBPF Explorer is ready to use!")
        print("\nTo launch the application:")
        print("  Linux/macOS: python3 dbpf_explorer.py")
        print("  Linux/macOS: ./launch_dbpf_explorer.sh")
        print("  Windows: launch_dbpf_explorer.bat")
        print("  Windows: python dbpf_explorer.py")
        return 0
    else:
        print("✗ Some tests failed!")
        print("\nPlease check the error messages above and ensure all dependencies are installed.")
        return 1


if __name__ == '__main__':
    exit(main())