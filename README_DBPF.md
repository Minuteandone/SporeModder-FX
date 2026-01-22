# DBPF Unpacker - Python Implementation

A Python implementation for unpacking Database Packed Files (DBPF) used in Maxis games like Spore.

## Features

- Supports both DBPF (32-bit) and DBBF (64-bit) formats
- Handles RefPack compression decompression
- Extracts all files from DBPF archives
- Command-line interface for easy usage

## Usage

### Command Line

```bash
python3 dbpf_unpacker.py input_file.package output_directory
```

### Python API

```python
from dbpf_unpacker import DBPFUnpacker

# Create unpacker instance
unpacker = DBPFUnpacker('path/to/file.package')

# Unpack to directory
unpacker.unpack('output/directory')
```

## File Structure

The unpacker extracts files into a directory structure based on their resource keys:

```
output_dir/
├── GROUPID1/
│   ├── INSTANCEID1.TYPEID1
│   ├── INSTANCEID2.TYPEID2
│   └── ...
└── GROUPID2/
    └── ...
```

Where:
- `GROUPID` is the hex representation of the group ID (folder name)
- `INSTANCEID` is the hex representation of the instance ID (file name)
- `TYPEID` is the hex representation of the type ID (file extension)

## Technical Details

### DBPF Format Structure

1. **Header**: Contains magic number (DBPF/DBBF), version info, and index metadata
2. **Index**: List of all files with their metadata (offsets, sizes, compression flags)
3. **Data**: Actual file data, compressed or uncompressed

### Compression

Files can be stored uncompressed or compressed using RefPack compression. The unpacker automatically detects and decompresses RefPack-compressed files.

### Resource Keys

Each file is identified by a ResourceKey consisting of:
- **Group ID**: Typically represents the folder/category
- **Instance ID**: Typically represents the filename
- **Type ID**: Typically represents the file extension

## Dependencies

- Python 3.6+
- Standard library only (no external dependencies)

## License

This implementation is based on the Java code from SporeModder-FX and follows the same GPL-3.0 license.