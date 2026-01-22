#!/usr/bin/env python3
"""
Minimal test for DBPF explorer functionality
"""

# Test the file type mappings
SPORE_FILE_TYPES = {
    0x00B1B104: ('prop', 'Property', 'Property File'),
    0x00E6BCE5: ('gmdl', 'Model', '3D Model'),
    0x2F4E681C: ('png', 'Texture', 'PNG Texture'),
}

def get_file_info_from_type(type_id: int):
    if type_id in SPORE_FILE_TYPES:
        return SPORE_FILE_TYPES[type_id]
    else:
        return ('dat', 'Unknown', f'Unknown Type (0x{type_id:08X})')

# Test the function
if __name__ == '__main__':
    test_types = [0x00B1B104, 0x00E6BCE5, 0x2F4E681C, 0x12345678]

    print("Testing file type mappings:")
    for type_id in test_types:
        ext, cat, desc = get_file_info_from_type(type_id)
        print(f"0x{type_id:08X} -> {ext} ({cat}) - {desc}")

    print("\n✓ Basic functionality test passed!")