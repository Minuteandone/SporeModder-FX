#!/usr/bin/env python3
"""
Spore DBPF Explorer - Standalone Python GUI

A complete graphical interface for working with DBPF (Database Packed File) files
from Spore and other Maxis games. This is a standalone Python application with
no Java dependencies.

Features:
- Browse and explore DBPF archives
- Extract individual files or entire archives
- View detailed file information
- Batch operations
- Search and filter capabilities
- Modern, user-friendly interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import time

# Import our DBPF functionality
try:
    from dbpf_interface import DBPFInterface, parse_resource_key, ResourceKey
    from dbpf_unpacker import DBPFUnpacker
    DBPF_AVAILABLE = True
except ImportError as e:
    DBPF_AVAILABLE = False
    print(f"Warning: DBPF modules not available: {e}")


# Spore file type mappings
SPORE_FILE_TYPES = {
    # Common Spore file types
    0x2F4E681C: ('png', 'Texture', 'PNG Texture'),
    0x2F7D0004: ('rw4', 'Model', 'RW4 Model'),
    0x2F7D0002: ('prop', 'Property', 'Property File'),
    0x2F4E681B: ('dds', 'DDS Texture', 'DDS Texture'),
    0x2F4E681D: ('png', 'PNG Texture', 'PNG Texture'),
    0x00B1B104: ('tga', 'TGA Texture', 'TGA Texture'),
    0x00B1B105: ('tga', 'TGA Texture', 'TGA Texture'),

    # Audio files
    0x8C0A3F5C: ('ogg', 'Audio', 'OGG Audio'),
    0x8C0A3F5D: ('wav', 'Audio', 'WAV Audio'),

    # Text files
    0x00B1B103: ('txt', 'Text', 'Plain Text'),
    0x00B1B106: ('xml', 'XML', 'XML File'),

    # Animation files
    0x8C0A3F5E: ('animation', 'Animation', 'Animation File'),

    # Effect files
    0x00B1B107: ('eff', 'Effect', 'Effect File'),

    # Other known types
    0x2F4E681E: ('dat', 'Data', 'Data File'),
    0x2F4E681F: ('dat', 'Data', 'Data File'),
    0x2F7D0005: ('dat', 'Data', 'Data File'),
}


def get_file_info_from_type(type_id: int) -> Tuple[str, str, str]:
    """
    Get file extension, category, and description from type ID.

    Args:
        type_id: The file type ID

    Returns:
        Tuple of (extension, category, description)
    """
    if type_id in SPORE_FILE_TYPES:
        return SPORE_FILE_TYPES[type_id]
    else:
        return ('dat', 'Unknown', f'Unknown Type (0x{type_id:08X})')


def generate_readable_filename(resource_key: ResourceKey, type_info: Tuple[str, str, str]) -> str:
    """
    Generate a human-readable filename from resource key and type info.

    Args:
        resource_key: The resource key
        type_info: Tuple of (extension, category, description)

    Returns:
        A readable filename
    """
    extension, category, description = type_info

    # Create a readable name based on the resource key
    group_hex = f"{resource_key.group_id:08X}"
    instance_hex = f"{resource_key.instance_id:08X}"
    type_hex = f"{resource_key.type_id:08X}"

    # Try to make it more readable - use last 4 digits of instance for uniqueness
    short_instance = f"{resource_key.instance_id & 0xFFFF:04X}"

    return f"{category}_{short_instance}_{type_hex}.{extension}"


class DBPFExplorer:
    """Main application class for the DBPF Explorer GUI."""

    def __init__(self, root):
        self.root = root
        self.root.title("Spore DBPF Explorer")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # Current DBPF interface
        self.current_dbpf: Optional[DBPFInterface] = None
        self.current_file_path: Optional[str] = None

        # Create the main interface
        self.setup_ui()

        # Check if DBPF functionality is available
        if not DBPF_AVAILABLE:
            self.show_error("DBPF modules not found. Please ensure dbpf_interface.py and dbpf_unpacker.py are in the same directory.")
            return

        # Set up status bar
        self.setup_status_bar()

    def setup_ui(self):
        """Set up the main user interface."""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create menu bar
        self.setup_menu()

        # Create toolbar
        self.setup_toolbar(main_frame)

        # Create main content area with paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - File tree and operations
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        # Right panel - Details and output
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        # Setup left panel
        self.setup_left_panel(left_frame)

        # Setup right panel
        self.setup_right_panel(right_frame)

    def setup_menu(self):
        """Set up the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open DBPF...", command=self.open_dbpf_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self.refresh_view, accelerator="F5")

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Extract All...", command=self.extract_all_files)
        tools_menu.add_command(label="Batch Extract...", command=self.batch_extract)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_dbpf_file())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<F5>', lambda e: self.refresh_view())

    def setup_toolbar(self, parent):
        """Set up the toolbar."""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))

        # Open button
        ttk.Button(toolbar, text="Open DBPF", command=self.open_dbpf_file).pack(side=tk.LEFT, padx=(0, 5))

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Extract buttons
        ttk.Button(toolbar, text="Extract Selected", command=self.extract_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Extract All", command=self.extract_all_files).pack(side=tk.LEFT, padx=(0, 5))

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Search
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind('<KeyRelease>', self.on_search_change)

        ttk.Button(toolbar, text="Clear", command=self.clear_search).pack(side=tk.LEFT)

    def setup_left_panel(self, parent):
        """Set up the left panel with file tree."""
        # File tree frame
        tree_frame = ttk.LabelFrame(parent, text="DBPF Contents", padding=5)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview with scrollbars
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # Treeview
        columns = ('size', 'compressed', 'type', 'readable_name')
        self.file_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=20)

        # Configure columns
        self.file_tree.heading('#0', text='Resource Key')
        self.file_tree.heading('readable_name', text='Name')
        self.file_tree.heading('size', text='Size')
        self.file_tree.heading('compressed', text='Compressed')
        self.file_tree.heading('type', text='Type')

        self.file_tree.column('#0', width=250, minwidth=200)
        self.file_tree.column('readable_name', width=200, minwidth=150)
        self.file_tree.column('size', width=80, minwidth=60)
        self.file_tree.column('compressed', width=80, minwidth=60)
        self.file_tree.column('type', width=100, minwidth=80)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.file_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack tree and scrollbars
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind events
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
        self.file_tree.bind('<Return>', self.on_file_double_click)

        # Operations frame
        ops_frame = ttk.LabelFrame(parent, text="Operations", padding=5)
        ops_frame.pack(fill=tk.X, pady=(5, 0))

        # Buttons
        btn_frame = ttk.Frame(ops_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="View Info", command=self.view_file_info).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Extract...", command=self.extract_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Extract All...", command=self.extract_all_files).pack(side=tk.LEFT)

    def setup_right_panel(self, parent):
        """Set up the right panel with details and output."""
        # Create notebook for different views
        self.details_notebook = ttk.Notebook(parent)
        self.details_notebook.pack(fill=tk.BOTH, expand=True)

        # File details tab
        details_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(details_frame, text="File Details")

        self.setup_details_tab(details_frame)

        # File preview tab
        preview_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(preview_frame, text="File Preview")

        self.setup_preview_tab(preview_frame)

        # Output tab
        output_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(output_frame, text="Output")

        self.setup_output_tab(output_frame)

    def setup_details_tab(self, parent):
        """Set up the file details tab."""
        # Info display
        info_frame = ttk.LabelFrame(parent, text="Archive Information", padding=5)
        info_frame.pack(fill=tk.X, pady=(0, 5))

        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        info_scroll = ttk.Scrollbar(info_frame, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scroll.set)

        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # File details
        details_frame = ttk.LabelFrame(parent, text="Selected File Details", padding=5)
        details_frame.pack(fill=tk.BOTH, expand=True)

        self.details_text = tk.Text(details_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        details_scroll = ttk.Scrollbar(details_frame, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)

        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_preview_tab(self, parent):
        """Set up the file preview tab."""
        # Preview controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(controls_frame, text="Preview Selected File", command=self.preview_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Clear Preview", command=self.clear_preview).pack(side=tk.LEFT)

        # Preview display
        preview_frame = ttk.LabelFrame(parent, text="File Content Preview", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        self.preview_text = tk.Text(preview_frame, height=20, wrap=tk.NONE, state=tk.DISABLED, font=('Courier', 10))
        preview_scroll_y = ttk.Scrollbar(preview_frame, command=self.preview_text.yview)
        preview_scroll_x = ttk.Scrollbar(preview_frame, command=self.preview_text.xview, orient=tk.HORIZONTAL)

        self.preview_text.configure(yscrollcommand=preview_scroll_y.set, xscrollcommand=preview_scroll_x.set)

        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        preview_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_output_tab(self, parent):
        """Set up the output tab."""
        self.output_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Clear", command=self.clear_output).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Save Log...", command=self.save_log).pack(side=tk.RIGHT)

    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.progress_bar.pack_forget()  # Hide initially

    def open_dbpf_file(self):
        """Open a DBPF file."""
        filename = filedialog.askopenfilename(
            title="Open DBPF File",
            filetypes=[("DBPF files", "*.package"), ("All files", "*.*")]
        )

        if filename:
            self.load_dbpf_file(filename)

    def load_dbpf_file(self, filepath: str):
        """Load a DBPF file."""
        if not DBPF_AVAILABLE:
            self.show_error("DBPF functionality not available.")
            return

        self.status_var.set(f"Loading {os.path.basename(filepath)}...")
        self.progress_var.set(0)
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.root.update()

        def load_task():
            try:
                # Clear existing data
                for item in self.file_tree.get_children():
                    self.file_tree.delete(item)

                # Load DBPF
                self.current_dbpf = DBPFInterface(filepath)
                self.current_file_path = filepath

                # Update info display
                self.update_archive_info()

                # Load file list
                files = self.current_dbpf.list_files()

                # Update progress
                total_files = len(files)
                for i, file_info in enumerate(files):
                    self.progress_var.set((i / total_files) * 100)
                    self.root.update()

                    # Parse file info
                    parts = file_info.split(' | ')
                    if len(parts) >= 3:
                        resource_key_str = parts[0]
                        compressed = parts[1]
                        size_info = parts[2]

                        # Parse resource key to get type info
                        try:
                            resource_key = parse_resource_key(resource_key_str)
                            type_info = get_file_info_from_type(resource_key.type_id)
                            extension, category, description = type_info

                            # Generate readable name
                            readable_name = generate_readable_filename(resource_key, type_info)

                            # Insert into tree with additional info
                            self.file_tree.insert('', 'end', text=resource_key_str,
                                                values=(readable_name, size_info, compressed, description))
                        except Exception:
                            # Fallback for parsing errors
                            self.file_tree.insert('', 'end', text=resource_key_str,
                                                values=('Unknown', size_info, compressed, 'Unknown Type'))

                self.status_var.set(f"Loaded {total_files} files from {os.path.basename(filepath)}")
                self.log_output(f"Successfully loaded DBPF file: {filepath}")
                self.log_output(f"Total files: {total_files}")

            except Exception as e:
                self.show_error(f"Failed to load DBPF file: {str(e)}")
                self.status_var.set("Failed to load file")
            finally:
                self.progress_bar.pack_forget()

        thread = threading.Thread(target=load_task, daemon=True)
        thread.start()

    def update_archive_info(self):
        """Update the archive information display."""
        if not self.current_dbpf:
            return

        try:
            self.current_dbpf.load()
            info = f"""File: {os.path.basename(self.current_file_path)}
Path: {self.current_file_path}
Format: {'DBBF (64-bit)' if self.current_dbpf.dbpf.is_dbbf else 'DBPF (32-bit)'}
Version: {self.current_dbpf.dbpf.major_version}.{self.current_dbpf.dbpf.min_version}
Index Version: {self.current_dbpf.dbpf.index_major_version}.{self.current_dbpf.dbpf.index_minor_version}
Total Files: {self.current_dbpf.dbpf.index_count}
Index Size: {self.current_dbpf.dbpf.index_size} bytes
"""

            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            self.info_text.config(state=tk.DISABLED)

        except Exception as e:
            self.show_error(f"Failed to read archive info: {str(e)}")

    def on_file_double_click(self, event):
        """Handle double-click on file in tree."""
        selection = self.file_tree.selection()
        if not selection:
            return

        self.view_file_info()

    def view_file_info(self):
        """View information about the selected file."""
        selection = self.file_tree.selection()
        if not selection or not self.current_dbpf:
            return

        item = self.file_tree.item(selection[0])
        resource_key_str = item['text']

        try:
            key = parse_resource_key(resource_key_str)
            info = self.current_dbpf.get_file_info(key)

            if info:
                details = f"""Resource Key: {info['resource_key']}
Group ID: {info['group_id']} ({info['group_id']})
Instance ID: {info['instance_id']} ({info['instance_id']})
Type ID: {info['type_id']} ({info['type_id']})
Offset: {info['offset']} (0x{info['offset']:08X})
Compressed Size: {info['compressed_size']} bytes
Uncompressed Size: {info['uncompressed_size']} bytes
Compressed: {info['compressed']}
Saved: {info['saved']}
"""

                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(1.0, details)
                self.details_text.config(state=tk.DISABLED)

                # Switch to details tab
                self.details_notebook.select(0)

                # Also try to show a quick preview if file is small
                try:
                    key = parse_resource_key(resource_key_str)
                    file_info = self.current_dbpf.get_file_info(key)
                    if file_info and file_info['uncompressed_size'] < 10240:  # Less than 10KB
                        # Auto-preview small files
                        self.preview_selected_file()
                except:
                    pass  # Ignore preview errors for auto-preview

            else:
                self.show_error("Could not get file information.")

        except Exception as e:
            self.show_error(f"Failed to get file info: {str(e)}")

    def preview_selected_file(self):
        """Preview the content of the selected file."""
        selection = self.file_tree.selection()
        if not selection or not self.current_dbpf:
            messagebox.showwarning("No Selection", "Please select a file to preview.")
            return

        item = self.file_tree.item(selection[0])
        resource_key_str = item['text']

        self.status_var.set(f"Loading preview for {resource_key_str}...")

        def preview_task():
            try:
                key = parse_resource_key(resource_key_str)

                # Extract file content to memory
                from io import BytesIO
                import tempfile
                import os

                # Create a temporary file to extract to
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = temp_file.name

                try:
                    success = self.current_dbpf.extract_file(key, temp_path)
                    if not success:
                        self.show_error("Failed to extract file for preview.")
                        return

                    # Read the file content
                    with open(temp_path, 'rb') as f:
                        file_data = f.read()

                    # Try to determine if it's text or binary
                    try:
                        # Try to decode as UTF-8
                        text_content = file_data.decode('utf-8', errors='replace')

                        # Check if it looks like binary data (has null bytes or high ratio of non-printable chars)
                        if '\x00' in text_content[:1024] or self._is_binary_data(file_data[:1024]):
                            # Binary file - show hex dump
                            hex_content = self._create_hex_dump(file_data[:2048])  # Limit preview size
                            preview_content = f"Binary file ({len(file_data)} bytes)\n\nHex dump (first 2048 bytes):\n\n{hex_content}"
                        else:
                            # Text file - show content
                            preview_content = f"Text file ({len(file_data)} bytes)\n\nContent:\n\n{text_content[:8192]}"  # Limit preview size

                    except UnicodeDecodeError:
                        # Definitely binary - show hex dump
                        hex_content = self._create_hex_dump(file_data[:2048])
                        preview_content = f"Binary file ({len(file_data)} bytes)\n\nHex dump (first 2048 bytes):\n\n{hex_content}"

                    # Update preview text
                    self.preview_text.config(state=tk.NORMAL)
                    self.preview_text.delete(1.0, tk.END)
                    self.preview_text.insert(1.0, preview_content)
                    self.preview_text.config(state=tk.DISABLED)

                    # Switch to preview tab
                    self.details_notebook.select(1)

                    self.status_var.set(f"Preview loaded for {resource_key_str}")

                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

            except Exception as e:
                self.show_error(f"Failed to preview file: {str(e)}")
                self.status_var.set("Preview failed")

        thread = threading.Thread(target=preview_task, daemon=True)
        thread.start()

    def _is_binary_data(self, data: bytes) -> bool:
        """Check if data appears to be binary."""
        if not data:
            return False

        # Count printable characters
        printable = sum(1 for byte in data if 32 <= byte <= 126 or byte in (9, 10, 13))
        return printable / len(data) < 0.7  # Less than 70% printable = likely binary

    def _create_hex_dump(self, data: bytes, bytes_per_line: int = 16) -> str:
        """Create a hex dump of binary data."""
        lines = []
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i:i + bytes_per_line]

            # Hex part
            hex_part = ' '.join(f'{b:02X}' for b in chunk)

            # ASCII part
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)

            # Pad hex part if necessary
            if len(chunk) < bytes_per_line:
                hex_part += '   ' * (bytes_per_line - len(chunk))

            lines.append(f'{i:08X}: {hex_part} | {ascii_part}')

        return '\n'.join(lines)

    def clear_preview(self):
        """Clear the file preview."""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)

    def extract_selected(self):
        """Extract the selected file."""
        selection = self.file_tree.selection()
        if not selection or not self.current_dbpf:
            messagebox.showwarning("No Selection", "Please select a file to extract.")
            return

        item = self.file_tree.item(selection[0])
        resource_key_str = item['text']
        readable_name = item['values'][0] if item['values'] else "extracted_file"

        # Ask for output location with suggested filename
        output_file = filedialog.asksaveasfilename(
            title="Save Extracted File",
            initialfile=readable_name,
            defaultextension="",
            filetypes=[("All files", "*.*")]
        )

        if not output_file:
            return

        self.status_var.set(f"Extracting {resource_key_str}...")
        self.progress_var.set(0)
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X)

        def extract_task():
            try:
                key = parse_resource_key(resource_key_str)
                success = self.current_dbpf.extract_file(key, output_file)

                if success:
                    self.status_var.set(f"Extracted {resource_key_str}")
                    self.log_output(f"✓ Successfully extracted {resource_key_str} to {output_file}")
                    messagebox.showinfo("Success", f"File extracted successfully!\nSaved to: {output_file}")
                else:
                    self.status_var.set("Extraction failed")
                    self.log_output(f"✗ Failed to extract {resource_key_str}")
                    messagebox.showerror("Error", "Failed to extract file.")

            except Exception as e:
                self.status_var.set("Extraction failed")
                self.log_output(f"✗ Extraction error: {str(e)}")
                self.show_error(f"Extraction failed: {str(e)}")
            finally:
                self.progress_bar.pack_forget()

        thread = threading.Thread(target=extract_task, daemon=True)
        thread.start()

    def extract_all_files(self):
        """Extract all files from the current DBPF."""
        if not self.current_dbpf:
            messagebox.showwarning("No File", "Please open a DBPF file first.")
            return

        # Ask for output directory
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return

        self.status_var.set("Extracting all files...")
        self.progress_var.set(0)
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.log_output(f"Starting extraction of all files to: {output_dir}")

        def extract_task():
            try:
                start_time = time.time()
                unpacker = DBPFUnpacker(self.current_file_path)
                unpacker.unpack(output_dir)

                # Count extracted files
                extracted = 0
                for root, dirs, files in os.walk(output_dir):
                    extracted += len(files)

                elapsed = time.time() - start_time
                self.status_var.set(f"Extracted {extracted} files")
                self.log_output(f"✓ Successfully extracted {extracted} files in {elapsed:.2f} seconds")
                messagebox.showinfo("Success", f"All files extracted successfully!\n{extracted} files saved to: {output_dir}")

            except Exception as e:
                self.status_var.set("Extraction failed")
                self.log_output(f"✗ Extraction error: {str(e)}")
                self.show_error(f"Extraction failed: {str(e)}")
            finally:
                self.progress_bar.pack_forget()

        thread = threading.Thread(target=extract_task, daemon=True)
        thread.start()

    def batch_extract(self):
        """Batch extract multiple files."""
        if not self.current_dbpf:
            messagebox.showwarning("No File", "Please open a DBPF file first.")
            return

        # Create batch extraction dialog
        dialog = BatchExtractDialog(self.root, self.current_dbpf, self)
        self.root.wait_window(dialog)

    def on_search_change(self, event):
        """Handle search input changes."""
        search_term = self.search_var.get().lower()
        self.filter_files(search_term)

    def filter_files(self, search_term: str):
        """Filter files based on search term."""
        # Clear current display
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        if not self.current_dbpf:
            return

        try:
            files = self.current_dbpf.list_files()

            for file_info in files:
                parts = file_info.split(' | ')
                if len(parts) >= 3:
                    resource_key_str = parts[0]
                    compressed = parts[1]
                    size_info = parts[2]

                    # Parse to get additional info
                    try:
                        key = parse_resource_key(resource_key_str)
                        type_info = get_file_info_from_type(key.type_id)
                        readable_name = generate_readable_filename(key, type_info)
                        extension, category, description = type_info
                    except:
                        readable_name = "Unknown"
                        description = "Unknown Type"

                    # Check if matches search (in resource key, readable name, or type)
                    searchable_text = f"{resource_key_str} {readable_name} {description}".lower()
                    if search_term in searchable_text:
                        self.file_tree.insert('', 'end', text=resource_key_str,
                                            values=(readable_name, size_info, compressed, description))

        except Exception as e:
            self.log_output(f"Search error: {str(e)}")

    def clear_search(self):
        """Clear the search filter."""
        self.search_var.set("")
        self.refresh_view()

    def refresh_view(self):
        """Refresh the current view."""
        if self.current_file_path:
            self.load_dbpf_file(self.current_file_path)

    def clear_output(self):
        """Clear the output log."""
        self.output_text.delete(1.0, tk.END)

    def save_log(self):
        """Save the output log to a file."""
        log_content = self.output_text.get(1.0, tk.END).strip()
        if not log_content:
            messagebox.showinfo("No Content", "No log content to save.")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(log_content)
                messagebox.showinfo("Success", f"Log saved to: {filename}")
            except Exception as e:
                self.show_error(f"Failed to save log: {str(e)}")

    def log_output(self, message: str):
        """Log a message to the output tab."""
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)

    def show_about(self):
        """Show about dialog."""
        about_text = """Spore DBPF Explorer

A standalone Python GUI for working with DBPF files from Spore and other Maxis games.

Features:
• Browse and explore DBPF archives
• Extract individual files or entire archives
• View detailed file information
• Search and filter capabilities
• Batch operations

Built with Python and tkinter.
No Java dependencies required.

Version: 1.0
"""
        messagebox.showinfo("About", about_text)

    def show_error(self, message: str):
        """Show an error message."""
        messagebox.showerror("Error", message)
        self.log_output(f"ERROR: {message}")


class BatchExtractDialog(tk.Toplevel):
    """Dialog for batch extraction operations."""

    def __init__(self, parent, dbpf_interface, main_app):
        super().__init__(parent)
        self.dbpf = dbpf_interface
        self.main_app = main_app

        self.title("Batch Extract")
        self.geometry("500x400")
        self.resizable(True, True)

        self.setup_ui()

    def setup_ui(self):
        """Set up the batch extract dialog UI."""
        # Instructions
        ttk.Label(self, text="Select files to extract:").pack(pady=5)

        # File list with checkboxes
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create scrollable frame for checkboxes
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Get all files and create checkboxes
        self.check_vars = {}
        try:
            files = self.dbpf.list_files()
            for file_info in files[:50]:  # Limit to first 50 for performance
                parts = file_info.split(' | ')
                if len(parts) >= 1:
                    resource_key_str = parts[0]

                    # Parse to get readable name
                    try:
                        key = parse_resource_key(resource_key_str)
                        type_info = get_file_info_from_type(key.type_id)
                        readable_name = generate_readable_filename(key, type_info)
                        display_name = f"{readable_name} ({resource_key_str})"
                    except:
                        display_name = resource_key_str

                    var = tk.BooleanVar()
                    self.check_vars[resource_key_str] = var
                    ttk.Checkbutton(scrollable_frame, text=display_name, variable=var).pack(anchor=tk.W)
        except Exception as e:
            ttk.Label(scrollable_frame, text=f"Error loading files: {str(e)}").pack()

        # Output directory selection
        output_frame = ttk.Frame(self)
        output_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W)
        self.output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).grid(row=0, column=2, padx=(5, 0))

        output_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Select None", command=self.select_none).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Extract", command=self.do_batch_extract).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def browse_output(self):
        """Browse for output directory."""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_var.set(dirname)

    def select_all(self):
        """Select all files."""
        for var in self.check_vars.values():
            var.set(True)

    def select_none(self):
        """Deselect all files."""
        for var in self.check_vars.values():
            var.set(False)

    def do_batch_extract(self):
        """Perform batch extraction."""
        output_dir = self.output_var.get().strip()
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return

        # Get selected files
        selected_files = [key for key, var in self.check_vars.items() if var.get()]

        if not selected_files:
            messagebox.showwarning("No Selection", "Please select at least one file to extract.")
            return

        self.destroy()  # Close dialog

        # Start batch extraction
        self.main_app.status_var.set(f"Batch extracting {len(selected_files)} files...")
        self.main_app.log_output(f"Starting batch extraction of {len(selected_files)} files to: {output_dir}")

        def batch_task():
            try:
                success_count = 0
                for i, resource_key_str in enumerate(selected_files):
                    try:
                        key = parse_resource_key(resource_key_str)
                        # Get type info and generate readable filename
                        type_info = get_file_info_from_type(key.type_id)
                        readable_name = generate_readable_filename(key, type_info)

                        # Create output filename with proper extension
                        output_file = os.path.join(output_dir, readable_name)
                        success = self.dbpf.extract_file(key, output_file)
                        if success:
                            success_count += 1
                            self.main_app.log_output(f"✓ Extracted {readable_name}")
                        else:
                            self.main_app.log_output(f"✗ Failed {resource_key_str}")
                    except Exception as e:
                        self.main_app.log_output(f"✗ Error extracting {resource_key_str}: {str(e)}")

                    # Update progress
                    progress = (i + 1) / len(selected_files) * 100
                    self.main_app.progress_var.set(progress)
                    self.main_app.root.update()

                self.main_app.status_var.set(f"Batch extraction complete: {success_count}/{len(selected_files)} files")
                self.main_app.log_output(f"Batch extraction complete: {success_count} successful, {len(selected_files) - success_count} failed")
                messagebox.showinfo("Batch Complete", f"Extracted {success_count} of {len(selected_files)} files.")

            except Exception as e:
                self.main_app.show_error(f"Batch extraction failed: {str(e)}")
            finally:
                self.main_app.progress_bar.pack_forget()

        thread = threading.Thread(target=batch_task, daemon=True)
        thread.start()


def main():
    """Main entry point."""
    root = tk.Tk()

    # Set a modern theme if available
    try:
        style = ttk.Style()
        # Try to use a modern theme
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
    except:
        pass  # Use default theme

    app = DBPFExplorer(root)
    root.mainloop()


if __name__ == '__main__':
    main()
