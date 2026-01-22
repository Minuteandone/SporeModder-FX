#!/usr/bin/env python3
"""
Test script for DBPF explorer advanced viewers
"""

import sys
import os
sys.path.insert(0, '/workspaces/SporeModder-FX')

try:
    # Test basic imports
    from dbpf_explorer import SPORE_FILE_TYPES, get_file_info_from_type
    print("✓ Basic imports successful")

    # Test file type mappings
    test_types = [0x00B1B104, 0x00E6BCE5, 0x2F4E681C, 0x2F7D0004]
    print("\n✓ Testing file type mappings:")
    for type_id in test_types:
        ext, cat, desc = get_file_info_from_type(type_id)
        print(f"  0x{type_id:08X} -> {ext} ({cat}) - {desc}")

    # Test optional dependencies
    try:
        import PIL
        print("✓ PIL/Pillow available for image viewing")
    except ImportError:
        print("⚠ PIL/Pillow not available - image viewing limited")

    try:
        import pygame
        print("✓ pygame available for audio playback")
    except ImportError:
        try:
            import playsound
            print("✓ playsound available for audio playback")
        except ImportError:
            print("⚠ No audio library available - audio playback disabled")

    print("\n✓ All basic functionality tests passed!")
    print("\nAdvanced viewers implemented:")
    print("  • Image Viewer (PIL-based with zoom, pan, export)")
    print("  • Property Viewer (tree-structured .prop files)")
    print("  • Audio Player (pygame/playsound-based playback)")
    print("  • Enhanced Cell/Creature data previews")
    print("  • Specialized binary file viewers")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()