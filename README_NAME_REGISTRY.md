## Name Extraction System - Using Registry Files

The Python DBPF Explorer now implements the same name extraction system as the Java SporeModder-FX implementation.

### How It Works

Instead of using hardcoded type mappings, the system uses registry files to look up actual names:

#### Registry Files

1. **reg_file.txt** - Maps file/instance hash IDs to their actual names (e.g., "sporemaster", "names")
2. **reg_type.txt** - Maps type hash IDs to their extensions (e.g., "prop", "gmdl", "png")
3. **reg_property.txt** - Maps property IDs to their property names (e.g., "description", "parent")

These files are automatically loaded when the application starts.

#### Name Lookup Process

When displaying a resource key like `0xABCD1234!0x56789012.0x00B1B104`:

1. **Instance Name** (`0x56789012`):
   - Look up in `reg_file.txt` registry
   - If found: return actual name (e.g., "names")
   - If not found: return hex format (e.g., "0x56789012")

2. **Type Name** (`0x00B1B104`):
   - Look up in `reg_type.txt` registry
   - If found: return extension (e.g., "prop")
   - If not found: return hex format (e.g., "0x00B1B104")

3. **Result**: Display as "names.prop" instead of "0x56789012.0x00B1B104"

#### Property Names

Property IDs in `.prop` files are also looked up in the registry:

1. Look up property ID in `reg_property.txt`
2. If found: display actual property name (e.g., "description")
3. If not found: display hex ID (e.g., "0x2F8B3BF4")

### Implementation Details

**Module: `name_registry.py`**

- `NameRegistry`: Manages individual registries (file, type, property)
- `HashManager`: Central hash manager that handles all lookups and calculations
- `get_hash_manager()`: Gets the global HashManager instance

**Key Methods:**

- `get_file_name(hash)` - Get file/instance name from hash
- `get_type_name(hash)` - Get type/extension name from hash
- `get_property_name(hash)` - Get property name from hash
- `fnv_hash(text)` - Calculate FNV-1a hash for a string

**Integration with DBPF Explorer:**

1. The `DBPFExplorer` class initializes `HashManager` in `__init__()`:
   ```python
   self.hash_manager = get_hash_manager(os.path.dirname(os.path.abspath(__file__)))
   ```

2. The `generate_readable_filename()` function uses the registry:
   ```python
   instance_name = get_file_name(resource_key.instance_id)
   type_name = get_type_name(resource_key.type_id)
   return f"{instance_name}.{type_name}"
   ```

3. Property viewer uses registry for property names:
   ```python
   prop_name = get_property_name(prop_id)
   ```

### Benefits

1. **Accurate Names**: Uses actual names from the game files, not hardcoded mappings
2. **Extensible**: New names can be added to registry files without code changes
3. **Matches Java Implementation**: Uses the same registry file format and lookup process
4. **User-Friendly**: Displays readable names instead of hex IDs when available

### Examples

**File Registry Entries (reg_file.txt):**
```
tribepopups~	0x182CD6CE
civpopups~	0xAA9A8ED7
eventTemplates~	0x2333F729
buttons_city_buildings~	0xDCC387F5
```

**Type Registry Entries (reg_type.txt):**
```
prop	0x00B1B104
gmdl	0x00E6BCE5
plt	0x011989B7
png	0x2F4E681C
```

**Property Registry Entries (reg_property.txt):**
```
description	0x00B2CCCA
parent	0x00B2CCCB
```

### Loading Status

On startup, the application loads:
- 1,559+ file entries from reg_file.txt
- 445+ type entries from reg_type.txt
- 4,900+ property entries from reg_property.txt

Run `test_name_registry.py` to verify registry loading:
```bash
python3 test_name_registry.py
```
