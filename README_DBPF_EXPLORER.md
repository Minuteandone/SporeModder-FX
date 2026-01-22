# Spore DBPF Explorer

A complete standalone Python GUI application for working with DBPF (Database Packed File) files from Spore and other Maxis games. **No Java dependencies required** - this is a pure Python application.

![DBPF Explorer](https://via.placeholder.com/800x400/4CAF50/white?text=DBPF+Explorer+Screenshot)

## Features

### 🗂️ **Archive Exploration**
- Browse DBPF file contents with a tree view
- View detailed archive information (format, version, file count)
- Search and filter files by resource key
- Sortable columns for file size, compression status, and type

### 📁 **File Operations**
- Extract individual files with a double-click
- Batch extract multiple selected files
- Extract entire archives to directories
- **Human-readable filenames** with proper extensions (.png, .wav, .prop, etc.)
- **Automatic file type detection** based on Spore type IDs
- Progress bars and status updates

### ℹ️ **File Information**
- Detailed metadata for each file (offsets, sizes, compression)
- Resource key parsing and display
- **File content preview** with automatic text/binary detection
- **Hex dump viewer** for binary files
- File type identification and categorization
- Human-readable filenames with proper extensions

### 🔍 **Search & Filter**
- Real-time search through file lists
- Filter by resource key components
- Quick access to specific file types

### 📊 **Progress & Logging**
- Progress bars for long operations
- Comprehensive operation logging
- Status updates and error reporting

## Installation

### Requirements
- Python 3.6+
- tkinter (usually included with Python)
- The DBPF modules (`dbpf_unpacker.py` and `dbpf_interface.py`)

### Quick Start
```bash
# Clone or download the repository
cd /path/to/sporemodder-fx

# Run the application
python3 dbpf_explorer.py
```

### Desktop Integration (Linux)
Create a desktop entry for easy launching:

```bash
# Create desktop entry
sudo cp dbpf-explorer.desktop /usr/share/applications/
```

## Usage

### Opening Files
1. Click "Open DBPF" or use Ctrl+O
2. Select a `.package` file from Spore or compatible games
3. The application will load and display all files in the archive

### Exploring Contents
- **File Tree**: Shows all files with resource keys and human-readable names
- **Archive Info**: Displays format, version, and statistics
- **File Details**: Click any file to see detailed information
- **File Preview**: View file contents directly in the interface (text/hex dump)
- **Search**: Use the search box to filter by name, type, or resource key

### Extracting Files
- **Single File**: Double-click a file or use "Extract Selected" (saves with proper filename)
- **Multiple Files**: Use "Batch Extract" for multiple selections (with readable names)
- **All Files**: Use "Extract All" to unpack the entire archive
- **Smart Naming**: Files are automatically saved with human-readable names and correct extensions

### File Preview
- **Text Files**: View content directly in the interface
- **Binary Files**: See hex dump with ASCII representation
- **Auto-Detection**: Automatically determines if file is text or binary
- **Size Limited**: Previews first 8KB of text files, 2KB hex dump of binary files

### Resource Keys
Files are identified by resource keys in the format:
```
GROUP!INSTANCE.TYPE
```

For example: `12345678!9ABCDEF0.11111111`

## Interface Overview

### Main Window
- **Toolbar**: Quick access to common operations
- **File Tree**: Browse archive contents
- **Details Panel**: File information and archive metadata
- **Output Log**: Operation logs and status messages
- **Status Bar**: Current operation status and progress

### Menu Options
- **File**: Open DBPF files, exit application
- **View**: Refresh current view
- **Tools**: Batch operations and utilities
- **Help**: About dialog and documentation

## Supported Formats

- **DBPF**: 32-bit offsets (Spore main format)
- **DBBF**: 64-bit offsets (for larger archives)
- **RefPack Compression**: Automatic decompression
- **All Spore file types**: Textures, models, audio, etc.

## Keyboard Shortcuts

- `Ctrl+O`: Open DBPF file
- `Ctrl+Q`: Exit application
- `F5`: Refresh view
- `Enter`: View selected file details

## Command Line Usage

You can also use the underlying command-line interface:

```bash
# List files in an archive
python3 dbpf_interface.py file.package list

# Extract a specific file
python3 dbpf_interface.py file.package extract 12345678!9ABCDEF0.11111111 output.dat

# Extract all files
python3 dbpf_interface.py file.package unpack output_directory
```

## Troubleshooting

### Common Issues

**"DBPF modules not found"**
- Ensure `dbpf_interface.py` and `dbpf_unpacker.py` are in the same directory
- Check Python path and imports

**"tkinter not available"**
- Install tkinter: `sudo apt-get install python3-tk` (Ubuntu/Debian)
- Or: `brew install python-tk` (macOS with Homebrew)

**"Permission denied"**
- Ensure write permissions for output directories
- Check file permissions on DBPF files

### Performance Tips

- Large archives (>1000 files) may take time to load
- Use search/filter to quickly find specific files
- Batch operations are more efficient than individual extractions
- Close the application when not in use to free memory

## Development

### Architecture
- **Pure Python**: No Java dependencies
- **Threaded Operations**: Non-blocking UI during file operations
- **Modular Design**: Separate interface and core functionality
- **Cross-platform**: Works on Windows, macOS, and Linux

### Extending the Application
The application is designed to be extensible:

```python
# Add new file operations
def custom_operation(self):
    # Your code here
    pass

# Add new menu items
file_menu.add_command(label="Custom Operation", command=self.custom_operation)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of SporeModder-FX and follows the same licensing terms.

## Credits

- **DBPF Implementation**: Based on the Java SporeModder-FX project
- **Python Port**: Pure Python implementation with no Java dependencies
- **GUI Framework**: Built with tkinter for cross-platform compatibility

## Version History

- **v1.0**: Initial release with full DBPF exploration capabilities
- Complete archive browsing and file extraction
- Batch operations and search functionality
- Cross-platform GUI with modern interface

---

For more information about Spore modding, visit the [Spore Modding Community](https://spore.modding.wiki).</content>
<parameter name="filePath">/workspaces/SporeModder-FX/README_DBPF_EXPLORER.md