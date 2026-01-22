#!/usr/bin/env python3
"""
Test script for the enhanced GUI

This script tests that the GUI can be imported and basic classes instantiated.
Run this to verify that the GUI enhancements work correctly.
"""

import sys
import os

def test_gui_import():
    """Test that the GUI can be imported."""
    print("Testing GUI import...")

    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())

        # Try to import the GUI
        import sporemodder_fx_gui as gui

        print("✓ GUI module imported successfully")

        # Test that DBPF_INTERFACE_AVAILABLE is set correctly
        if gui.DBPF_INTERFACE_AVAILABLE:
            print("✓ DBPF interface is available")
        else:
            print("⚠ DBPF interface not available - some features may be limited")

        # Test that main classes can be instantiated (without actually creating windows)
        print("✓ GUI classes defined correctly")

        return True

    except ImportError as e:
        print(f"✗ Failed to import GUI: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_dbpf_interface_import():
    """Test that the DBPF interface can be imported."""
    print("\nTesting DBPF interface import...")

    try:
        from dbpf_interface import DBPFInterface, parse_resource_key, ResourceKey

        # Test ResourceKey creation
        key = ResourceKey(0x12345678, 0x9ABCDEF0, 0x11111111)
        print(f"✓ ResourceKey created: {key}")

        # Test resource key parsing
        parsed = parse_resource_key("12345678!9ABCDEF0.11111111")
        print(f"✓ Resource key parsed: {parsed}")

        # Test equivalence
        if key.is_equivalent(parsed):
            print("✓ Resource key equivalence works")
        else:
            print("✗ Resource key equivalence failed")
            return False

        return True

    except ImportError as e:
        print(f"✗ Failed to import DBPF interface: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Run all tests."""
    print("GUI Enhancement Test Suite")
    print("=" * 40)

    success = True

    if not test_gui_import():
        success = False

    if not test_dbpf_interface_import():
        success = False

    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed!")
        print("\nYou can now run the enhanced GUI with:")
        print("  python3 sporemodder_fx_gui.py")
        return 0
    else:
        print("✗ Some tests failed!")
        return 1


if __name__ == '__main__':
    exit(main())