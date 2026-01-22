#!/usr/bin/env python3
"""
Script to parse reg_type.txt and generate updated SPORE_FILE_TYPES dictionary
"""

import re

def parse_reg_type_file():
    """Parse reg_type.txt and return a dictionary of type mappings"""
    types = {}

    with open('/workspaces/SporeModder-FX/reg_type.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Split by tab
            parts = line.split('\t')
            if len(parts) >= 2:
                name = parts[0].strip()
                hash_str = parts[1].strip()

                # Convert hex string to int
                try:
                    if hash_str.startswith('0x'):
                        type_id = int(hash_str, 16)
                    else:
                        type_id = int(hash_str, 16)  # Assume hex even without 0x
                except ValueError:
                    continue

                # Determine extension and category
                extension, category = get_extension_and_category(name)

                # Create description
                description = f"{name.replace('_', ' ').title()}"

                types[type_id] = (extension, category, description)

    return types

def get_extension_and_category(name):
    """Determine file extension and category from the name"""
    name_lower = name.lower()

    # Direct extension matches
    if '.' in name:
        # Handle cases like "png.dds", "bak.png"
        parts = name.split('.')
        if len(parts) >= 2:
            ext = parts[-1]
            base_name = '.'.join(parts[:-1])
            return ext, categorize(base_name)
    elif name_lower in ['png', 'jpg', 'jpeg', 'bmp', 'tga', 'gif', 'ico', 'dds']:
        return name_lower, 'Texture'
    elif name_lower in ['wav', 'ogg', 'mp3']:
        return name_lower, 'Audio'
    elif name_lower in ['txt', 'xml', 'html', 'json', 'ini', 'cfg', 'lua', 'js', 'py', 'log', 'bak']:
        return name_lower, 'Text/Document'
    elif name_lower in ['prop', 'properties']:
        return 'prop', 'Property'
    elif name_lower in ['animation', 'anim']:
        return 'animation', 'Animation'
    elif name_lower in ['rw4', 'gmdl', 'bmdl']:
        return name_lower, 'Model'
    elif name_lower in ['eff', 'pfx', 'effect']:
        return 'eff', 'Effect'
    elif name_lower in ['cnv', 'conversion']:
        return 'cnv', 'Conversion'
    elif name_lower in ['lvl', 'level']:
        return 'lvl', 'Level'
    elif name_lower in ['creaturedata', 'creature_data']:
        return 'creaturedata', 'Creature Data'
    elif name_lower in ['advect', 'adv']:
        return 'adv', 'Advection'
    elif name_lower in ['pctp', 'particle']:
        return 'pctp', 'Particle'
    elif name_lower in ['locale', 'localization']:
        return 'locale', 'Localization'
    elif name_lower in ['ttf', 'font']:
        return 'ttf', 'Font'
    elif name_lower in ['hkx', 'animation']:
        return 'hkx', 'Animation'
    elif name_lower in ['bin', 'binary']:
        return 'bin', 'Binary'
    elif name_lower in ['dat', 'data']:
        return 'dat', 'Data'
    elif name_lower in ['db', 'database']:
        return 'db', 'Database'
    elif name_lower in ['blend', 'blender']:
        return 'blend', 'Blender'
    elif name_lower in ['xls', 'excel']:
        return 'xls', 'Spreadsheet'
    elif name_lower in ['avi', 'video']:
        return 'avi', 'Video'
    elif name_lower in ['bnk', 'bank']:
        return 'bnk', 'Sound Bank'
    elif name_lower in ['er2', 'audio']:
        return 'er2', 'Audio'
    elif name_lower in ['mrk', 'marker']:
        return 'mrk', 'Marker'
    elif name_lower in ['arg', 'script']:
        return 'arg', 'Script'
    elif name_lower in ['blockinfo', 'block']:
        return 'blockinfo', 'Block Info'
    elif name_lower.endswith('.bin'):
        return 'bin', 'Binary Data'
    else:
        # Try to infer from name patterns
        if 'texture' in name_lower or 'tex' in name_lower:
            return 'dds', 'Texture'
        elif 'model' in name_lower or 'mesh' in name_lower:
            return 'rw4', 'Model'
        elif 'sound' in name_lower or 'audio' in name_lower:
            return 'wav', 'Audio'
        elif 'effect' in name_lower:
            return 'eff', 'Effect'
        elif 'creature' in name_lower:
            return 'creaturedata', 'Creature'
        elif 'building' in name_lower or 'structure' in name_lower:
            return 'bld', 'Building'
        elif 'vehicle' in name_lower:
            return 'vcl', 'Vehicle'
        elif 'plant' in name_lower or 'flora' in name_lower:
            return 'plt', 'Plant'
        elif 'city' in name_lower:
            return 'bld', 'City'
        elif 'mission' in name_lower or 'quest' in name_lower:
            return 'dat', 'Mission'
        elif 'tribe' in name_lower:
            return 'dat', 'Tribe'
        elif 'space' in name_lower:
            return 'dat', 'Space'
        elif 'cell' in name_lower:
            return 'cell', 'Cell'
        elif 'adventure' in name_lower:
            return 'dat', 'Adventure'
        else:
            return 'dat', 'Data'

def categorize(name):
    """Categorize based on name patterns"""
    name_lower = name.lower()

    if any(x in name_lower for x in ['texture', 'tex', 'png', 'dds', 'tga', 'jpg', 'bmp']):
        return 'Texture'
    elif any(x in name_lower for x in ['model', 'mesh', 'rw4', 'gmdl']):
        return 'Model'
    elif any(x in name_lower for x in ['sound', 'audio', 'wav', 'ogg', 'bnk']):
        return 'Audio'
    elif any(x in name_lower for x in ['anim', 'animation', 'hkx']):
        return 'Animation'
    elif any(x in name_lower for x in ['effect', 'eff', 'pfx']):
        return 'Effect'
    elif any(x in name_lower for x in ['prop', 'property', 'properties']):
        return 'Property'
    elif any(x in name_lower for x in ['creature', 'animal', 'being']):
        return 'Creature'
    elif any(x in name_lower for x in ['building', 'structure', 'city', 'house']):
        return 'Building'
    elif any(x in name_lower for x in ['vehicle', 'car', 'ship']):
        return 'Vehicle'
    elif any(x in name_lower for x in ['plant', 'flora', 'tree']):
        return 'Plant'
    elif any(x in name_lower for x in ['mission', 'quest', 'adventure']):
        return 'Mission'
    elif any(x in name_lower for x in ['tribe', 'civilization']):
        return 'Tribe'
    elif any(x in name_lower for x in ['space', 'planet', 'star', 'solar']):
        return 'Space'
    elif any(x in name_lower for x in ['cell', 'stage']):
        return 'Cell'
    elif any(x in name_lower for x in ['level', 'lvl']):
        return 'Level'
    elif any(x in name_lower for x in ['ui', 'interface', 'menu']):
        return 'UI'
    elif any(x in name_lower for x in ['script', 'code']):
        return 'Script'
    elif any(x in name_lower for x in ['data', 'dat', 'bin']):
        return 'Data'
    elif any(x in name_lower for x in ['text', 'txt', 'xml', 'json']):
        return 'Text'
    else:
        return 'Other'

def generate_python_dict(types):
    """Generate the Python dictionary code"""
    lines = []
    lines.append("# Spore file type mappings - Generated from reg_type.txt")
    lines.append("SPORE_FILE_TYPES = {")

    # Sort by type_id for consistency
    sorted_types = sorted(types.items())

    for type_id, (ext, cat, desc) in sorted_types:
        lines.append(f"    0x{type_id:08X}: ('{ext}', '{cat}', '{desc}'),")

    lines.append("}")
    return '\n'.join(lines)

if __name__ == '__main__':
    types = parse_reg_type_file()
    print(f"Parsed {len(types)} file types")
    dict_code = generate_python_dict(types)
    
    # Write to file
    with open('/workspaces/SporeModder-FX/spore_types_dict.py', 'w') as f:
        f.write(dict_code)
    
    print("Dictionary written to spore_types_dict.py")