#!/usr/bin/env python3
"""
Simple Interface for DBPF Python Implementation

This module provides a user-friendly interface for working with DBPF files,
including unpacking, listing contents, and extracting specific files.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
import os

from dbpf_unpacker import DBPFUnpacker, DatabasePackedFile, ResourceKey


class DBPFInterface:
    """Simple interface for DBPF file operations."""

    def __init__(self, dbpf_path: str):
        """
        Initialize the DBPF interface.

        Args:
            dbpf_path: Path to the DBPF file
        """
        self.dbpf_path = Path(dbpf_path)
        self.dbpf = DatabasePackedFile()
        self._loaded = False

        if not self.dbpf_path.exists():
            raise FileNotFoundError(f"DBPF file not found: {dbpf_path}")

    def load(self) -> None:
        """Load and parse the DBPF file."""
        if self._loaded:
            return

        try:
            with open(self.dbpf_path, 'rb') as f:
                self.dbpf.read(f)
            self._loaded = True
            print(f"Loaded DBPF file: {self.dbpf_path}")
            print(f"Format: {'DBBF' if self.dbpf.is_dbbf else 'DBPF'}")
            print(f"Version: {self.dbpf.major_version}.{self.dbpf.min_version}")
            print(f"Files: {self.dbpf.index_count}")
        except Exception as e:
            raise RuntimeError(f"Failed to load DBPF file: {e}")

    def list_files(self, limit: Optional[int] = None) -> List[str]:
        """
        List all files in the DBPF archive.

        Args:
            limit: Maximum number of files to list (None for all)

        Returns:
            List of file descriptions
        """
        self.load()

        files = []
        for i, item in enumerate(self.dbpf.index.items):
            if limit and i >= limit:
                break

            compressed = "compressed" if item.is_compressed else "uncompressed"
            size_info = f"{item.compressed_size} -> {item.mem_size}" if item.is_compressed else str(item.mem_size)

            files.append(f"{item.name} | {compressed} | {size_info} bytes")

        return files

    def extract_file(self, resource_key: ResourceKey, output_path: str) -> bool:
        """
        Extract a specific file by resource key.

        Args:
            resource_key: The resource key of the file to extract
            output_path: Where to save the extracted file

        Returns:
            True if extraction successful, False otherwise
        """
        self.load()

        # Find the item
        item = None
        for dbpf_item in self.dbpf.index.items:
            if dbpf_item.name.is_equivalent(resource_key):
                item = dbpf_item
                break

        if not item:
            print(f"File not found: {resource_key}")
            return False

        try:
            with open(self.dbpf_path, 'rb') as f:
                f.seek(item.chunk_offset)

                if item.is_compressed:
                    from dbpf_unpacker import RefPackCompression
                    compressed_data = f.read(item.compressed_size)
                    data = RefPackCompression.decompress_fast(compressed_data)
                else:
                    data = f.read(item.mem_size)

            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as out_f:
                out_f.write(data)

            print(f"Extracted {resource_key} to {output_path}")
            return True

        except Exception as e:
            print(f"Error extracting {resource_key}: {e}")
            return False

    def extract_all(self, output_dir: str, verbose: bool = False) -> int:
        """
        Extract all files to a directory.

        Args:
            output_dir: Output directory
            verbose: Whether to show progress

        Returns:
            Number of files extracted successfully
        """
        unpacker = DBPFUnpacker(str(self.dbpf_path))
        unpacker.unpack(output_dir)

        # Count extracted files
        extracted = 0
        for root, dirs, files in os.walk(output_dir):
            extracted += len(files)

        if verbose:
            print(f"Extracted {extracted} files to {output_dir}")

        return extracted

    def get_file_info(self, resource_key: ResourceKey) -> Optional[dict]:
        """
        Get information about a specific file.

        Args:
            resource_key: The resource key to look up

        Returns:
            Dictionary with file information, or None if not found
        """
        self.load()

        for item in self.dbpf.index.items:
            if item.name.is_equivalent(resource_key):
                return {
                    'resource_key': str(item.name),
                    'group_id': f"0x{item.name.group_id:08X}",
                    'instance_id': f"0x{item.name.instance_id:08X}",
                    'type_id': f"0x{item.name.type_id:08X}",
                    'offset': item.chunk_offset,
                    'compressed_size': item.compressed_size,
                    'uncompressed_size': item.mem_size,
                    'compressed': item.is_compressed,
                    'saved': item.is_saved
                }

        return None


def parse_resource_key(key_str: str) -> ResourceKey:
    """
    Parse a resource key string in format: GROUP!INSTANCE.TYPE

    Args:
        key_str: String representation of resource key

    Returns:
        ResourceKey object
    """
    try:
        parts = key_str.replace('!', '.').split('.')
        if len(parts) != 3:
            raise ValueError("Invalid format. Use: GROUP!INSTANCE.TYPE")

        group = int(parts[0], 16)
        instance = int(parts[1], 16)
        type_id = int(parts[2], 16)

        return ResourceKey(group, instance, type_id)
    except ValueError as e:
        raise ValueError(f"Invalid resource key format: {e}")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Simple DBPF File Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file.package list                    # List all files
  %(prog)s file.package list --limit 10         # List first 10 files
  %(prog)s file.package extract 12345678!9ABCDEF0.11111111 output.dat
  %(prog)s file.package unpack output_dir       # Extract all files
  %(prog)s file.package info 12345678!9ABCDEF0.11111111
        """
    )

    parser.add_argument('dbpf_file', help='Path to DBPF file')
    parser.add_argument('command', choices=['list', 'extract', 'unpack', 'info'],
                       help='Command to execute')
    parser.add_argument('args', nargs='*', help='Additional arguments for command')
    parser.add_argument('--limit', '-l', type=int, help='Limit number of files to list')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    try:
        interface = DBPFInterface(args.dbpf_file)

        if args.command == 'list':
            files = interface.list_files(args.limit)
            for file_info in files:
                print(file_info)

        elif args.command == 'extract':
            if len(args.args) != 2:
                parser.error("extract command requires resource_key and output_path")
            key = parse_resource_key(args.args[0])
            interface.extract_file(key, args.args[1])

        elif args.command == 'unpack':
            if len(args.args) != 1:
                parser.error("unpack command requires output_directory")
            interface.extract_all(args.args[0], args.verbose)

        elif args.command == 'info':
            if len(args.args) != 1:
                parser.error("info command requires resource_key")
            key = parse_resource_key(args.args[0])
            info = interface.get_file_info(key)
            if info:
                print("File Information:")
                for k, v in info.items():
                    print(f"  {k}: {v}")
            else:
                print(f"File not found: {key}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
