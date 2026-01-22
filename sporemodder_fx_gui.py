#!/usr/bin/env python3
"""
SporeModder-FX Python Tools GUI Interface

A simple graphical interface for the Python implementations in SporeModder-FX.
Provides access to DBPF unpacking and advect file visualization/generation.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import subprocess
import sys
import os
import threading
from pathlib import Path

# Import our DBPF interface
try:
    from dbpf_interface import DBPFInterface, parse_resource_key
    DBPF_INTERFACE_AVAILABLE = True
except ImportError:
    DBPF_INTERFACE_AVAILABLE = False


class SporeModderFXGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SporeModder-FX Python Tools")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Create notebook for tabs
        self.notebook = tk.ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # DBPF Unpacker tab
        self.dbpf_frame = tk.ttk.Frame(self.notebook)
        self.notebook.add(self.dbpf_frame, text='DBPF Unpacker')

        # Advect Tools tab
        self.advect_frame = tk.ttk.Frame(self.notebook)
        self.notebook.add(self.advect_frame, text='Advect Tools')

        self.setup_dbpf_tab()
        self.setup_advect_tab()

    def setup_dbpf_tab(self):
        """Setup the DBPF unpacker tab."""
        frame = self.dbpf_frame

        # Title
        title_label = tk.Label(frame, text="DBPF File Tools",
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Description
        desc_text = ("Work with Database Packed Files (DBPF) used in Spore.\n"
                    "Extract entire archives or individual files, and explore contents.")
        desc_label = tk.Label(frame, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=5)

        # Create notebook for DBPF sub-tabs
        dbpf_notebook = tk.ttk.Notebook(frame)
        dbpf_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Unpack All tab
        unpack_frame = tk.ttk.Frame(dbpf_notebook)
        dbpf_notebook.add(unpack_frame, text='Unpack All')

        # Explore tab
        explore_frame = tk.ttk.Frame(dbpf_notebook)
        dbpf_notebook.add(explore_frame, text='Explore')

        # Extract Single tab
        extract_frame = tk.ttk.Frame(dbpf_notebook)
        dbpf_notebook.add(extract_frame, text='Extract Single')

        self.setup_unpack_tab(unpack_frame)
        self.setup_explore_tab(explore_frame)
        self.setup_extract_tab(extract_frame)

    def setup_unpack_tab(self, frame):
        """Setup the unpack all tab."""
        # Input file selection
        input_frame = tk.Frame(frame)
        input_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(input_frame, text="DBPF File:").grid(row=0, column=0, sticky='w')
        self.dbpf_input_var = tk.StringVar()
        self.dbpf_input_entry = tk.Entry(input_frame, textvariable=self.dbpf_input_var, width=50)
        self.dbpf_input_entry.grid(row=0, column=1, padx=(10, 0))
        tk.Button(input_frame, text="Browse...", command=self.browse_dbpf_input).grid(row=0, column=2, padx=(10, 0))

        # Output directory selection
        output_frame = tk.Frame(frame)
        output_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky='w')
        self.dbpf_output_var = tk.StringVar()
        self.dbpf_output_entry = tk.Entry(output_frame, textvariable=self.dbpf_output_var, width=50)
        self.dbpf_output_entry.grid(row=0, column=1, padx=(10, 0))
        tk.Button(output_frame, text="Browse...", command=self.browse_dbpf_output).grid(row=0, column=2, padx=(10, 0))

        # Unpack button
        unpack_button = tk.Button(frame, text="Unpack DBPF File",
                                 command=self.unpack_dbpf, bg='#4CAF50', fg='white',
                                 font=('Arial', 10, 'bold'))
        unpack_button.pack(pady=20)

        # Output text area
        self.dbpf_output_text = scrolledtext.ScrolledText(frame, height=10, width=70)
        self.dbpf_output_text.pack(padx=20, pady=10, fill='both', expand=True)

    def setup_explore_tab(self, frame):
        """Setup the explore tab."""
        # Input file selection
        input_frame = tk.Frame(frame)
        input_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(input_frame, text="DBPF File:").grid(row=0, column=0, sticky='w')
        self.dbpf_explore_var = tk.StringVar()
        self.dbpf_explore_entry = tk.Entry(input_frame, textvariable=self.dbpf_explore_var, width=50)
        self.dbpf_explore_entry.grid(row=0, column=1, padx=(10, 0))
        tk.Button(input_frame, text="Browse...", command=self.browse_dbpf_explore).grid(row=0, column=2, padx=(10, 0))

        # Buttons frame
        buttons_frame = tk.Frame(frame)
        buttons_frame.pack(fill='x', padx=20, pady=5)

        tk.Button(buttons_frame, text="Load & List Files",
                 command=self.load_and_list_files, bg='#2196F3', fg='white').pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(buttons_frame, text="Show Info",
                 command=self.show_dbpf_info, bg='#FF9800', fg='white').pack(side=tk.LEFT)

        # File list
        list_frame = tk.Frame(frame)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        tk.Label(list_frame, text="Files in DBPF:").pack(anchor='w')

        # Create treeview for file list
        self.file_tree = ttk.Treeview(list_frame, columns=('resource', 'size', 'compressed'), show='headings', height=15)
        self.file_tree.heading('resource', text='Resource Key')
        self.file_tree.heading('size', text='Size')
        self.file_tree.heading('compressed', text='Compressed')

        self.file_tree.column('resource', width=300)
        self.file_tree.column('size', width=100)
        self.file_tree.column('compressed', width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        # Bind double-click to show file info
        self.file_tree.bind('<Double-1>', self.on_file_double_click)

    def setup_extract_tab(self, frame):
        """Setup the extract single file tab."""
        # DBPF file selection
        dbpf_frame = tk.Frame(frame)
        dbpf_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(dbpf_frame, text="DBPF File:").grid(row=0, column=0, sticky='w')
        self.dbpf_extract_var = tk.StringVar()
        self.dbpf_extract_entry = tk.Entry(dbpf_frame, textvariable=self.dbpf_extract_var, width=50)
        self.dbpf_extract_entry.grid(row=0, column=1, padx=(10, 0))
        tk.Button(dbpf_frame, text="Browse...", command=self.browse_dbpf_extract).grid(row=0, column=2, padx=(10, 0))

        # Resource key input
        key_frame = tk.Frame(frame)
        key_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(key_frame, text="Resource Key:").grid(row=0, column=0, sticky='w')
        self.resource_key_var = tk.StringVar()
        self.resource_key_entry = tk.Entry(key_frame, textvariable=self.resource_key_var, width=50)
        self.resource_key_entry.grid(row=0, column=1, padx=(10, 0))

        # Output file selection
        output_frame = tk.Frame(frame)
        output_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky='w')
        self.extract_output_var = tk.StringVar()
        self.extract_output_entry = tk.Entry(output_frame, textvariable=self.extract_output_var, width=50)
        self.extract_output_entry.grid(row=0, column=1, padx=(10, 0))
        tk.Button(output_frame, text="Browse...", command=self.browse_extract_output).grid(row=0, column=2, padx=(10, 0))

        # Extract button
        extract_button = tk.Button(frame, text="Extract File",
                                  command=self.extract_single_file, bg='#4CAF50', fg='white',
                                  font=('Arial', 10, 'bold'))
        extract_button.pack(pady=20)

        # Status text
        self.extract_status_text = scrolledtext.ScrolledText(frame, height=8, width=70)
        self.extract_status_text.pack(padx=20, pady=10, fill='both', expand=True)

    def setup_advect_tab(self):
        """Setup the advect tools tab."""
        frame = self.advect_frame

        # Title
        title_label = tk.Label(frame, text="Advect File Tools",
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Description
        desc_text = ("Visualize or generate .advect files (128x128 vector force fields).\n"
                    ".advect files are used in Spore for particle effects and fluid simulation.")
        desc_label = tk.Label(frame, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=5)

        # Notebook for sub-tabs
        sub_notebook = tk.ttk.Notebook(frame)
        sub_notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Visualize tab
        visualize_frame = tk.ttk.Frame(sub_notebook)
        sub_notebook.add(visualize_frame, text='Visualize')

        # Generate tab
        generate_frame = tk.ttk.Frame(sub_notebook)
        sub_notebook.add(generate_frame, text='Generate')

        self.setup_visualize_tab(visualize_frame)
        self.setup_generate_tab(generate_frame)

    def setup_visualize_tab(self, frame):
        """Setup the visualize advect tab."""
        # File selection
        file_frame = tk.Frame(frame)
        file_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(file_frame, text=".advect File:").grid(row=0, column=0, sticky='w')
        self.advect_viz_var = tk.StringVar()
        self.advect_viz_entry = tk.Entry(file_frame, textvariable=self.advect_viz_var, width=50)
        self.advect_viz_entry.grid(row=0, column=1, padx=(10, 0))
        tk.Button(file_frame, text="Browse...", command=self.browse_advect_viz).grid(row=0, column=2, padx=(10, 0))

        # Note about matplotlib
        note_label = tk.Label(frame,
                             text="Note: Visualization requires matplotlib. The plot will open in a separate window.",
                             fg='#666666', wraplength=500, justify=tk.LEFT)
        note_label.pack(pady=5)

        # Visualize button
        viz_button = tk.Button(frame, text="Visualize Advect File",
                              command=self.visualize_advect, bg='#2196F3', fg='white',
                              font=('Arial', 10, 'bold'))
        viz_button.pack(pady=20)

    def setup_generate_tab(self, frame):
        """Setup the generate advect tab."""
        # Output file selection
        file_frame = tk.Frame(frame)
        file_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(file_frame, text="Output .advect File:").grid(row=0, column=0, sticky='w')
        self.advect_gen_var = tk.StringVar()
        self.advect_gen_entry = tk.Entry(file_frame, textvariable=self.advect_gen_var, width=50)
        self.advect_gen_entry.grid(row=0, column=1, padx=(10, 0))
        tk.Button(file_frame, text="Browse...", command=self.browse_advect_gen).grid(row=0, column=2, padx=(10, 0))

        # Math expression input
        expr_frame = tk.Frame(frame)
        expr_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(expr_frame, text="Math Expression:").grid(row=0, column=0, sticky='nw', pady=(0, 5))
        self.expression_var = tk.StringVar()
        self.expression_entry = tk.Entry(expr_frame, textvariable=self.expression_var, width=50)
        self.expression_entry.grid(row=0, column=1, padx=(10, 0), pady=(0, 5))

        # Examples
        examples_text = ("Examples:\n"
                        "• np.sin(x), np.cos(y)  - Sine/cosine waves\n"
                        "• x*2-1, y*2-1  - Radial flow from center\n"
                        "• np.random.random()*2-1, np.random.random()*2-1  - Random\n"
                        "• 0.1*np.sin(10*x), 0.1*np.cos(10*y)  - Turbulent flow\n\n"
                        "Expression should return 2 or 3 values (x,y,z components)\n"
                        "using variables 'x' and 'y' (normalized 0.0 to 1.0)")
        examples_label = tk.Label(expr_frame, text=examples_text, justify=tk.LEFT,
                                 fg='#666666', wraplength=300)
        examples_label.grid(row=1, column=1, sticky='w', padx=(10, 0))

        # Generate button
        gen_button = tk.Button(frame, text="Generate Advect File",
                              command=self.generate_advect, bg='#FF9800', fg='white',
                              font=('Arial', 10, 'bold'))
        gen_button.pack(pady=20)

    def browse_dbpf_input(self):
        """Browse for DBPF input file."""
        filename = filedialog.askopenfilename(
            title="Select DBPF file",
            filetypes=[("DBPF files", "*.package"), ("All files", "*.*")]
        )
        if filename:
            self.dbpf_input_var.set(filename)

    def browse_dbpf_output(self):
        """Browse for output directory."""
        dirname = filedialog.askdirectory(title="Select output directory")
        if dirname:
            self.dbpf_output_var.set(dirname)

    def browse_advect_viz(self):
        """Browse for advect file to visualize."""
        filename = filedialog.askopenfilename(
            title="Select .advect file",
            filetypes=[("Advect files", "*.advect"), ("All files", "*.*")]
        )
        if filename:
            self.advect_viz_var.set(filename)

    def browse_dbpf_extract(self):
        """Browse for DBPF file to extract from."""
        filename = filedialog.askopenfilename(
            title="Select DBPF file",
            filetypes=[("DBPF files", "*.package"), ("All files", "*.*")]
        )
        if filename:
            self.dbpf_extract_var.set(filename)

    def browse_extract_output(self):
        """Browse for output file location."""
        filename = filedialog.asksaveasfilename(
            title="Save extracted file",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            self.extract_output_var.set(filename)

    def browse_dbpf_explore(self):
        """Browse for DBPF file to explore."""
        filename = filedialog.askopenfilename(
            title="Select DBPF file",
            filetypes=[("DBPF files", "*.package"), ("All files", "*.*")]
        )
        if filename:
            self.dbpf_explore_var.set(filename)

    def unpack_dbpf(self):
        """Unpack the selected DBPF file."""
        input_file = self.dbpf_input_var.get().strip()
        output_dir = self.dbpf_output_var.get().strip()

        if not input_file:
            messagebox.showerror("Error", "Please select a DBPF input file.")
            return
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return

        if not Path(input_file).exists():
            messagebox.showerror("Error", f"Input file does not exist: {input_file}")
            return

        # Clear output text
        self.dbpf_output_text.delete(1.0, tk.END)
        self.dbpf_output_text.insert(tk.END, f"Unpacking {input_file} to {output_dir}...\n\n")

        try:
            # Run the unpacker
            result = subprocess.run([
                sys.executable, 'dbpf_unpacker.py', input_file, output_dir
            ], capture_output=True, text=True, cwd=os.getcwd())

            # Display output
            if result.stdout:
                self.dbpf_output_text.insert(tk.END, result.stdout)
            if result.stderr:
                self.dbpf_output_text.insert(tk.END, f"Errors:\n{result.stderr}")

            if result.returncode == 0:
                messagebox.showinfo("Success", "DBPF file unpacked successfully!")
            else:
                messagebox.showerror("Error", f"Unpacking failed with return code {result.returncode}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to run unpacker: {str(e)}")

    def load_and_list_files(self):
        """Load DBPF file and list its contents."""
        dbpf_file = self.dbpf_explore_var.get().strip()

        if not dbpf_file:
            messagebox.showerror("Error", "Please select a DBPF file.")
            return

        if not Path(dbpf_file).exists():
            messagebox.showerror("Error", f"File does not exist: {dbpf_file}")
            return

        if not DBPF_INTERFACE_AVAILABLE:
            messagebox.showerror("Error", "DBPF interface not available. Please ensure dbpf_interface.py is in the same directory.")
            return

        def load_task():
            try:
                # Clear existing items
                for item in self.file_tree.get_children():
                    self.file_tree.delete(item)

                # Load and list files
                interface = DBPFInterface(dbpf_file)
                files = interface.list_files()

                # Add to treeview
                for file_info in files:
                    # Parse the file info: "RESOURCE_KEY | compressed/uncompressed | SIZE bytes"
                    parts = file_info.split(' | ')
                    if len(parts) >= 3:
                        resource = parts[0]
                        compressed = parts[1]
                        size = parts[2]
                        self.file_tree.insert('', 'end', values=(resource, size, compressed))

                messagebox.showinfo("Success", f"Loaded {len(files)} files from DBPF archive.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load DBPF file: {str(e)}")

        # Run in thread to avoid blocking GUI
        thread = threading.Thread(target=load_task, daemon=True)
        thread.start()

    def show_dbpf_info(self):
        """Show information about the loaded DBPF file."""
        dbpf_file = self.dbpf_explore_var.get().strip()

        if not dbpf_file:
            messagebox.showerror("Error", "Please select a DBPF file first.")
            return

        if not DBPF_INTERFACE_AVAILABLE:
            messagebox.showerror("Error", "DBPF interface not available.")
            return

        try:
            interface = DBPFInterface(dbpf_file)
            interface.load()

            info_text = f"""DBPF File Information:

File: {dbpf_file}
Format: {'DBBF (64-bit)' if interface.dbpf.is_dbbf else 'DBPF (32-bit)'}
Version: {interface.dbpf.major_version}.{interface.dbpf.min_version}
Index Version: {interface.dbpf.index_major_version}.{interface.dbpf.index_minor_version}
Total Files: {interface.dbpf.index_count}
Index Offset: {interface.dbpf.index_offset}
Index Size: {interface.dbpf.index_size} bytes
"""

            messagebox.showinfo("DBPF Information", info_text)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get DBPF info: {str(e)}")

    def on_file_double_click(self, event):
        """Handle double-click on file in treeview."""
        selection = self.file_tree.selection()
        if not selection:
            return

        item = self.file_tree.item(selection[0])
        resource_key_str = item['values'][0]

        # Show file information
        dbpf_file = self.dbpf_explore_var.get().strip()
        if not dbpf_file or not DBPF_INTERFACE_AVAILABLE:
            return

        try:
            interface = DBPFInterface(dbpf_file)
            key = parse_resource_key(resource_key_str)
            info = interface.get_file_info(key)

            if info:
                info_text = f"""File Information:

Resource Key: {info['resource_key']}
Group ID: {info['group_id']}
Instance ID: {info['instance_id']}
Type ID: {info['type_id']}
Offset: {info['offset']}
Compressed Size: {info['compressed_size']} bytes
Uncompressed Size: {info['uncompressed_size']} bytes
Compressed: {info['compressed']}
Saved: {info['saved']}
"""
                messagebox.showinfo("File Information", info_text)
            else:
                messagebox.showerror("Error", "Could not get file information.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get file info: {str(e)}")

    def extract_single_file(self):
        """Extract a single file from the DBPF archive."""
        dbpf_file = self.dbpf_extract_var.get().strip()
        resource_key_str = self.resource_key_var.get().strip()
        output_file = self.extract_output_var.get().strip()

        if not dbpf_file:
            messagebox.showerror("Error", "Please select a DBPF file.")
            return
        if not resource_key_str:
            messagebox.showerror("Error", "Please enter a resource key.")
            return
        if not output_file:
            messagebox.showerror("Error", "Please select an output file location.")
            return

        if not DBPF_INTERFACE_AVAILABLE:
            messagebox.showerror("Error", "DBPF interface not available.")
            return

        # Clear status text
        self.extract_status_text.delete(1.0, tk.END)
        self.extract_status_text.insert(tk.END, f"Extracting {resource_key_str} from {dbpf_file}...\n")

        def extract_task():
            try:
                interface = DBPFInterface(dbpf_file)
                key = parse_resource_key(resource_key_str)

                success = interface.extract_file(key, output_file)

                if success:
                    self.extract_status_text.insert(tk.END, f"✓ Successfully extracted to: {output_file}\n")
                    messagebox.showinfo("Success", f"File extracted successfully!\nSaved to: {output_file}")
                else:
                    self.extract_status_text.insert(tk.END, "✗ Failed to extract file (file not found or error occurred)\n")
                    messagebox.showerror("Error", "Failed to extract file. Check the resource key and try again.")

            except ValueError as e:
                self.extract_status_text.insert(tk.END, f"✗ Invalid resource key format: {e}\n")
                messagebox.showerror("Error", f"Invalid resource key format: {e}")
            except Exception as e:
                self.extract_status_text.insert(tk.END, f"✗ Extraction failed: {e}\n")
                messagebox.showerror("Error", f"Extraction failed: {str(e)}")

        # Run in thread to avoid blocking GUI
        thread = threading.Thread(target=extract_task, daemon=True)
        thread.start()

    def visualize_advect(self):
        """Visualize the selected advect file."""
        input_file = self.advect_viz_var.get().strip()

        if not input_file:
            messagebox.showerror("Error", "Please select an .advect file to visualize.")
            return

        if not Path(input_file).exists():
            messagebox.showerror("Error", f"File does not exist: {input_file}")
            return

        try:
            # Check if matplotlib is available
            import matplotlib
            matplotlib.use('TkAgg')  # Use TkAgg backend for tkinter compatibility

            # Run the visualization
            result = subprocess.run([
                sys.executable, 'advect.py', input_file
            ], capture_output=True, text=True, cwd=os.getcwd())

            if result.returncode != 0:
                if result.stderr:
                    messagebox.showerror("Error", f"Visualization failed:\n{result.stderr}")
                else:
                    messagebox.showerror("Error", "Visualization failed (check matplotlib installation)")

        except ImportError:
            messagebox.showerror("Error", "Matplotlib is required for visualization. Install with: pip install matplotlib numpy")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run visualization: {str(e)}")

    def generate_advect(self):
        """Generate a new advect file."""
        output_file = self.advect_gen_var.get().strip()
        expression = self.expression_var.get().strip()

        if not output_file:
            messagebox.showerror("Error", "Please select an output file location.")
            return
        if not expression:
            messagebox.showerror("Error", "Please enter a math expression.")
            return

        try:
            # Run the generator
            result = subprocess.run([
                sys.executable, 'advect.py', output_file, '--generate', expression
            ], capture_output=True, text=True, cwd=os.getcwd())

            if result.returncode == 0:
                messagebox.showinfo("Success", f"Advect file generated successfully!\nSaved to: {output_file}")
            else:
                error_msg = result.stderr if result.stderr else "Unknown error occurred"
                messagebox.showerror("Error", f"Generation failed:\n{error_msg}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate advect file: {str(e)}")


def main():
    """Main entry point."""
    root = tk.Tk()

    # Set theme if ttkthemes is available
    try:
        import ttkthemes
        style = ttkthemes.ThemedStyle(root)
        style.set_theme("arc")  # Modern looking theme
    except ImportError:
        # Use default theme
        style = ttk.Style()
        style.theme_use('default')

    app = SporeModderFXGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()