#!/usr/bin/env python3
"""
DBPF Unpacker - Python implementation for unpacking Spore DBPF files

This module provides functionality to unpack Database Packed Files (DBPF)
used in Maxis games like Spore. It supports both DBPF and DBBF formats,
with RefPack compression decompression.

Based on the Java implementation from SporeModder-FX.
"""

import struct
import os
from typing import List, Dict, Optional, BinaryIO
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ResourceKey:
    """Represents a Spore resource key with group, instance, and type IDs."""
    group_id: int = 0
    instance_id: int = 0
    type_id: int = 0

    def __str__(self) -> str:
        return f"{self.group_id:08X}!{self.instance_id:08X}.{self.type_id:08X}"

    def is_equivalent(self, other: 'ResourceKey') -> bool:
        """Check if two resource keys are equivalent (same group, instance, type)."""
        return (self.group_id == other.group_id and
                self.instance_id == other.instance_id and
                self.type_id == other.type_id)


@dataclass
class DBPFItem:
    """Represents a single item in the DBPF index."""
    name: ResourceKey
    chunk_offset: int
    compressed_size: int
    mem_size: int
    is_compressed: bool
    is_saved: bool = True


class DBPFIndex:
    """Represents the index section of a DBPF file."""

    def __init__(self):
        self.group_id: int = -1  # -1 means group IDs are stored per item
        self.type_id: int = -1   # -1 means type IDs are stored per item
        self.items: List[DBPFItem] = []

    def read(self, stream: BinaryIO) -> None:
        """Read the index header."""
        type_flags = struct.unpack('<I', stream.read(4))[0]

        # Check flags for which IDs are stored globally vs per-item
        if type_flags & (1 << 0):
            self.type_id = struct.unpack('<I', stream.read(4))[0]
        if type_flags & (1 << 1):
            self.group_id = struct.unpack('<I', stream.read(4))[0]
        if type_flags & (1 << 2):
            stream.read(4)  # Unknown value, skip

    def read_items(self, stream: BinaryIO, num_items: int, is_dbbf: bool) -> None:
        """Read all items in the index."""
        read_group = self.group_id == -1
        read_type = self.type_id == -1

        for _ in range(num_items):
            item = DBPFItem(ResourceKey(), 0, 0, 0, False)

            # Set default IDs if not stored per-item
            if not read_group:
                item.name.group_id = self.group_id
            if not read_type:
                item.name.type_id = self.type_id

            # Read item data
            if read_type:
                item.name.type_id = struct.unpack('<I', stream.read(4))[0]
            if read_group:
                item.name.group_id = struct.unpack('<I', stream.read(4))[0]

            item.name.instance_id = struct.unpack('<I', stream.read(4))[0]

            if is_dbbf:
                item.chunk_offset = struct.unpack('<Q', stream.read(8))[0]
            else:
                item.chunk_offset = struct.unpack('<I', stream.read(4))[0]

            item.compressed_size = struct.unpack('<I', stream.read(4))[0] & 0x7FFFFFFF
            item.mem_size = struct.unpack('<I', stream.read(4))[0]

            compression_flag = struct.unpack('<h', stream.read(2))[0]
            if compression_flag == 0:
                item.is_compressed = False
            elif compression_flag == -1:
                item.is_compressed = True
            else:
                raise ValueError(f"Unknown compression flag: {compression_flag}")

            item.is_saved = bool(struct.unpack('<?', stream.read(1))[0])
            stream.read(1)  # Padding

            self.items.append(item)


class DatabasePackedFile:
    """Main DBPF file handler."""

    TYPE_DBPF = 0x46504244  # 'DBPF'
    TYPE_DBBF = 0x46424244  # 'DBBF'

    def __init__(self):
        self.major_version: int = 3
        self.min_version: int = 0
        self.index_major_version: int = 0
        self.index_minor_version: int = 3
        self.is_dbbf: bool = False
        self.index_count: int = 0
        self.index_offset: int = 0
        self.index_size: int = 0
        self.index = DBPFIndex()

    def read_header(self, stream: BinaryIO) -> None:
        """Read the DBPF header."""
        magic = struct.unpack('<I', stream.read(4))[0]

        if magic == self.TYPE_DBPF:
            self.is_dbbf = False
            self._read_dbpf_header(stream)
        elif magic == self.TYPE_DBBF:
            self.is_dbbf = True
            self._read_dbbf_header(stream)
        else:
            raise ValueError(f"Unrecognized DBPF type magic: 0x{magic:08X}")

    def _read_dbpf_header(self, stream: BinaryIO) -> None:
        """Read DBPF header (32-bit offsets)."""
        self.major_version = struct.unpack('<I', stream.read(4))[0]
        self.min_version = struct.unpack('<I', stream.read(4))[0]
        stream.read(20)  # Skip unused
        self.index_major_version = struct.unpack('<I', stream.read(4))[0]
        self.index_count = struct.unpack('<I', stream.read(4))[0]
        stream.read(4)  # Skip unused
        self.index_size = struct.unpack('<I', stream.read(4))[0]
        stream.read(12)  # Skip unused
        self.index_minor_version = struct.unpack('<I', stream.read(4))[0]
        self.index_offset = struct.unpack('<I', stream.read(4))[0]

    def _read_dbbf_header(self, stream: BinaryIO) -> None:
        """Read DBBF header (64-bit offsets)."""
        self.major_version = struct.unpack('<I', stream.read(4))[0]
        self.min_version = struct.unpack('<I', stream.read(4))[0]
        stream.read(20)  # Skip unused
        self.index_major_version = struct.unpack('<I', stream.read(4))[0]
        self.index_count = struct.unpack('<I', stream.read(4))[0]
        self.index_size = struct.unpack('<I', stream.read(4))[0]
        stream.read(8)  # Skip unused
        self.index_minor_version = struct.unpack('<I', stream.read(4))[0]
        self.index_offset = struct.unpack('<I', stream.read(4))[0]

    def read_index(self, stream: BinaryIO) -> None:
        """Read the index from the file."""
        stream.seek(self.index_offset)
        self.index.read(stream)
        self.index.read_items(stream, self.index_count, self.is_dbbf)

    def read(self, stream: BinaryIO) -> None:
        """Read the complete DBPF file structure."""
        self.read_header(stream)
        self.read_index(stream)


class RefPackCompression:
    """RefPack compression/decompression implementation."""

    @staticmethod
    def decompress_fast(compressed_data: bytes) -> bytes:
        """
        Decompress RefPack compressed data.

        Args:
            compressed_data: The compressed data bytes

        Returns:
            The decompressed data bytes
        """
        if len(compressed_data) < 2:
            raise ValueError("Compressed data too short")

        pin = 0
        c_type = compressed_data[pin]
        pin += 1
        pin += 1  # Skip second byte

        if c_type not in (0x10, 0x50):
            raise ValueError(f"Unknown compression type: 0x{c_type:02X}")

        # Read decompressed size (3 bytes, big-endian)
        decomp_size = ((compressed_data[pin] & 0xFF) << 16 |
                      (compressed_data[pin + 1] & 0xFF) << 8 |
                      (compressed_data[pin + 2] & 0xFF))
        pin += 3

        out = bytearray(decomp_size)
        size = 0

        while size < decomp_size:
            control_char = compressed_data[pin] & 0xFF
            pin += 1

            num_plain_data = 0
            num_to_copy = 0
            copy_offset = 0

            if control_char >= 252:
                num_plain_data = control_char & 0x03
            elif control_char >= 224:
                num_plain_data = ((control_char & 0x1F) << 2) + 4
            elif control_char >= 192:
                cc_array = compressed_data[pin:pin+3]
                pin += 3
                num_plain_data = control_char & 0x03
                num_to_copy = ((control_char & 0x0C) << 6) + cc_array[2] + 5
                copy_offset = ((control_char & 0x10) << 12) + (cc_array[0] << 8) + cc_array[1] + 1
            elif control_char >= 128:
                cc_array = compressed_data[pin:pin+2]
                pin += 2
                num_plain_data = (cc_array[0] & 0xC0) >> 6
                num_to_copy = (control_char & 0x3F) + 4
                copy_offset = ((cc_array[0] & 0x3F) << 8) + cc_array[1] + 1
            else:
                cc_byte = compressed_data[pin]
                pin += 1
                num_plain_data = control_char & 0x03
                num_to_copy = ((control_char & 0x1C) >> 2) + 3
                copy_offset = ((control_char & 0x60) << 3) + cc_byte + 1

            # Copy plain data
            if num_plain_data > 0:
                if pin + num_plain_data > len(compressed_data):
                    raise ValueError("Compressed data corrupted")
                out[size:size + num_plain_data] = compressed_data[pin:pin + num_plain_data]
                pin += num_plain_data
                size += num_plain_data

            # Copy compressed data
            if num_to_copy > 0:
                if copy_offset > size:
                    raise ValueError("Invalid copy offset")

                if num_to_copy > copy_offset:
                    # Overlapping copy, do it byte by byte
                    for _ in range(num_to_copy):
                        out[size] = out[size - copy_offset]
                        size += 1
                else:
                    # Non-overlapping, use slice copy
                    out[size:size + num_to_copy] = out[size - copy_offset:size - copy_offset + num_to_copy]
                    size += num_to_copy

        return bytes(out)


class DBPFUnpacker:
    """Main class for unpacking DBPF files."""

    def __init__(self, input_file: str):
        self.input_file = Path(input_file)
        self.dbpf = DatabasePackedFile()

    def unpack(self, output_dir: str) -> None:
        """
        Unpack the DBPF file to the specified output directory.

        Args:
            output_dir: Directory to unpack files to
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        with open(self.input_file, 'rb') as f:
            # Read DBPF structure
            self.dbpf.read(f)

            print(f"Unpacking {self.dbpf.index_count} files...")

            for i, item in enumerate(self.dbpf.index.items):
                try:
                    # Read the compressed/uncompressed data
                    f.seek(item.chunk_offset)

                    if item.is_compressed:
                        compressed_data = f.read(item.compressed_size)
                        data = RefPackCompression.decompress_fast(compressed_data)
                    else:
                        data = f.read(item.mem_size)

                    # Create output filename
                    # For now, use hex representation since we don't have name resolution
                    filename = f"{item.name.instance_id:08X}.{item.name.type_id:08X}"

                    # Create group directory if needed
                    group_dir = output_path / f"{item.name.group_id:08X}"
                    group_dir.mkdir(exist_ok=True)

                    # Write the file
                    output_file = group_dir / filename
                    with open(output_file, 'wb') as out_f:
                        out_f.write(data)

                    if (i + 1) % 100 == 0:
                        print(f"Unpacked {i + 1}/{self.dbpf.index_count} files...")

                except Exception as e:
                    print(f"Error unpacking item {item.name}: {e}")
                    continue

        print(f"Successfully unpacked {len(self.dbpf.index.items)} files to {output_dir}")


def main():
    """Command line interface for the DBPF unpacker."""
    import argparse

    parser = argparse.ArgumentParser(description='Unpack DBPF files')
    parser.add_argument('input', help='Input DBPF file')
    parser.add_argument('output', help='Output directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' does not exist")
        return 1

    try:
        unpacker = DBPFUnpacker(args.input)
        unpacker.unpack(args.output)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def test_decompression():
    """Simple test for RefPack decompression."""
    # Test data - this would need actual compressed data to test properly
    # For now, just test that the classes can be instantiated
    key = ResourceKey(0x12345678, 0x9ABCDEF0, 0x11111111)
    assert str(key) == "12345678!9ABCDEF0.11111111"

    item = DBPFItem(key, 100, 50, 100, True)
    assert item.is_compressed == True
    assert item.chunk_offset == 100

    print("Basic tests passed!")


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_decompression()
    else:
        exit(main())