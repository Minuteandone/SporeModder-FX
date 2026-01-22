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


# Spore file type mappings - Based on reg_type.txt from Java implementation
SPORE_FILE_TYPES = {
    # Core Spore file types
    0x00B1B104: ('prop', 'Property', 'Property File'),
    0x00E6BCE5: ('gmdl', 'Model', '3D Model'),
    0x011989B7: ('plt', 'Plant', 'Plant Data'),
    0x2F4E681C: ('png', 'Texture', 'PNG Texture'),
    0x2F4E681B: ('rw4', 'Model', 'RW4 Model'),
    0x2F7D0002: ('jpeg', 'Texture', 'JPEG Texture'),
    0x2F7D0004: ('png', 'Texture', 'PNG Texture'),
    0x2F7D0005: ('bmp', 'Texture', 'BMP Texture'),
    0x2F7D0006: ('tga', 'Texture', 'TGA Texture'),
    0x2F7D0007: ('gif', 'Texture', 'GIF Texture'),
    0x17952E6C: ('dds', 'Texture', 'DDS Texture'),
    0x276CA4B9: ('ttf', 'Font', 'TrueType Font'),
    0x27C5CEF: ('ttf', 'Font', 'TrueType Font'),
    0x2FAC0B6: ('locale', 'Localization', 'Locale Data'),
    0x4AEB6BC6: ('tlsa', 'Animation', 'Animation Data'),
    0x7C19AA7A: ('pctp', 'Particle', 'Particle System'),
    0xCF6C21B8: ('xml', 'Text', 'XML File'),
    0xEFBDA3FF: ('layout', 'UI', 'UI Layout'),
    0x12952634: ('dat', 'Data', 'Data File'),
    0x250FE9A2: ('spui', 'UI', 'Spore UI'),
    0x2B6CAB5F: ('txt', 'Text', 'Text File'),
    0x37979F71: ('cfg', 'Config', 'Configuration'),
    0x617715C4: ('py', 'Script', 'Python Script'),
    0xDFAD9F51: ('cell', 'Cell', 'Cell Stage'),
    0xEE17C6AD: ('animation', 'Animation', 'Animation'),
    0x55ADA24: ('cnv', 'Conversion', 'Conversion Data'),
    0xF43029A: ('creaturedata', 'Creature', 'Creature Data'),
    0x47B8300: ('lvl', 'Level', 'Level Data'),
    0x4805684: ('adv', 'Advection', 'Advection Data'),

    # Audio files
    0x2B9F662: ('prop', 'Audio Property', 'Audio Property'),
    0x42C9CBB: ('snd', 'Audio', 'Sound File'),
    0x2C9EFF2: ('submix', 'Audio', 'Audio Submix'),
    0x29E333B: ('voice', 'Audio', 'Voice Audio'),

    # Effect files
    0x497767B9: ('pfx', 'Effect', 'Particle Effect'),
    0x433FB70C: ('effectmap', 'Effect', 'Effect Map'),
    0xEA5118B0: ('effdir', 'Effect', 'Effect Directory'),

    # Model files
    0x1C135DA: ('gmsh', 'Model', 'Game Mesh'),
    0x72047DE2: ('bmdl', 'Model', 'Building Model'),

    # Animation files
    0x3F9C28B5: ('ani', 'Animation', 'Animation File'),
    0x448AE7E2: ('hkx', 'Animation', 'Havok Animation'),

    # UI files
    0x250FE9A2: ('spui', 'UI', 'Spore UI'),
    0xEFBDA3FF: ('layout', 'UI', 'UI Layout'),

    # Script/Config files
    0x248F226: ('css', 'Style', 'CSS Stylesheet'),
    0x65266B7: ('xhtml', 'Text', 'XHTML File'),
    0xDD6233D6: ('html', 'Text', 'HTML File'),
    0x1E639C34: ('xml', 'Text', 'XML File'),
    0x3681D755: ('lua', 'Script', 'Lua Script'),
    0x67771F5C: ('js', 'Script', 'JavaScript'),

    # Data files
    0x1AD2416: ('creature_traits', 'Data', 'Creature Traits'),
    0x1AD2417: ('building_traits', 'Data', 'Building Traits'),
    0x1AD2418: ('vehicle_traits', 'Data', 'Vehicle Traits'),
    0x2D5C9AF: ('summary', 'Data', 'Summary'),
    0x30BDEE3: ('pollen_metadata', 'Data', 'Pollen Metadata'),
    0x376C3DA: ('hm', 'Data', 'Height Map'),
    0x472329B: ('arth', 'Data', 'Arth Data'),
    0x5C74D18B: ('density', 'Data', 'Density Data'),
    0x617715D9: ('pd', 'Data', 'PD Data'),
    0x9B8E862F: ('world', 'Data', 'World Data'),
    0x76E1259D: ('physx_bin', 'Physics', 'PhysX Binary'),
    0x7EAB18FD: ('physx_xml', 'Physics', 'PhysX XML'),
    0x278CF8F2: ('cfx', 'Effect', 'CFX Effect'),
    0x1A527DB: ('snr', 'Audio', 'SNR Audio'),
    0x1EEF63A: ('sns', 'Audio', 'SNS Audio'),
    0x469A3F7: ('smt', 'Audio', 'SMT Audio'),
    0x22D2C83: ('pdr', 'Data', 'PDR Data'),
    0x6EFC6AA: ('package', 'Data', 'Package'),
    0x3055F61: ('instrument', 'Audio', 'Instrument'),
    0x497925E: ('mode', 'Data', 'Mode'),
    0x3F51892: ('children', 'Data', 'Children'),
    0x4B9EF6DC: ('structure', 'Data', 'Structure'),
    0xDA141C1B: ('populate', 'Data', 'Populate'),
    0xD92AF091: ('loottable', 'Data', 'Loot Table'),
    0xDBA35AE2: ('look_algorithm', 'Data', 'Look Algorithm'),
    0x612B3191: ('backgroundmap', 'Data', 'Background Map'),
    0xF9C3D770: ('random_creature', 'Creature', 'Random Creature'),
    0x8C042499: ('look_table', 'Data', 'Look Table'),
    0x2A3CE5B7: ('globals', 'Data', 'Globals'),
    0x76A8F7D8: ('geo', 'Data', 'Geometry'),
    0x2393756: ('cur', 'Data', 'Cursor'),
    0x339479: ('animstate', 'Animation', 'Animation State'),

    # Binary data files
    0x1A99B06B: ('bem', 'Data', 'BEM Data'),
    0x1E99B626: ('bat', 'Data', 'BAT Data'),
    0x1F639D98: ('xls', 'Spreadsheet', 'Excel File'),
    0x2399BE55: ('bld', 'Building', 'Building Data'),
    0x24682294: ('vcl', 'Vehicle', 'Vehicle Data'),
    0x25DF0112: ('gait', 'Animation', 'Gait Data'),
    0x2B978C46: ('crt', 'Data', 'CRT Data'),
    0x376840D7: ('vp6', 'Video', 'VP6 Video'),
    0x3C77532E: ('psd', 'Image', 'Photoshop File'),
    0x3C7E0F63: ('mcl', 'Data', 'MCL Data'),
    0x3D97A8E4: ('cll', 'Data', 'CLL Data'),
    0x438F6347: ('flr', 'Data', 'FLR Data'),
    0x476A98C7: ('ufo', 'Data', 'UFO Data'),
    0x477764F5: ('pdn', 'Image', 'Paint.NET File'),
    0x2081B4F5: ('log', 'Text', 'Log File'),
    0x1E99B639: ('bak', 'Backup', 'Backup File'),
    0x2699C284: ('bin', 'Binary', 'Binary Data'),
    0x1999AE0B: ('bfx', 'Effect', 'BFX Effect'),
    0x4F684A4: ('cmp', 'Data', 'CMP Data'),

    # Special binary files
    0xA11D3144: ('markerset.bin', 'Data', 'Marker Set'),
    0x76A8F7D8: ('noun.bin', 'Data', 'Noun Data'),
    0x92EA4AAC: ('servereventdef.bin', 'Data', 'Server Event Def'),
    0x17BBCE29: ('characteranimation.bin', 'Animation', 'Character Animation'),
    0xEEEB0E31: ('aidefinition.bin', 'AI', 'AI Definition'),
    0x474940A5: ('classattributes.bin', 'Data', 'Class Attributes'),
    0xD117AFCA: ('nonplayerclass.bin', 'Data', 'Non-Player Class'),
    0x9F8087D5: ('condition.bin', 'Data', 'Condition'),
    0x30728CE7: ('phase.bin', 'Data', 'Phase'),
    0x20426A63: ('crystaltuning.bin', 'Data', 'Crystal Tuning'),
    0xE5C2D838: ('elitenpcglobals.bin', 'Data', 'Elite NPC Globals'),
    0x7CA6C6C9: ('npcaffix.bin', 'Data', 'NPC Affix'),
    0x36201B51: ('magicnumbers.bin', 'Data', 'Magic Numbers'),
    0x8E94F44C: ('difficultytuning.bin', 'Data', 'Difficulty Tuning'),
    0xA8A25294: ('chainlevels.bin', 'Data', 'Chain Levels'),
    0xA38FA119: ('sectionconfig.bin', 'Data', 'Section Config'),
    0x9342C4D3: ('directortuning.bin', 'Data', 'Director Tuning'),
    0xAAED883B: ('charactertype.bin', 'Data', 'Character Type'),
    0x61BF29AA: ('lootpreferences.bin', 'Data', 'Loot Preferences'),
    0x58E9A177: ('weapontuning.bin', 'Data', 'Weapon Tuning'),
    0x534136B6: ('unlockstuning.bin', 'Data', 'Unlocks Tuning'),
    0x60C1B295: ('spaceshiptuning.bin', 'Vehicle', 'Spaceship Tuning'),
    0x1BCED3D7: ('lootrigblock.bin', 'Data', 'Loot Rig Block'),
    0x1DFEA336: ('testasset.bin', 'Data', 'Test Asset'),
    0x5CB9F7C7: ('affixtuning.bin', 'Data', 'Affix Tuning'),
    0x6A1812C6: ('lootprefix.bin', 'Data', 'Loot Prefix'),
    0x23EF98FD: ('pvplevels.bin', 'Data', 'PVP Levels'),
    0x52D095F6: ('levelconfig.bin', 'Level', 'Level Config'),
    0x68232164: ('levelobjectives.bin', 'Level', 'Level Objectives'),
    0xB9193960: ('level.bin', 'Level', 'Level Data'),
    0xBBA5400D: ('navpowertuning.bin', 'Data', 'Nav Power Tuning'),
    0x447DC2E5: ('lootsuffix.bin', 'Data', 'Loot Suffix'),

    # Special texture files
    0xEF7D16E1: ('uitexture', 'Texture', 'UI Texture'),
    0xDEAF6ADE: ('bak.png', 'Texture', 'Backup PNG'),
    0xDC74130E: ('bak2.png', 'Texture', 'Backup PNG 2'),

    # Special data files
    0x2523258: ('formation', 'Data', 'Formation'),
    0x24A0E52: ('trigger', 'Data', 'Trigger'),
    0x1C3C4B3: ('trait_pill', 'Data', 'Trait Pill'),
    0x2E5A9763: ('lrumetadata', 'Data', 'LRU Metadata'),
    0x793F6424: ('blockinfo', 'Data', 'Block Info'),
    0x366A930D: ('adv', 'Advection', 'Advection Data'),
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
        """Set up the file preview tab with enhanced preview capabilities."""
        # Preview controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(controls_frame, text="Preview Selected File", command=self.preview_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Clear Preview", command=self.clear_preview).pack(side=tk.LEFT)

        # Preview info label
        self.preview_info_var = tk.StringVar()
        self.preview_info_var.set("Select a file and click 'Preview Selected File' to view its contents.")
        info_label = ttk.Label(controls_frame, textvariable=self.preview_info_var, foreground="blue")
        info_label.pack(side=tk.LEFT, padx=(20, 0))

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
        """Preview the content of the selected file using appropriate preview method."""
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
                type_info = get_file_info_from_type(key.type_id)
                extension, category, description = type_info

                # Extract file content to memory
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

                    # Use appropriate preview method based on file type
                    preview_content = self._generate_preview_content(file_data, extension, category, key)

                    # Update preview text
                    self.preview_text.config(state=tk.NORMAL)
                    self.preview_text.delete(1.0, tk.END)
                    self.preview_text.insert(1.0, preview_content)
                    self.preview_text.config(state=tk.DISABLED)

                    # Update info label
                    self.preview_info_var.set(f"Previewing: {extension.upper()} file ({category}) - {len(file_data)} bytes")

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

    def _generate_preview_content(self, file_data: bytes, extension: str, category: str, resource_key) -> str:
        """Generate appropriate preview content based on file type."""
        file_size = len(file_data)

        # Image files - show basic info (can't display actual images in text widget)
        if extension.lower() in ['png', 'jpg', 'jpeg', 'bmp', 'tga', 'gif', 'dds', 'uitexture']:
            return self._preview_image(file_data, extension, resource_key)

        # Text-based files
        elif extension.lower() in ['txt', 'xml', 'html', 'json', 'ini', 'cfg', 'lua', 'js', 'py', 'log', 'css', 'xhtml']:
            return self._preview_text_file(file_data, extension)

        # Property files
        elif extension.lower() == 'prop':
            return self._preview_prop_file(file_data, resource_key)

        # Effect files
        elif extension.lower() in ['eff', 'pfx', 'effectmap', 'cfx', 'bfx']:
            return self._preview_effect_file(file_data, extension)

        # Model files
        elif extension.lower() in ['rw4', 'gmdl', 'bmdl', 'gmsh']:
            return self._preview_model_file(file_data, extension)

        # Animation files
        elif extension.lower() in ['animation', 'tlsa', 'ani', 'hkx', 'gait', 'animstate']:
            return self._preview_animation_file(file_data, extension)

        # Audio files
        elif extension.lower() in ['wav', 'ogg', 'mp3', 'bnk', 'snr', 'sns', 'smt', 'instrument', 'voice', 'submix']:
            return self._preview_audio_file(file_data, extension)

        # Cell/stage files
        elif extension.lower() == 'cell':
            return self._preview_cell_file(file_data)

        # Level files
        elif extension.lower() in ['lvl', 'level.bin', 'levelconfig.bin', 'levelobjectives.bin']:
            return self._preview_level_file(file_data, extension)

        # Creature data
        elif extension.lower() == 'creaturedata':
            return self._preview_creature_data(file_data)

        # Binary data files (various types)
        elif extension.lower() in ['bin', 'dat', 'blockinfo', 'adv', 'formation', 'trigger', 'trait_pill',
                                   'lrumetadata', 'cur', 'geom', 'geo', 'physx_bin', 'physx_xml']:
            return self._preview_binary_data(file_data, extension, category)

        # Default binary preview
        else:
            return self._preview_binary_data(file_data, extension, category)

    def _preview_image(self, file_data: bytes, extension: str, resource_key) -> str:
        """Preview image file information."""
        file_size = len(file_data)

        # Try to get basic image info if possible
        info_lines = [f"Image File ({extension.upper()}) - {file_size} bytes"]
        info_lines.append(f"Resource Key: {resource_key.group_id:08X}!{resource_key.instance_id:08X}.{resource_key.type_id:08X}")
        info_lines.append("")

        # For DDS files, try to parse header
        if extension.lower() == 'dds' and file_size >= 128:
            try:
                # DDS header parsing (simplified)
                width = int.from_bytes(file_data[16:20], 'little')
                height = int.from_bytes(file_data[12:16], 'little')
                info_lines.append(f"Dimensions: {width} x {height}")
            except:
                pass

        info_lines.append("")
        info_lines.append("Note: Full image preview not available in text mode.")
        info_lines.append("Use 'Extract' to save the image file and view it with an image viewer.")

        return "\n".join(info_lines)

    def _preview_text_file(self, file_data: bytes, extension: str) -> str:
        """Preview text-based files."""
        file_size = len(file_data)

        try:
            # Try different encodings
            for encoding in ['utf-8', 'utf-16', 'latin-1']:
                try:
                    text_content = file_data.decode(encoding, errors='replace')
                    break
                except:
                    continue
            else:
                text_content = file_data.decode('utf-8', errors='replace')

            # Limit preview size
            max_preview = 16384  # 16KB
            if len(text_content) > max_preview:
                text_content = text_content[:max_preview] + "\n\n[... Content truncated due to size ...]"

            header = f"Text File ({extension.upper()}) - {file_size} bytes\n\nContent:\n\n"
            return header + text_content

        except Exception as e:
            return f"Text File ({extension.upper()}) - {file_size} bytes\n\nError reading text content: {str(e)}\n\nHex dump:\n\n{self._create_hex_dump(file_data[:1024])}"

    def _preview_prop_file(self, file_data: bytes, resource_key) -> str:
        """Preview property file."""
        file_size = len(file_data)

        header = f"Property File - {file_size} bytes\n"
        header += f"Resource Key: {resource_key.group_id:08X}!{resource_key.instance_id:08X}.{resource_key.type_id:08X}\n\n"

        # Try to parse as text first
        try:
            text_content = file_data.decode('utf-8', errors='replace')
            if len(text_content) > 4096:
                text_content = text_content[:4096] + "\n\n[... Content truncated ...]"
            return header + "Content (Text View):\n\n" + text_content
        except:
            return header + "Binary property file:\n\n" + self._create_hex_dump(file_data[:2048])

    def _preview_effect_file(self, file_data: bytes, extension: str) -> str:
        """Preview effect file."""
        file_size = len(file_data)

        header = f"Effect File ({extension.upper()}) - {file_size} bytes\n\n"

        # Try text first, then hex
        try:
            text_content = file_data.decode('utf-8', errors='replace')
            if len(text_content) > 4096:
                text_content = text_content[:4096] + "\n\n[... Content truncated ...]"
            return header + "Content:\n\n" + text_content
        except:
            return header + "Binary effect data:\n\n" + self._create_hex_dump(file_data[:2048])

    def _preview_model_file(self, file_data: bytes, extension: str) -> str:
        """Preview 3D model file."""
        file_size = len(file_data)

        header = f"3D Model File ({extension.upper()}) - {file_size} bytes\n\n"
        header += "Note: This is a binary 3D model file.\n"
        header += "Use specialized 3D software to view the complete model.\n\n"

        # Try to extract some basic info
        if extension.lower() == 'rw4' and file_size >= 64:
            try:
                # RW4 files start with "RBFH" or similar
                magic = file_data[:4].decode('ascii', errors='ignore')
                header += f"File signature: {magic}\n"
            except:
                pass

        return header + "Hex dump (first 512 bytes):\n\n" + self._create_hex_dump(file_data[:512])

    def _preview_animation_file(self, file_data: bytes, extension: str) -> str:
        """Preview animation file."""
        file_size = len(file_data)

        header = f"Animation File ({extension.upper()}) - {file_size} bytes\n\n"
        header += "Note: This contains animation data for creatures/objects.\n\n"

        return header + "Binary animation data:\n\n" + self._create_hex_dump(file_data[:1024])

    def _preview_audio_file(self, file_data: bytes, extension: str) -> str:
        """Preview audio file."""
        file_size = len(file_data)

        header = f"Audio File ({extension.upper()}) - {file_size} bytes\n\n"

        # Try to get basic WAV info
        if extension.lower() == 'wav' and file_size >= 44:
            try:
                channels = int.from_bytes(file_data[22:24], 'little')
                sample_rate = int.from_bytes(file_data[24:28], 'little')
                bits_per_sample = int.from_bytes(file_data[34:36], 'little')
                header += f"Channels: {channels}\n"
                header += f"Sample Rate: {sample_rate} Hz\n"
                header += f"Bits per Sample: {bits_per_sample}\n\n"
            except:
                pass

        header += "Note: Use an audio player to listen to this file.\n\n"
        return header + "Raw audio data (first 256 bytes):\n\n" + self._create_hex_dump(file_data[:256])

    def _preview_cell_file(self, file_data: bytes) -> str:
        """Preview cell/stage file."""
        file_size = len(file_data)

        header = f"Cell/Stage File - {file_size} bytes\n\n"
        header += "This file contains Spore cell stage data and configuration.\n\n"

        return header + "Binary cell data:\n\n" + self._create_hex_dump(file_data[:1024])

    def _preview_level_file(self, file_data: bytes, extension: str) -> str:
        """Preview level file."""
        file_size = len(file_data)

        header = f"Level File ({extension}) - {file_size} bytes\n\n"
        header += "This file contains level configuration and objectives.\n\n"

        return header + "Binary level data:\n\n" + self._create_hex_dump(file_data[:1024])

    def _preview_creature_data(self, file_data: bytes) -> str:
        """Preview creature data file."""
        file_size = len(file_data)

        header = f"Creature Data File - {file_size} bytes\n\n"
        header += "This file contains creature definition and statistics.\n\n"

        return header + "Binary creature data:\n\n" + self._create_hex_dump(file_data[:1024])

    def _preview_binary_data(self, file_data: bytes, extension: str, category: str) -> str:
        """Preview generic binary data."""
        file_size = len(file_data)

        header = f"Binary File ({extension.upper()}) - {file_size} bytes\n"
        header += f"Category: {category}\n\n"

        # Try to detect some common patterns
        if file_data.startswith(b'RBFH'):
            header += "Detected: RenderWare file header\n"
        elif file_data.startswith(b'DDS '):
            header += "Detected: DDS texture file\n"
        elif file_data[:4] in [b'PROP', b'prop']:
            header += "Detected: Property file\n"

        header += "\nHex dump (first 1024 bytes):\n\n"
        return header + self._create_hex_dump(file_data[:1024])

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
        """Clear the preview display."""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)
        self.preview_info_var.set("Select a file and click 'Preview Selected File' to view its contents.")
        self.status_var.set("Preview cleared")

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
