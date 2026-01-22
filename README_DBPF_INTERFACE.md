# DBPF Interface

A simple command-line interface for working with DBPF (Database Packed File) files used in Maxis games like Spore.

## Features

- **List files**: View all files contained in a DBPF archive
- **Extract specific files**: Extract individual files by their resource key
- **Extract all files**: Unpack entire archives to a directory
- **File information**: Get detailed information about specific files
- **Graphical User Interface**: Enhanced GUI with multiple tabs for different operations

## Usage

```bash
python3 dbpf_interface.py <dbpf_file> <command> [options]
```

### Commands

#### List Files
```bash
# List all files in the archive
python3 dbpf_interface.py file.package list

# List first 10 files
python3 dbpf_interface.py file.package list --limit 10
```

#### Extract Specific File
```bash
# Extract a file by its resource key
python3 dbpf_interface.py file.package extract GROUP!INSTANCE.TYPE output.dat
```

Resource keys are in hexadecimal format: `GROUPID!INSTANCEID.TYPEID`

#### Extract All Files
```bash
# Extract all files to a directory
python3 dbpf_interface.py file.package unpack output_directory

# With verbose output
python3 dbpf_interface.py file.package unpack output_directory --verbose
```

#### Get File Information
```bash
# Get detailed information about a specific file
python3 dbpf_interface.py file.package info GROUP!INSTANCE.TYPE
```

### Graphical User Interface

Launch the GUI with enhanced DBPF tools:

```bash
python3 sporemodder_fx_gui.py
```

The GUI provides three tabs for DBPF operations:

#### Unpack All Tab
- Extract entire DBPF archives to directories
- Progress reporting and status updates

#### Explore Tab
- Load and browse files within DBPF archives
- View file list with compression and size information
- Double-click files to see detailed information
- Get archive metadata (format, version, file count)

#### Extract Single Tab
- Extract individual files by resource key
- Browse for output locations
- Real-time status updates

## Examples

```bash
# List contents of a Spore package file
python3 dbpf_interface.py Data.package list --limit 20

# Extract a specific texture file
python3 dbpf_interface.py Data.package extract 12345678!9ABCDEF0.2F4E681C texture.png

# Unpack an entire mod package
python3 dbpf_interface.py mod.package unpack extracted_mod/

# Get info about a creature definition
python3 dbpf_interface.py Data.package info 12345678!9ABCDEF0.2F4E681C
```

## API Usage

You can also use the `DBPFInterface` class directly in your Python code:

```python
from dbpf_interface import DBPFInterface, ResourceKey

# Create interface
dbpf = DBPFInterface("file.package")

# List files
files = dbpf.list_files(limit=10)
for file_info in files:
    print(file_info)

# Extract a specific file
key = ResourceKey(0x12345678, 0x9ABCDEF0, 0x11111111)
dbpf.extract_file(key, "output.dat")

# Get file information
info = dbpf.get_file_info(key)
if info:
    print(f"Size: {info['uncompressed_size']} bytes")
    print(f"Compressed: {info['compressed']}")
```

## Dependencies

- Python 3.6+
- tkinter (usually included with Python)
- The `dbpf_unpacker.py` module (included in this project)

## File Format Support

- DBPF (32-bit offsets)
- DBBF (64-bit offsets)
- RefPack compression/decompression</content>
<parameter name="filePath">/workspaces/SporeModder-FX/README_DBPF_INTERFACE.md